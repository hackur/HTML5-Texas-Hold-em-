import json
import os
import sys
import time

# Detect if we're running in a git repo
from os.path import exists, normpath
if exists(normpath('../pika')):
    sys.path.insert(0, '..')

import pika
import tornado.httpserver
import tornado.ioloop
import tornado.web

import database
from database import DatabaseConnection,User,Room, DealerInfo
from authenticate import *
from pika_channel import Channel,PersistentChannel
from config_controller import ConfigReader

class ListRoomHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		roomType = int(self.get_argument('type',0))
		print "ROOOM TYPE:",roomType
		print [ x for x in  DatabaseConnection()['room'].find()]
		rooms = Room.find_all(roomType=roomType)
		rooms = [(r.id,r.blind,r.player,r.max_player,r.min_stake,r.max_stake) for r in rooms]
		self.write(json.dumps({"rooms":rooms}))


class FastEnterRoomHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		roomType = self.get_argument('type',0)
		room = DatabaseConnection()[Room.table_name].find_one( \
				{"$where":'this.max_player > this.player','roomType':roomType})
		self.write(str(room['_id']))


class CreateRoomHandler(tornado.web.RequestHandler):
	def find_dealer(self):
		collection = DealerInfo.get_collection()
		dealer = collection.find(sort=[("rooms",1)],limit=1)[0]
		return dealer

	@tornado.web.asynchronous
	@authenticate
	def post(self):
		roomType	= self.get_argument("roomType",None)
		blind		= int(self.get_argument("blind"))
		max_stake	= blind * 200
		min_stake	= blind * 10
		max_player	= self.get_argument("max_player")
		room = ConfigReader.getObj("room")[roomType]

		if blind < room[0] or blind > room[1]:
			self.finish()
			return
		if (blind - room[0]) % room[2] != 0:
			self.finish()
			return

		dealer = self.find_dealer()
		self.channel	= Channel(
				self.application.channel,
				str(dealer['exchange']))

		arguments = self.session["user_id"]
		self.channel.add_ready_action(self.connected_call_back, arguments);
		self.channel.add_message_action(self.message_call_back, None)
		self.channel.connect()

	def message_call_back(self,argument):
		message = self.channel.get_messages()[0]
		print "ROOM ID ", message["room_id"]
		self.write(json.dumps(message))
		self.finish()

	def connected_call_back(self,userid):
		blind		= int(self.get_argument("blind"))
		roomType	= int(self.get_argument("roomType",None))
		max_stake	= blind * 200
		min_stake	= blind * 10
		max_player	= self.get_argument("max_player")

		msg = {"method":"create_room","blind":blind,"max_stake":max_stake,"min_stake":min_stake,
				"max_player":max_player,"user_id":str(userid),"roomType":roomType,
				"source":self.channel.routing_key}

		self.channel.publish_message("dealer",json.dumps(msg))



class EnterRoomHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		message			= None
		user			= self.user
		room_id			= self.get_argument('room_id')
		room			= Room.find(_id = room_id)
		if not room:
			print Room.find_all()
			print "not a valid room",room_id
			self.finish()
			return

		self.mongodb	= self.application.settings['_db']
		msg = self.mongodb.board.find_one({"user_id":self.session["user_id"], "room_id":room._id})
		if msg:
			msg["message-list"] = []
		else:
			msg = {"user_id":self.session["user_id"], "room_id":room.id, "message-list": []}

		print "Saving ",msg
		self.mongodb.board.remove({"user_id":self.session["user_id"]}) # guarantee only one exist
		self.mongodb.board.save(msg)

		queue				= str(user.username) + '_init'
		exchange			= str(room.exchange)

		self.session['exchange'] = exchange

		routing_key			= exchange + '_' + queue

		broadcast_queue		= str(user.username) + '_broadcast'
		public_key			= ('broadcast_%s_%s.testing')% (exchange, room._id)
		private_key			= ('direct.%s.%s.%s') % (exchange, room._id, user._id)
		binding_keys= [public_key, private_key]
		if user.isBot:
			bot_key			= ('direct.%s.%s.bot') % (exchange, room._id)
			binding_keys.append(bot_key)
			self.session['bot_key'] = bot_key


		message				= {	'method'		: 'enter',
								'user_id'		: user.id,
								#'source'		: routing_key,
								'room_id'		: room.id,
								'private_key'	: private_key}

		arguments			= {'routing_key': 'dealer', 'message': message}
		broadcast_channel	= PersistentChannel(
									self.application.channel,
									broadcast_queue,
									exchange,
									binding_keys,
									declare_queue_only=True,
									arguments = {"x-expires":int(15000)}
									)

		self.callBackCount = 0
		broadcast_channel.add_ready_action(self.initial_call_back,
				arguments)
		broadcast_channel.connect()

		self.channel = Channel(self.application.channel,exchange)

		self.channel.add_ready_action(self.initial_call_back, arguments);
		self.channel.connect()
		self.session['public_key']	= public_key
		self.session['private_key']	= private_key
		#self.session['messages']	= list()
		print "ENTER!"

	def initial_call_back(self, argument):
		print "ENTER CALL BACK",argument
		self.callBackCount += 1
		if self.callBackCount < 2:
			#We have to wait broadcast_channel created
			return

		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.channel.add_message_action(self.message_call_back, None)

		argument['message']['source'] = self.channel.routing_key
		print "PUBLISHED"
		self.channel.publish_message(argument['routing_key'], json.dumps(argument['message']))

	def message_call_back(self, argument):
		messages= self.channel.get_messages()[0]
		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.write(json.dumps(messages))
		self.channel.close();
		self.finish()

	def on_connection_close(self):
		self.channel.close()


class SitDownBoardHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		self.mongodb = self.application.settings['_db']
		user		= self.user
		seat		= self.get_argument('seat')
		stake		= self.get_argument('stake')

		if 'is_sit_down' in self.session and \
			self.session['is_sit_down'] == True and \
			self.session['seat'] == seat:
			self.write(json.dumps({'status':'success'}))
			self.finish()
		else:
			messages		= self.mongodb.board.find_one({"user_id":self.session["user_id"]})
			print messages
			room			= Room.find(_id=messages["room_id"])
			if room is None:
				self.finish(json.dumps({'status':'failed'}))
				return

			queue_name		= str(user.username) + '_sit'
			exchange_name   = self.session['exchange']

			user.room_id	= room.id
			#exchange_name	= str(user.room.exchange)
			#source_key		= "%s_%s" % (exchange_name, queue_name)

			message			=	{
									'method':'sit',
									'user_id':user.id,
									'seat':seat,
									#'source':source_key,
									'room_id':str(user.room_id),
									'private_key':self.session['private_key'] ,
									'stake':stake
								}

			arguments		= {'routing_key': 'dealer', 'message':message}
			self.channel	= Channel(self.application.channel, exchange_name)
			self.channel.add_ready_action(self.sit_call_back, arguments)
			self.channel.connect()

	def sit_call_back(self, argument):
		if self.request.connection.stream.closed():
			self.channel.close()
			return

		self.channel.add_message_action(self.message_call_back, None)
		argument['message']['source'] = self.channel.routing_key
		self.channel.publish_message(argument['routing_key'], json.dumps(argument['message']))

	def message_call_back(self, argument):
		messages= self.channel.get_messages()[0]
		if self.request.connection.stream.closed():
			self.channel.close()
			return
		if messages['status'] == 'success':
			board_message = self.mongodb.board.find_one({"user_id":self.session['user_id']});
			board_message['is_sit_down'] = True
			self.mongodb.board.save(board_message)

		self.write(json.dumps(messages))
		self.channel.close();
		self.finish()

	def on_connection_close(self):
		self.channel.close()

class BoardActionMessageHandler(tornado.web.RequestHandler):
	@authenticate
	def post(self):
		user					= self.user
		message					= json.loads(self.get_argument('message'))
		queue					= '%s_action_queue' % (str(user.username))
		exchange				= self.session['exchange']
		message['user_id']		= user.id
		message['method']		= 'action'
		message['private_key']	= self.session['private_key']
		message['room_id']		= user.room_id
		self.channel			= Channel(self.application.channel,exchange)
		self.channel.publish_message("dealer", json.dumps(message));




class BoardListenMessageSocketHandler(tornado.websocket.WebSocketHandler):
#TODO Merge these code with long-polling functions. avoid frequently db access
	@authenticate
	def open(self):
		print "WebSocket opened","x" * 20
		self.mongodb = self.application.settings['_db']
		user		= self.user
		queue		= str(user.username)  + '_broadcast'
		exchange	= self.session['exchange']
		messages = self.mongodb.board.find_one({"user_id":self.session["user_id"]})
		if len(messages["message-list"]) > 0:
			self.write_message(json.dumps(messages["message-list"]))

		self.mongoSession = messages
		self.messagesBuffer = messages["message-list"]
		binding_keys= (self.session['public_key'], self.session['private_key'])
		self.channel= PersistentChannel(
				self.application.channel,
				queue, exchange, binding_keys, self,arguments = {"x-expires":int(15000)})
		self.channel.add_message_action(self.message_call_back, None)
		self.channel.connect()

	def clean_matured_message(self, timestamp):
		self.messagesBuffer = filter(lambda x: int(x['timestamp']) > timestamp, self.messagesBuffer)
		#self.mongodb.board.update({"user_id": self.session["user_id"]}, board_messages)



	def on_connection_close(self):
		user_id			= self.session['user_id']
		mongoSession	= self.mongodb.board.find_one({"user_id": user_id})
		mongoSession["message-list"] = self.messagesBuffer
		self.mongodb.board.save(mongoSession)
		self.channel.close()

	def message_call_back(self, argument):
		new_messages	= self.channel.get_messages()

		self.messagesBuffer.extend(new_messages)
		self.write_message(json.dumps(new_messages))
		#board_messages	= self.mongodb.board.find_one({"user_id": user_id})
		#board_messages["message-list"].extend(new_messages)
		#self.mongodb.board.save(board_messages)
		#self.board_messages = board_messages["message-list"]
		#self.mongoSession = board_messages


	def on_message(self, message):
		print message
		msg = json.loads(message)
		if 'timestamp' in msg:
			timestamp	= int(msg['timestamp'])
			self.clean_matured_message(timestamp)
		elif 'action' in msg:
			message					= msg
			message['user_id']		= str(self.session['user_id'])
			message['method']		= 'action'
			message['private_key']	= self.session['private_key']
			message['room_id']		= str(self.mongoSession['room_id'])
			self.channel.publish_message("dealer", json.dumps(message));


	def on_close(self):
		self.channel.close();
		print "WebSocket closed"

	def allow_draft76(self):
		return True

###BoardListenMessageHandler shouldn't touch database at all. Even in authenticate
class BoardListenMessageHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		self.mongodb = self.application.settings['_db']
		user		= self.user
		timestamp	= int(self.get_argument('timestamp'))
		queue		= str(user.username)  + '_broadcast'
		exchange	= self.session['exchange']
		self.clean_matured_message(timestamp)
		messages = self.mongodb.board.find_one({"user_id":self.session["user_id"]})
		if len(messages["message-list"]) > 0:
			self.finish(json.dumps(messages["message-list"]))
			return

		binding_keys= [self.session['public_key'], self.session['private_key']]
		if self.user.isBot:
			binding_keys.append(self.session['bot_key'])


		self.channel= PersistentChannel(
				self.application.channel,
				queue, exchange, binding_keys, self,arguments = {"x-expires":int(15000)})
		self.channel.add_message_action(self.message_call_back, None)
		self.channel.connect()

	def clean_matured_message(self, timestamp):
		board_messages = self.mongodb.board.find_one({"user_id":self.session["user_id"]})
		print "========================[start]========================="
		print board_messages
		print "========================[ end ]========================="
		if board_messages is not None:
			board_messages["message-list"] = filter(lambda x: int(x['timestamp']) > timestamp, board_messages["message-list"])
			self.mongodb.board.update({"user_id": self.session["user_id"]}, board_messages)


	def on_connection_close(self):
		self.channel.close()

	def message_call_back(self, argument):
		new_messages	= self.channel.get_messages()
		print "------message receive start------"
		print new_messages
		print "------message receive end------"
		user_id			= self.session['user_id']
		board_messages	= self.mongodb.board.find_one({"user_id": user_id})
		board_messages["message-list"].extend(new_messages)
		self.mongodb.board.save(board_messages)
		self.board_messages = board_messages["message-list"]
		self.channel.close();

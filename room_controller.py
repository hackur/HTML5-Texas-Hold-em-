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
import functools
import database
from database import DatabaseConnection,User,Room, DealerInfo
from authenticate import *
from pika_channel import Channel,PersistentChannel
from config_controller import ConfigReader

class ListRoomHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		roomType = int(self.get_argument('type',0))
		rooms = Room.find_all(roomType=roomType)
		rooms = [(r.id,r.blind,r.player,r.max_player,r.min_stake,r.max_stake) for r in rooms]
		self.write(json.dumps({"rooms":rooms}))

	@authenticate
	def post(self):
		roomType = int(self.get_argument('type',0))
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
		msg = {"id":self.session.session_id, "room_id":room.id}

		BoardMessage.get_collection().remove({
						"id":self.session.session_id,
						},safe=True)

		# guarantee only one exist
		self.mongodb.board.update({"id":self.session.session_id},msg,upsert=True)

		exchange			= str(room.exchange)

		self.session['exchange'] = exchange

		public_key			= ('broadcast_%s_%s.testing')% (exchange, room._id)
		private_key			= ('direct.%s.%s.%s') % (exchange, room._id, user._id)
		binding_keys		= [public_key, private_key]
		if user.isBot:
			bot_key			= ('direct.%s.%s.bot') % (exchange, room._id)
			binding_keys.append(bot_key)
			self.session['bot_key'] = bot_key


		message				= {	'method'		: 'enter',
								'user_id'		: user.id,
								'room_id'		: room.id,
								'private_key'	: private_key}

		arguments			= {'routing_key': 'dealer', 'message': message}
		self.broadcast_channel = broadcast_channel	= PersistentChannel(
									self.application.channel,
									"%s%s" % (str(self.session.session_id),room.id[-10:]),
									exchange,
									binding_keys,
									declare_queue_only=True,
									arguments = {"x-expires":int(600000)}
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


	def purge_call_back(self,data):
		argument = self.argument
		self.channel.add_message_action(self.message_call_back, None)
		self.mongodb.board.update(
			{"id":self.session.session_id},
			{"$set": {'queue':self.broadcast_channel.queue_name}}
		)
		argument['message']['source'] = self.channel.routing_key
		self.channel.publish_message(	argument['routing_key'],
										json.dumps(argument['message']))

	def initial_call_back(self, argument):
		print "ENTER CALL BACK",argument
		self.callBackCount += 1
		if self.callBackCount < 2:
			#We have to wait broadcast_channel created
			return

		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.argument = argument
		self.application.channel.queue_purge(
			callback= self.purge_call_back,
			queue	= self.broadcast_channel.queue_name
		)



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

		if False and 'is_sit_down' in self.session and \
			self.session['is_sit_down'] == True and \
			self.session['seat'] == seat:
			self.write(json.dumps({'status':'success'}))
			self.finish()
		else:
			messages		= self.mongodb.board.find_one({"id":self.session.session_id})
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
			self.mongodb.board.update({"id":self.session.session_id},\
					{"$set" :{'is_sit_down':True}});

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
		exchange	= self.session['exchange']

		messages = [ msg.content for msg in BoardMessage.find_all(id=self.session.session_id)]
		if len(messages) > 0:
			self.write_message(json.dumps(messages["message-list"]))

		session = self.mongodb.board.find_one({"id":self.session.session_id})

		self.mongoSession = session
		self.messagesBuffer = messages
		binding_keys= (self.session['public_key'], self.session['private_key'])
		print "QUEUE NAME",session['queue']
		self.channel= PersistentChannel(
				self.application.channel,
				str(session['queue']), exchange, binding_keys, self,arguments = {"x-expires":int(600000)})
		self.channel.add_message_action(self.message_call_back, None)
		self.channel.connect()
		self.lastestTimestamp = 0
		self._isClosed = False

	def clean_matured_message(self, timestamp):
		self.lastestTimestamp = timestamp
		self.messagesBuffer = filter(lambda x: int(x['timestamp']) > timestamp, self.messagesBuffer)


	def isClosed(self):
		return self._isClosed

	def on_connection_close(self):
		self._isClosed = True
		DatabaseConnection()[BoardMessage.table_name].remove({
						"id":self.session.session_id,
						'timestamp':{'$lte':self.lastestTimestamp}
						})

		id			= self.session.session_id
		for content in self.messagesBuffer:
			BoardMessage.new(id,int(content['timestamp']),content)
		self.channel.close()

	def message_call_back(self, argument):
		new_messages	= self.channel.get_messages()
		print "=======================Mr.%s's Message============================" % (self.user.username)
		print "+++++++++++++++++++++++++++++++++++"
		print new_messages
		print "+++++++++++++++++++++++++++++++++++"

		self.messagesBuffer.extend(new_messages)
		self.write_message(json.dumps(new_messages))
		#board_messages	= self.mongodb.board.find_one({"user_id": user_id})
		#board_messages["message-list"].extend(new_messages)
		#self.mongodb.board.save(board_messages)
		#self.board_messages = board_messages["message-list"]
		#self.mongoSession = board_messages


	def on_message(self, message):
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

	def cancel_ok(self):
		pass

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
		exchange	= self.session['exchange']
		self.clean_matured_message(timestamp)
		messages = [ msg['content'] for msg in BoardMessage.get_collection().find(\
					{
					"id":self.session.session_id,
					"timestamp":{"$gt":timestamp}
					},
				sort=[("timestamp",1)]
					)]

		session = self.mongodb.board.find_one({"id":self.session.session_id})

		if len(messages) > 0:
			self.finish(json.dumps(messages))
			return
		else:
			print "Nothing in DB",timestamp,self.user.username


		binding_keys = [self.session['public_key'], self.session['private_key']]
		if self.user.isBot:
			binding_keys.append(self.session['bot_key'])


		self.channel= PersistentChannel(
				self.application.channel,
				str(session['queue']), exchange, binding_keys, self,arguments = {"x-expires":int(600000)})
		self.channel.add_message_action(self.message_call_back, None)
		self.channel.connect()
		self.closed = False

	def clean_matured_message(self, timestamp):
		BoardMessage.get_collection().remove({
						"id":self.session.session_id,
						'timestamp':{'$lte':timestamp}
						})

	def on_connection_close(self):
		self.channel.close()

	def isClosed(self):
		return self.request.connection.stream.closed()

	def cancel_ok(self):
		if self.request.connection.stream.closed():
			return

		if hasattr(self,"BoardMessage"):
			self.write(json.dumps(self.BoardMessage))
			pika.log.info( "Cancel OK %s",self.user.username)
			print json.dumps(self.BoardMessage)
		else:
			pika.log.info( "Cancel..... %s",self.user.username)
			self.write(json.dumps({}))
		self.finish()

	def message_call_back(self, argument):
		new_messages	= self.channel.get_messages()
		pika.log.info( "MR: %s %s",self.user.username,[ x for x in new_messages ])
		user_id			= self.user.id
		for content in new_messages:
			BoardMessage.new(self.session.session_id,int(content['timestamp']),content)

		if hasattr(self,"BoardMessage"):
			self.BoardMessage.extend(new_messages)
		else:
			self.BoardMessage = new_messages
		#if not self.closed:
		#	self.write(json.dumps(new_messages))
		#	self.finish();
		#	self.closed = True
		print "+++++++++++++++++++++++++++++"
		print self.BoardMessage
		print "+++++++++++++++++++++++++++++"
		self.channel.close();

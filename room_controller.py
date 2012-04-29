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

from sqlalchemy.orm import sessionmaker,relationship, backref
import database
from database import DatabaseConnection,User,Room, DealerInfo
from authenticate import *
from pika_channel import Channel,PersistentChannel
from sqlalchemy.sql import functions as SQLFunc

class ListRoomHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		roomType = self.get_argument('type',0)
		rooms = self.db_connection.query(Room).filter_by(roomType=roomType)
		rooms = [(r.id,r.blind,r.player,r.max_player,r.min_stake,r.max_stake) for r in rooms]
		self.write(json.dumps({"rooms":rooms}))


class FastEnterRoomHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		roomType = self.get_argument('type',0)
		rooms = self.db_connection.query(Room). \
				filter_by(roomType=roomType).filter(Room.player < Room.max_player).first()
		self.write(str(rooms.id))


class CreateRoomHandler(tornado.web.RequestHandler):
	def find_dealer(self):
		dealer = self.db_connection.query(SQLFunc.min(DealerInfo.rooms)).one()
		print dealer[0]
		dealer = self.db_connection.query(DealerInfo).filter_by(rooms=dealer[0]).one()
		print dealer
		return dealer

	@tornado.web.asynchronous
	@authenticate
	def post(self):
		dealer = self.find_dealer()
		self.channel	= Channel(
				self.application.channel,
				str(dealer.exchange))

		arguments = self.session["user"].id
		self.channel.add_ready_action(self.connected_call_back, arguments);
		self.channel.add_message_action(self.message_call_back, None)
		self.channel.connect()

	def message_call_back(self,argument):
		message = self.channel.get_messages()[0]
		print "ROOM ID ", message["room_id"]
		self.write(json.dumps(message))
		self.finish()

	def connected_call_back(self,userid):
		blind		= self.get_argument("blind")
		max_stake	= self.get_argument("max_stake")
		min_stake	= self.get_argument("min_stake")
		max_player	= self.get_argument("max_player")

		msg = {"method":"create_room","blind":blind,"max_stake":max_stake,"min_stake":min_stake,
				"max_player":max_player,"user_id":userid,
				"source":self.channel.routing_key}

		self.channel.publish_message("dealer",json.dumps(msg))



class EnterRoomHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		message			= None
		user			= self.session['user']
		room_id			= self.get_argument('room_id')
		room			= self.db_connection.query(Room).filter_by(id = room_id).one()
		self.mongodb	= self.application.settings['_db']
		self.mongodb.board.remove({"user_id":self.session["user_id"]})
		self.mongodb.board.save({"user_id":self.session["user_id"], "room_id":room.id, "message-list": []})
		self.db_connection.addItem(user)
		self.db_connection.commit_session()
		queue				= str(user.username) + '_init'
		exchange			= str(room.exchange)

		self.session['exchange'] = exchange

		routing_key			= exchange + '_' + queue

		broadcast_queue		= str(user.username) + '_broadcast'
		public_key			= ('broadcast_%s_%d.testing')% (exchange, room.id)
		private_key			= ('direct.%s.%d.%d') % (exchange, room.id, user.id)
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
									(private_key, public_key),
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
		self.session['user']		= user
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
		user		= self.session['user']
		seat		= self.get_argument('seat')
		stake		= self.get_argument('stake')

		if 'is_sit_down' in self.session and \
			self.session['is_sit_down'] == True and \
			self.session['seat'] == seat:
			self.write(json.dumps({'status':'success'}))
			self.finish()
		else:
			messages		= self.mongodb.board.find_one({"user_id":self.session["user_id"]})
			room			= self.db_connection.query(Room).filter_by(id = messages["room_id"]).first()
			if room is None:
				self.finish(json.dumps({'status':'failed'}))
				return

			queue_name		= str(user.username) + '_sit'
			exchange_name   = self.session['exchange']
			user.room		= room
			user.room_id	= room.id
			self.db_connection.addItem(user)
			self.db_connection.commit_session()
			#exchange_name	= str(user.room.exchange)
			#source_key		= "%s_%s" % (exchange_name, queue_name)

			message			=	{
									'method':'sit',
									'user_id':user.id,
									'seat':seat,
									#'source':source_key,
									'room_id':user.room.id,
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
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user					= self.session['user']
		message					= json.loads(self.get_argument('message'))
		queue					= '%s_action_queue' % (str(user.username))
		exchange				= str(user.room.exchange)
		message['user_id']		= user.id
		message['method']		= 'action'
		message['private_key']	= self.session['private_key']
		message['room_id']		= user.room.id
		arguments				= {'routing_key':'dealer', 'message':json.dumps(message)}
		self.channel			= Channel(self.application.channel,exchange)
		self.channel.publish_message("dealer", json.dumps(message));
		self.finish("{\"status\":\"success\"}");


###BoardListenMessageHandler shouldn't touch database at all. Even in authenticate
class BoardListenMessageHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		self.mongodb = self.application.settings['_db']
		user		= self.session['user']
		timestamp	= int(self.get_argument('timestamp'))
		queue		= str(user.username)  + '_broadcast'
		exchange	= self.session['exchange']
		self.clean_matured_message(timestamp)
		messages = self.mongodb.board.find_one({"user_id":self.session["user_id"]})
		if len(messages["message-list"]) > 0:
			self.finish(json.dumps(messages["message-list"]))
			return

		binding_keys= (self.session['public_key'], self.session['private_key'])
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

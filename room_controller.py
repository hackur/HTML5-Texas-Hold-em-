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
from database import DatabaseConnection,User,Room
from authenticate import *
from pika_channel import Channel



class EnterRoomHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		db_connection	= DatabaseConnection()
		message			= None

		# Only for using  apache ab to test
		#self.session['user'] = db_connection.query(User).filter_by(username = "ting").one()

		user			= self.session['user']
		room_id			= self.get_argument('room_id')
		room			= db_connection.query(Room).filter_by(id = room_id).one()

		user.room	= room
		user.room_id= room.id
		db_connection.addItem(user)
		db_connection.commit_session()
		queue				= str(user.username) + '_init'
		exchange			= str(room.exchange)

		self.session['exchange'] = exchange

		routing_key			= exchange + '_' + queue

		broadcast_queue		= str(user.username) + '_broadcast'
		public_key			= ('broadcast_%s_%d.testing')% (exchange, room.id)
		private_key			= ('direct.%s.%d.%d') % (exchange, room.id, user.id)
		message				= {	'method'		: 'enter',
								'user_id'		: user.id,
								'source'		: routing_key,
								'room_id'		: user.room.id,
								'private_key'	: private_key}

		arguments			= {'routing_key': 'dealer', 'message': json.dumps(message)}
		broadcast_channel	= Channel(	self.application.channel,
										broadcast_queue,
										exchange,
										(private_key, public_key),
										durable_queue = True,
										declare_queue_only=True,
										arguments = {"x-expires":int(15000)})

		self.callBackCount = 0
		broadcast_channel.add_ready_action(self.initial_call_back, arguments)
		broadcast_channel.connect()

		self.channel		= Channel(self.application.channel,queue, exchange, [routing_key])
		self.channel.add_ready_action(self.initial_call_back, arguments);
		self.channel.connect()
		self.session['public_key']	= public_key
		self.session['private_key']	= private_key
		self.session['user']		= user
		self.session['messages']	= list()
		print "ENTER!"

	def get(self):
		self.render("room-test-ajax.html")

	def initial_call_back(self, argument):
		print "ENTER CALL BACK",argument
		if self.callBackCount < 2:
			#We have to wait broadcast_channel created
			self.callBackCount += 1
			return

		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.channel.add_message_action(self.message_call_back, None)
		self.channel.publish_message(argument['routing_key'], argument['message'])

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
		user		= self.session['user']
		seat		= self.get_argument('seat')
		stake		= self.get_argument('stake')

		if 'is_sit_down' in self.session and \
			self.session['is_sit_down'] == True and \
			self.session['seat'] == seat:
			self.write(json.dumps({'status':'success'}))
			self.finish()
		else:
			queue_name		= str(user.username) + '_sit'
			exchange_name   = self.session['exchange']
			#exchange_name	= str(user.room.exchange)
			source_key		= "%s_%s" % (exchange_name, queue_name)

			message			= {'method':'sit', 'user_id':user.id,'seat':seat,
							'source':source_key, 'room_id':user.room.id,
							'private_key':self.session['private_key'] ,'stake':stake}

			arguments		= {'routing_key': 'dealer', 'message':json.dumps(message)}
			self.channel	= Channel(self.application.channel,queue_name, exchange_name, (source_key,))
			self.channel.add_ready_action(self.sit_call_back, arguments)
			self.channel.connect()

	def sit_call_back(self, argument):
		if self.request.connection.stream.closed():
			self.channel.close()
			return

		self.channel.add_message_action(self.message_call_back, None)
		self.channel.publish_message(argument['routing_key'], argument['message'])

	def message_call_back(self, argument):
		messages= self.channel.get_messages()[0]
		if self.request.connection.stream.closed():
			self.channel.close()
			return

		if messages['status'] == 'success':
			self.session['is_site_down']	= True

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
		self.channel			= Channel(self.application.channel,queue, exchange, [])
		self.channel.publish_message("dealer", json.dumps(message));
		self.finish("{\'status\':\'success\'}");


###BoardListenMessageHandler shouldn't touch database at all. Even in authenticate
class BoardListenMessageHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user		= self.session['user']
		timestamp	= int(self.get_argument('timestamp'))
		queue		= str(user.username)
		exchange	= self.session['exchange']
		self.clean_matured_message(timestamp)

		if len(self.session['messages']) > 0:
			messages = self.session['messages']
			self.finish(json.dumps(messages))
			return

		binding_keys= (self.session['public_key'], self.session['private_key'])
		self.channel= Channel(self.application.channel,queue, exchange, binding_keys, self)
		self.channel.add_message_action(self.message_call_back, None)
		self.channel.connect()

	def clean_matured_message(self, timestamp):
		self.session['messages'] = filter(lambda x: int(x['timestamp']) > timestamp,self.session['messages'])

	def on_connection_close(self):
		self.channel.close()

	def message_call_back(self, argument):
		messages= self.channel.get_messages()
		print "------message receive start------"
		print messages
		print "------message receive end------"
		self.session['messages'].extend(messages)
		self.channel.close();

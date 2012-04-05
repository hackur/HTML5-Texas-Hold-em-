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
from database import DatabaseConnection,User,Room,MessageQueue
from authenticate import *
from pika.adapters.tornado_connection import TornadoConnection
try:
    import cpickle as pickle
except:
    import pickle

import threading
threadLock = threading.Lock()
class Channel(object):
	tag = 0
	def __init__(self, channel, queue_name, exchange, binding_keys,
					request=None,
					durable_queue = False,
					declare_queue_only = False):
		# Construct a queue name we'll use for this instance only
		self.channel		= channel
		self.exchange		= exchange
		self.queue_name		= queue_name
		self.binding_keys	= binding_keys
		self.durable_queue	= durable_queue
		self.messages		= list()
		self.ready_actions	= list()
		self.message_actions= list()
		self.request		= request
		self.closing		= False
		self.declare_queue_only = declare_queue_only
		self.consumer_tag   = None
		print "exchange [%s] queue [%s]" %( self.exchange, queue_name)

	def connect(self):
		pika.log.info('Declaring Queue')
		if self.durable_queue:
			self.channel.queue_declare(
								queue		= self.queue_name,
								auto_delete	= not self.durable_queue,
								durable		= self.durable_queue,
								exclusive	= not self.durable_queue, # durable_queue may be shared
								callback	= self.on_queue_declared)
		else:
			self.channel.queue_declare(
								auto_delete	= not self.durable_queue,
								durable		= self.durable_queue,
								exclusive	= not self.durable_queue, # durable_queue may be shared
								callback	= self.on_queue_declared)

		pika.log.info('PikaClient: Exchange Declared, Declaring Queue Finish')

	def on_queue_declared(self, frame):
		pika.log.info('PikaClient: Queue Declared, Binding Queue')
		#if not self.queue_name:
		self.queue_name = frame.method.queue

		if len(self.binding_keys) > 0:
			for key in self.binding_keys:
				self.channel.queue_bind(exchange	= self.exchange,
										queue		= self.queue_name,
										routing_key	= key,
										callback	= self.on_queue_bound)

		else:
			for element in self.ready_actions:
				element['functor'](element['argument'])

	def on_queue_bound(self, frame):
		if self.declare_queue_only:
			return

		pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume')

		threadLock.acquire()
		self.consumer_tag	= "mtag%i" % Channel.tag ## Seems pika's tag name is not that reliable
		Channel.tag += 1
		threadLock.release()

		self.consumer_tag = self.channel.basic_consume(consumer_callback=self.on_room_message,
						queue=self.queue_name,
						no_ack=True,consumer_tag=self.consumer_tag)
		pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume Finish')

		for element in self.ready_actions:
			element['functor'](element['argument'])


	def on_room_message(self, channel, method, header, body):
		pika.log.info('PikaCient: Message receive, delivery tag #%i' % method.delivery_tag)
		self.messages.append(pickle.loads(body))
		for element in self.message_actions:
			element['functor'](element['argument'])



	def on_basic_cancel(self, frame):
		pika.log.info('PikaClient: Basic Cancel Ok')
		print "connection close---"
		if self.request and not self.request.request.connection.stream.closed():
			if len(self.request.session['messages']) > 0:
				self.request.write(json.dumps(self.request.session['messages']));
			try:
				self.request.finish()
			except:
				print "Client connection closed"

	def close(self):
		if not self.closing:
			#self.channel.close()
			self.closing = True
			self.channel.basic_cancel(self.consumer_tag,nowait=False, callback=self.on_basic_cancel)
			if not self.request: # We need to keep the actions for BoardListenMessageHandler
				self.message_actions = ()
				self.ready_actions = ()

	def publish_message(self, routing_key, message):
		self.channel.basic_publish(exchange	= self.exchange,
					routing_key	= routing_key,
					body		= message)

	def get_messages(self):
		output = self.messages
		self.messages = list()
		return output

	def add_ready_action(self, functor, argument):
		self.ready_actions.append({'functor':functor, 'argument':argument})

	def add_message_action(self, functor, argument):
		self.message_actions.append({'functor':functor, 'argument':argument})


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
		exchange			= str(user.room.exchange)
		routing_key			= exchange + '_' + queue

		broadcast_queue		= str(user.username) + '_broadcast'
		public_key			= ('broadcast_%s_%d.testing')% (exchange, room.id)
		private_key			= ('direct.%s.%d.%d') % (exchange, room.id, user.id)
		message				= {	'method'		: 'init',
								'user_id'		: user.id,
								'source'		: routing_key,
								'room_id'		: user.room.id,
								'private_key'	: private_key}

		arguments			= {'routing_key': 'dealer', 'message': pickle.dumps(message)}
		print broadcast_queue
		broadcast_channel	= Channel(	self.application.channel,
										broadcast_queue,
										exchange,
										(private_key, public_key),
										durable_queue = True,
										declare_queue_only=True)

		broadcast_channel.connect()

		self.channel		= Channel(self.application.channel,queue, exchange, [routing_key])
		self.channel.add_ready_action(self.initial_call_back, arguments);
		self.channel.connect()
		self.session['public_key']	= public_key
		self.session['private_key']	= private_key
		self.session['user']		= user
		self.session['messages']	= list()

	def get(self):
		self.render("room-test-ajax.html")

	def initial_call_back(self, argument):
		print "init call back"
		print argument['routing_key']
		print argument['message']
		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.channel.publish_message(argument['routing_key'], argument['message'])
		self.channel.add_message_action(self.message_call_back, None)

	def message_call_back(self, argument):
		messages= self.channel.get_messages()[0]
		print "=====message====="
		print messages
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

		#DEBUG
		#if'is_sit_down' in self.session and \
		if False and 'is_sit_down' in self.session and \
			self.session['is_sit_down'] == True and \
			self.session['seat'] == seat:
			self.write(json.dumps({'status':'success'}))
			self.finish()
		else:
			queue_name		= str(user.username) + '_sit'
			exchange_name	= str(user.room.exchange)
			source_key		= "%s_%s" % (exchange_name, queue_name)
			print '=============================keys==================================='
			print self.session['private_key']
			print self.session['public_key']
			message			= {'method':'sit', 'user_id':user.id,'seat':seat, 'source':source_key, 'room_id':user.room.id, 'private_key':self.session['private_key']}
			arguments		= {'routing_key': 'dealer', 'message':pickle.dumps(message)}
			self.channel	= Channel(self.application.channel,queue_name, exchange_name, [source_key])
			self.channel.add_ready_action(self.sit_call_back, arguments)
			self.channel.connect()

	def sit_call_back(self, argument):
		if self.request.connection.stream.closed():
			self.channel.close()
			return
		self.channel.publish_message(argument['routing_key'], argument['message'])
		self.channel.add_message_action(self.message_call_back, None)

	def message_call_back(self, argument):
		user	= self.session['user']
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
		arguments				= {'routing_key':'dealer', 'message':pickle.dumps(message)}
		self.channel			= Channel(self.application.channel,queue, exchange, [])
		self.channel.publish_message("dealer", pickler.dummps(message));
		self.finish("{\'status\':\'success\'}");


class BoardListenMessageHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user		= self.session['user']
		timestamp	= int(self.get_argument('timestamp'))
		queue		= str(user.username)
		exchange	= str(user.room.exchange)
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

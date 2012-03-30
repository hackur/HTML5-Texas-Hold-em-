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

class Channel(object):
	def __init__(self, queue_name, exchange, routing_key,  durable_queue = False,host='localhost'):
		# Construct a queue name we'll use for this instance only
		self.connected		= False
		self.connecting		= False
		self.connection		= None
		self.channel		= None
		self.host			= host
		self.exchange		= exchange
		self.queue_name		= queue_name
		self.routing_key	= routing_key
		self.durable_queue	= durable_queue
		self.messages		= list()
		self.ready_actions	= list()
		self.message_actions= list()
		self.consumer_tag	= None
		print "exchange [%s] queue [%s]" %( self.exchange, self.queue_name)

	def connect(self):
		pika.log.info('PikaClient: Connecting to RabbitMQ on localhost:5672')

		self.connecting = True
		credentials = pika.PlainCredentials('guest', 'guest')
		param = pika.ConnectionParameters(host=self.host,
						port=5672,
						virtual_host="/",
						credentials=credentials)
		self.connection = TornadoConnection(param, on_open_callback=self.on_connected)
		self.connection.add_on_close_callback(self.on_closed)

	def on_connected(self, connection):
		pika.log.info('PikaClient: Connected to RabbitMQ on %s:5672' % self.host)
		self.connected = True
		self.connection = connection
		self.connection.channel(self.on_channel_open)

	def on_channel_open(self, channel):
		pika.log.info('PikaClient: Channel Open, Declaring Exchange')
		self.channel = channel
		self.channel.exchange_declare(exchange=self.exchange,
				type="topic",
				auto_delete=True,
				durable=False,
				callback=self.on_exchange_declared)

	def on_exchange_declared(self, frame):
		pika.log.info('PikaClient: Exchange Declared, Declaring Queue')
		self.channel.queue_declare(	queue		= self.queue_name,
									auto_delete	= not self.durable_queue,
									durable		= self.durable_queue,
									exclusive	= True,
									callback	= self.on_queue_declared)

	def on_queue_declared(self, frame):
		pika.log.info('PikaClient: Queue Declared, Binding Queue')
		self.channel.queue_bind(exchange=self.exchange,
					queue=self.queue_name,
					routing_key=self.routing_key,
					callback=self.on_queue_bound)

	def on_queue_bound(self, frame):
		pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume')
		self.consumer_tag = self.channel.basic_consume(consumer_callback=self.on_room_message,
						queue=self.queue_name,
						no_ack=True)

		for element in self.ready_actions:
			element['functor'](element['argument'])


	def on_room_message(self, channel, method, header, body):
		pika.log.info('PikaCient: Message receive, delivery tag #%i' % method.delivery_tag)
		self.messages.append(pickle.loads(body))
		print pickle.loads(body)
		for element in self.message_actions:
			element['functor'](element['argument'])



	def on_basic_cancel(self, frame):
		pika.log.info('PikaClient: Basic Cancel Ok')
		self.channel.close()
#		self.connection.close()

	def on_closed(self, connection):
		print "connection cloase"
		pass

	def close(self):
		print "close"
		self.connection.close()

	def publish_message(self, routing_key, message):
		print "publish "
		print "exchange		=>" + self.exchange
		print "rountint key	=>" + routing_key
		print "body		=>" + message
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
		user			= self.session['user']
		room_id 		= self.get_argument('room_id')
		room			= db_connection.query(Room).filter_by(id = room_id).one()

		user.room	= room
		user.room_id= room.id
		db_connection.addItem(user)
		db_connection.commit_session()
		queue			= str(user.username) + '_init'
		exchange		= str(user.room.exchange)
		routing_key		= exchange + '_' + queue
		broadcast_queue	= str(user.username) + '_broadcast'
		broadcast_key	= ('broadcast_'+exchange+'_%d.*')% (room.id)
		message 		= {	'method'	: 'init',
							'user_id'	: user.id,
							'source'	: routing_key,
							'room_id'	: user.room.id,
							'listen_source': broadcast_key}

		arguments	= {'routing_key': 'dealer', 'message': pickle.dumps(message)}
		broadcast_channel = Channel(broadcast_queue, exchange, broadcast_key, True)
		broadcast_channel.connect()

		self.channel= Channel(queue, exchange, routing_key)
		self.channel.add_ready_action(self.initial_call_back, arguments);
		self.channel.connect()
		self.session['broadcast_key']	= broadcast_key
		self.session['user'] 			= user
		self.session['messages']		= list()

	def get(self):
		self.render("room-test-ajax.html")

	def initial_call_back(self, argument):
		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.channel.publish_message(argument['routing_key'], argument['message'])
		self.channel.add_message_action(self.message_call_back, None)

	def message_call_back(self, argument):
		messages= self.channel.get_messages()[0]
		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.channel.close();
		self.write(json.dumps(messages))
		self.finish()


class SitDownBoardHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		message		= None
		user		= self.session['user']
		seat		= self.get_argument('seat')
		if False and 'is_sit_down' in self.session and \
			self.session['is_sit_down'] == True and \
			self.session['seat'] == seat:
			self.write(json.dumps({'status':'success', 'message':messages}))
			self.finish()
		else:
			queue_name		= str(user.username)+'_sit'
			exchange_name	= str(user.room.exchange)
			source_key		= exchange_name + '_' + queue_name
			message 		= {'method':'sit', 'user_id':user.id,'seat':seat, 'source':source_key, 'room_id':user.room.id}
			arguments		= {'routing_key': 'dealer', 'message':pickle.dumps(message)}
			self.channel	= Channel(queue_name, exchange_name, source_key)
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
			print "SUCCESS!!!"
			self.session['messages'].append(messages)
			self.session['is_site_down']	= True
			#self.session['seat']		= message['seat']

		self.write(json.dumps(messages))
		self.finish()
		self.channel.close();

class BoardActionMessageHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		if self.session['user'] is not None:
			user		= self.session['user']
			action		= self.get_argument('action')
			amount		= self.get_argument('amount')
			timestamp	= self.get_argument('timestamp')
			queue		= str(user.username)+'_action'
			exchange	= str(user.room.exchange)
			source		= exchange + '_' + queue
			message		= {'method':'action', 'user_id':user.id, 'amount':amount, 'source':source}
			arguments	= {'routing_key':'dealer', 'message':pickle.dumps(message)}
			self.channel	= Channel(queue, exchange, source)
			self.channel.add_ready_action(self.action_call_back, arguments)
			self.channel.connect()
			self.clean_matured_message(timestamp)

	def clean_matured_message(self, timestamp):
		for message in self.session['messages'][:]:
			if message['timestamp'] < timestamp:
				self.session['messages'].remove(message)

	def action_call_back(self, argument):
		if self.request.connection.stream.closed():
			self.channel.close()
			return

		self.channel.publish_message(argument['routing_key'], argument['message'])
		self.channel.add_message_action(self.message_call_back, None)

	def message_call_back(self, argument):
		messages= self.channel.get_messages()
		user	= self.session['user']
		for message in messages:
			if message['user_id'] == user.id:
				self.session['messages'].append(message)

		if self.request.connection.stream.close():
			self.channel.close()
		self.write(json.dumps({'status':'success', 'message':self.session['messages']}))
		self.finish()
		self.channel.close()


class BoardListenMessageHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		if self.session['user'] is not None:
			user		= self.session['user']
			print  user
			timestamp	= self.get_argument('timestamp')
			queue		= str(user.username)
			exchange	= str(user.room.exchange)
			self.channel= Channel(queue, exchange, self.session['broadcast_key'])
			self.channel.add_message_action(self.message_call_back, None)
			self.channel.connect()
	 		self.clean_matured_message(timestamp)

	def clean_matured_message(self, timestamp):
		for message in self.session['messages'][:]:
	 		if message['timestamp'] < timestamp:
	 			self.session['messages'].remove(message)

	def message_call_back(self, argument):
		print "channel message"

		messages= self.channel.get_messages()
		user	= self.session['user']
		for message in messages:
			self.session['messages'].append(message)


		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.write(json.dumps(messages));#{'status':'success', 'message':self.session['messages']}))
		self.finish()
		self.channel.close();


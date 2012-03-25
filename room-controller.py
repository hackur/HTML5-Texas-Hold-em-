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
from session import *
from pika.adapters.tornado_connection import TornadoConnection

PORT = 8888
class Channel(object):
	def __init__(self, queue_name, exchange, routing_key):
		# Construct a queue name we'll use for this instance only
		self.connected		= False
		self.connecting		= False
		self.connection		= None
		self.channel		= None
		self.status		= False
		self.exchange		= exchange
		self.queue_name		= queue_name
		self.routing_key	= routing_key
		self.pending		= list()
		self.messages		= list()
		self.ready_actions	= list()
		self.message_actions	= list()
		print "exchange [%s] queue [%s]" %( self.exchange, self.queue_name)


	def connect(self, connection):
#		pika.log.info('PikaClient: Connected to RabbitMQ on localhost:5672')
		self.connected = True
		self.connection = connection
		self.connection.channel(self.on_channel_open)

	def on_channel_open(self, channel):
#		pika.log.info('PikaClient: Channel Open, Declaring Exchange')
		channel.saw = True
		self.channel = channel
		self.status  = True
		self.channel.exchange_declare(exchange=self.exchange,
				type="direct",
				auto_delete=True,
				durable=False,
				callback=self.on_exchange_declared)

	def on_exchange_declared(self, frame):
#		pika.log.info('PikaClient: Exchange Declared, Declaring Queue')
		self.channel.queue_declare(queue=self.queue_name,
			auto_delete=True,
			durable=False,
			exclusive=True,
			callback=self.on_queue_declared)

	def on_queue_declared(self, frame):
#		pika.log.info('PikaClient: Queue Declared, Binding Queue')
		self.channel.queue_bind(exchange=self.exchange,
					queue=self.queue_name,
					routing_key=self.routing_key,
					callback=self.on_queue_bound)

	def on_queue_bound(self, frame):
#		pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume')
		self.channel.basic_consume(consumer_callback=self.on_room_message,
						queue=self.queue_name,
						no_ack=True)

		for element in self.ready_actions:
			element['functor'](element['argument'])
		

	def on_room_message(self, channel, method, header, body):
#		pika.log.info('PikaCient: Message receive, delivery tag #%i' % method.delivery_tag)
		self.messages.append(body)
		for element in self.message_actions:
			element['functor'](element['argument'])



#	def on_basic_cancel(self, frame):
#		pika.log.info('PikaClient: Basic Cancel Ok')
#		self.channel.close()
	
	def on_closed(self, connection):
		pass
	
	def close(self):
		print "close [start]"
#		self.channel.basic_cancel()
		self.channel.close()
		print "close [end]"

	def publish_message(self, routing_key, message):
#		print "body		=>" + message
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


class SenderChannel(Channel):
	def on_queue_bound(self, frame):
#		pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume')
		for element in self.ready_actions:
			element['functor'](element['argument'])

class ReceiverChannel(Channel):
	def on_queue_bound(self, frame):
#		pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume')
		self.channel.basic_consume(consumer_callback=self.on_room_message,
						queue=self.queue_name,
						no_ack=True)
		for element in self.ready_actions:
			element['functor'](element['argument'])

prefix = 0;
class EnterRoomHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		global prefix
		prefix += 1
		message		= None
		dbConnection	= DatabaseConnection()
		dbConnection.start_session()
		room_id 	= self.get_argument('room_id')
		username	= self.get_argument('username')
		user		= dbConnection.query(User).filter_by(username = username).one()
		room		= dbConnection.query(Room).filter_by(id = room_id).one()
		message_queue	= dbConnection.query(MessageQueue).filter_by(room = room).filter_by(user = None).first()
	
		if True or message_queue is not None:
			user.queue	= message_queue
			user.room	= room
			user.room_id= room.id
			dbConnection.addItem(user)
			dbConnection.commit_session()
			queue_name	= str(username) + '_init_' + str(prefix)
			exchange_name	= str(user.room.exchange)
			routing_key	= exchange_name + '_' + queue_name 
			message 	= {'method':'init', 'user_id':user.id, 'source':routing_key}
			arguments	= {'routing_key': 'dealer',  'message':pickle.dumps(message)}
			self.channel	= ReceiverChannel(queue_name, exchange_name, routing_key)
			self.channel.add_ready_action(self.initial_call_back, arguments)
			self.channel.connect(self.application.connection)
			self.session['user'] = user
		else:
			dbConnection.rollback()
			message = json.dumps({'status':'failed'})
			self.write(message)
	def get(self):
		self.render("room-test-ajax.html")
	
	def initial_call_back(self, argument):
		print "init call back [start]"
		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.channel.publish_message(argument['routing_key'], argument['message'])
		self.channel.add_message_action(self.message_call_back, None)
		print "init call back [end]"

	def message_call_back(self, argument):
		print "message call back [start]"
		messages = self.channel.get_messages()
		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.channel.close();
		self.write(json.dumps({'status':'success', 'message':messages}))
		self.finish()
		print "message call back [end]"
		

class SitDownBoardHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):	
		if self.session['user'] is not None:
			user		= self.session['user']
			seat		= self.get_argument('seat')
			
			queue_name	= str(user.username)+'_sit'
			exchange_name	= str(user.room.exchange)
			source_key	= exchange_name + '_' + queue_name + '_sit'
			message 	= {'method':'sit', 'user_id':user.id,'seat':seat, 'source':source_key}
			arguments	= {'routing_key': 'dealer', 'message':pickle.dumps(message)}
			self.channel	= ReceiverChannel(queue_name, exchange_name, source_key)
			self.channel.add_ready_action(self.sit_call_back, arguments);
			self.channel.connect()
	
	def sit_call_back(self, argument):
		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.channel.publish_message(argument['routing_key'], argument['message'])
		self.channel.add_message_action(self.message_call_back, None)

	def message_call_back(self, argument):
		messages = self.channel.get_messages()
#		print 'message call back'
#		print messages
		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.channel.close();
		self.write(json.dumps({'status':'success', 'message':messages}))
		self.finish()

class BoardListenMessageHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		if self.session['user'] is not None:
			user		= self.session['user']
			queue_name	= str(user.username)
			exchange_name	= str(user.room.exchange)
			routing_key	= exchange_name + '_' + queue_name + '_listen' 
			self.channel	= ReceiverChannel(queue_name, exchange_name, routing_key)
			self.channel.add_message_action(self.message_call_back, None)
			self.channel.connect(self.application.connection)

	def message_call_back(self, argument):
#		print "time out call back"
		messages = self.channel.get_messages()
		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.write(json.dumps(messages))
		self.channel.close();
		self.finish()


if __name__ == '__main__':
	def on_connected(connection):
		print "connected"
	def connect(application):
		credentials = pika.PlainCredentials('guest', 'guest')
		param = pika.ConnectionParameters(host='localhost',
				port=5672,
				virtual_host="/",
				credentials=credentials)
		application.connection = TornadoConnection(param, on_open_callback=on_connected)

	settings = {
		"debug": True,
		'cookie_secret':"COOKIESECRET=ajbdfjbaodbfjhbadjhfbkajhwsbdofuqbeoufb",
		"static_path": os.path.join(os.path.dirname(__file__), "static"),
		'session_storage':"dir",
	}
	application = tornado.web.Application([
		(r"/sit-down", SitDownBoardHandler),
		(r"/listen-board-message", BoardListenMessageHandler),
		(r"/enter", EnterRoomHandler),
		(r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
		], **settings)


	# Start the HTTP Server
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(PORT)

	# Get a handle to the instance of IOLoop
	ioloop = tornado.ioloop.IOLoop.instance()

	# Add our Pika connect to the IOLoop with a deadline in 0.1 seconds
	#ioloop.add_timeout(time.time() + .1, application.room.connect)
	connect(application)
	# Start the IOLoop
	ioloop.start()

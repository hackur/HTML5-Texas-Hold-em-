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
from pika.adapters.tornado_connection import TornadoConnection
try:
    import cpickle as pickle
except:
    import pickle

PORT = 8888
class Channel(object):
	def __init__(self, queue_name, exchange, routing_key):
		# Construct a queue name we'll use for this instance only
		self.connected		= False
		self.connecting		= False
		self.connection		= None
		self.channel		= None
		self.host		= 'localhost'
		self.exchange		= exchange
		self.queue_name		= queue_name
		self.routing_key	= routing_key
		self.pending		= list()
		self.messages		= list()
		self.ready_actions	= list()
		self.message_actions	= list()
		self.consumer_tag	= None
		print "exchange [%s] queue [%s]" %( self.exchange, self.queue_name)

	def connect(self):
		if self.connecting:
			pika.log.info('PikaClient: Already connecting to RabbitMQ')
			return
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
				type="direct",
				auto_delete=True,
				durable=False,
				callback=self.on_exchange_declared)

	def on_exchange_declared(self, frame):
		pika.log.info('PikaClient: Exchange Declared, Declaring Queue')
		self.channel.queue_declare(queue=self.queue_name,
			auto_delete=True,
			durable=False,
			exclusive=True,
			callback=self.on_queue_declared)

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
		for element in self.message_actions:
			element['functor'](element['argument'])



	def on_basic_cancel(self, frame):
		pika.log.info('PikaClient: Basic Cancel Ok')
		self.channel.close()
#		self.connection.close()
	
	def on_closed(self, connection):
		print "connection cloase"
		pass
#		tornado.ioloop.IOLoop.instance().stop()
	
	def close(self):
		print "close"
	#	self.channel.close()
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


# class SenderChannel(Channel):
# 	def on_queue_bound(self, frame):
# 		pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume')
# 		for element in self.ready_actions:
# 			element['functor'](element['argument'])

# class ReceiverChannel(Channel):
# 	def on_queue_bound(self, frame):
# 		pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume')
# 		self.channel.basic_consume(consumer_callback=self.on_room_message,
# 						queue=self.queue_name,
# 						no_ack=True)
# 		for element in self.ready_actions:
# 			element['functor'](element['argument'])


class EnterRoomHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		message		= None
		dbConnection	= DatabaseConnection()
		dbConnection.start_session()
		room_id 	= self.get_argument('room_id')
		username	= self.get_argument('username')
		user		= dbConnection.query(User).filter_by(username = username).one()
		room		= dbConnection.query(Room).filter_by(id = room_id).one()
		message_queue	= dbConnection.query(MessageQueue).filter_by(room = room).filter_by(user = None).first()
	
		if message_queue is not None:
			user.queue	= message_queue
			user.room	= room
			user.room_id= room.id
			dbConnection.addItem(user)
			dbConnection.commit_session()
			queue_name	= str(username) + '_init'
			exchange_name	= str(user.room.exchange)
			routing_key	= exchange_name + '_' + queue_name 
			message 	= {'method':'init', 'user_id':user.id, 'source':routing_key}
			arguments	= {'routing_key': 'dealer',  'message':pickle.dumps(message)}
			self.channel	= Channel(queue_name, exchange_name, routing_key)
			self.channel.add_ready_action(self.initial_call_back, arguments);
			self.channel.connect()
			self.session['user'] 		= user
			self.session['messages']	= list()
		else:
			dbConnection.rollback()
			message = json.dumps({'status':'failed'})
			self.write(message)

	def get(self):
		self.render("room-test-ajax.html")
	
	def initial_call_back(self, argument):
		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.channel.publish_message(argument['routing_key'], argument['message'])
		self.channel.add_message_action(self.message_call_back, None)

	def message_call_back(self, argument):
		messages= self.channel.get_messages()
		if self.request.connection.stream.closed():
			self.channel.close();
			return
		self.channel.close();
		self.write(json.dumps(messages))
		self.finish()
		

class SitDownBoardHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		if self.session['user'] is not None:
			user		= self.session['user']
			seat		= self.get_argument('seat')
			if 'is_sit_down' in self.session and \
				self.session['is_sit_down'] == True and \
				self.session['seat'] == seat:
				self.write(json.dumps({'status':'success', 'message':messages}))
				self.finish()
			else:
				queue_name	= str(user.username)+'_sit'
				exchange_name	= str(user.room.exchange)
				source_key	= exchange_name + '_' + queue_name
				message 	= {'method':'sit', 'user_id':user.id,'seat':seat, 'source':source_key}
				arguments	= {'routing_key': 'dealer', 'message':pickle.dumps(message)}
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
		messages= self.channel.get_messages()
		if self.request.connection.stream.closed():
			self.channel.close()
			return

		for message in messages[:]:
			if message['user_id'] == user.id and message['status'] == 'success':
				self.session['messages'].append(message)
				self.session['is_site_down']	= True
				self.session['seat']		= message['seat']

		self.write(json.dumps(messages))
		self.finish()
		self.channel.close();

class BoardActionMessageHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		if self.session['user'] is not None:
			user		= self.session['user']
			action		= self.get_argument('action')
			amount		= self.get_argument('amount')
			offset		= self.get_argument('offset')
			queue		= str(user.username)+'_action'
			exchange	= str(user.room.exchange)
			source		= exchange + '_' + queue
			message		= {'method':'action', 'user_id':user.id, 'amount':amount, 'source':source}
			arguments	= {'routing_key':'dealer', 'message':pickle.dumps(message)}
			self.channel	= Channel(queue, exchange, source)
			self.channel.add_ready_action(self.action_call_back, arguments)
			self.channel.connect()
			self.clean_matured_message(offset)

	def clean_matured_message(self, offset):
		for message in self.session['messages'][:]:
			if message['index'] < offset:
				self.session['messages'].remove(message)

	def action_call_back(self, argument):
		if self.request.connection.stream.closed():
			self.channel.close()
			return

		self.channel.publish_message(argument['routing_key'], argument['message'])
		self.channel.add_message_action(self.message_call_back, None)
	
	def message_call_back(self, argument):
		messages= pickle.load(self.channel.get_messages())
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
	def post(self):
		if self.session['user'] is not None:
			user		= self.session['user']
			offset		= self.get_argument('offset')
			queue_name	= str(user.username)
			exchange_name	= str(user.room.exchange)
			routing_key	= exchange_name + '_' + queue_name + '_listen' 
			self.channel	= Channel(queue_name, exchange_name, routing_key)
			self.channel.add_message_action(self.message_call_back, None)
			self.channel.connect()
	 		self.clean_matured_message(offset)

	def clean_matured_message(self, offset):
		for message in self.session['messages'][:]:
	 		if message['index'] < offset:
	 			self.session['messages'].remove(message)

	def message_call_back(self, argument):
		messages= pickle.load(self.channel.get_messages())
		user	= self.session['user']
		for message in messages:
			if message['user_id'] == user.id:
				self.session['messages'].append(message)


		if self.request.connection.stream.closed():
			self.channel.close();
			return
		
		self.write(json.dumps({'status':'success', 'message':self.session['messages']}))
		self.finish()
		self.finish()
		self.channel.close();


if __name__ == '__main__':
	settings = {
		"debug": True,
		'cookie_secret':"COOKIESECRET=ajbdfjbaodbfjhbadjhfbkajhwsbdofuqbeoufb",
		"static_path": os.path.join(os.path.dirname(__file__), "static"),
		'session_storage':"dir",
		#"session_storage":"mongodb:///db"
	}
	application = tornado.web.Application([
		(r"/sit-down", SitDownBoardHandler),
		(r"/listen-board-message", BoardListenMessageHandler),
		(r"/enter", EnterRoomHandler),
		(r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
		], **settings)


	# Set our pika.log options
	pika.log.setup(color=True)

	# Start the HTTP Server
	pika.log.info("Starting Tornado HTTPServer on port %i" % PORT)
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(PORT)

	# Get a handle to the instance of IOLoop
	ioloop = tornado.ioloop.IOLoop.instance()

	# Add our Pika connect to the IOLoop with a deadline in 0.1 seconds
	#ioloop.add_timeout(time.time() + .1, application.room.connect)

	# Start the IOLoop
	ioloop.start()

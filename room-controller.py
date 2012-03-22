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
from session import session
from pika.adapters.tornado_connection import TornadoConnection

PORT = 8888


class Channel(object):

    def __init__(self,queue_name,exchange):
        # Construct a queue name we'll use for this instance only
        self.queue_name = queue_name
        self.connected	= False
        self.connecting	= False
        self.connection	= None
        self.channel	= None
	self.pending	= list()
	self.exchange	= exchange

    def connect(self):
        if self.connecting:
            pika.log.info('PikaClient: Already connecting to RabbitMQ')
            return
        pika.log.info('PikaClient: Connecting to RabbitMQ on localhost:5672')
        self.connecting = True

        credentials = pika.PlainCredentials('guest', 'guest')
        param = pika.ConnectionParameters(host='localhost',
                                          port=5672,
                                          virtual_host="/",
                                          credentials=credentials)
        self.connection = TornadoConnection(param, on_open_callback=self.on_connected)
        self.connection.add_on_close_callback(self.on_closed)

    def on_connected(self, connection):
        pika.log.info('PikaClient: Connected to RabbitMQ on localhost:5672')
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        pika.log.info('PikaClient: Channel Open, Declaring Exchange')
        self.channel = channel
        self.channel.exchange_declare(exchange=self.exchange,
                                      type="fanout",
                                      auto_delete=True,
                                      durable=False,
                                      callback=self.on_exchange_declared)

    def on_exchange_declared(self, frame):
        pika.log.info('PikaClient: Exchange Declared, Declaring Queue')
        self.channel.queue_declare(queue=self.queue_name,
                                   auto_delete=True,
                                   durable=False,
                                   exclusive=False,
                                   callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        pika.log.info('PikaClient: Queue Declared, Binding Queue')
        self.channel.queue_bind(exchange='tornado',
                                queue=self.queue_name,
                                routing_key='',
                                callback=self.on_queue_bound)

    def on_queue_bound(self, frame):
        pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume')
        self.channel.basic_consume(consumer_callback=self.on_room_message,
                                   queue=self.queue_name,
                                   no_ack=True)
	for message in self.pending:
		self.channel.basic_publish(exchange=self.exchange,
					routing_key='',
					body=message)
		

    def on_room_message(self, channel, method, header, body):
        pika.log.info('PikaCient: Message receive, delivery tag #%i' % \
                     method.delivery_tag)
        # Append it to our messages list
	self.handler.finish(body);

    def on_basic_cancel(self, frame):
        pika.log.info('PikaClient: Basic Cancel Ok')
        # If we don't have any more consumer processes running close
        self.connection.close()

    def on_closed(self, connection):
        # We've closed our pika connection so stop the demo
        tornado.ioloop.IOLoop.instance().stop()

    def publish_message(self, tornado_request):
	self.channel.basic_publish(exchange=self.exchange,
				routing_key='',
				body=tornado_request.get_argument('message'))
	

class MainHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@session
	def get(self):
		dbConnection	= DatabaseConnection()
		dbConnection.start_session()
		
		username	= self.get_argument("username")
		room_id		= self.get_argument("room_id")
		user		= dbConnection.query(User).filter_by(username = username).first()
		message_queue	= dbConnection.query(MessageQueue).filter_by(user = None).first()
		user.queue	= message_queue	
		dbConnection.addItem(user)
		dbConnection.commit_session()
		self.session['username']= username
		self.session['room_id']	= room_id
		self.finish(user.__repr__());

class EnterAjaxHandler(tornado.web.RequestHandler):
	@session
	def post(self):
		message		= None
		dbConnection	= DatabaseConnection()
		dbConnection.start_session()
		room_id 	= self.get_argument('room_id')
		username		= self.get_argument('username')#self.session["user"]
		user		= dbConnection.query(User).filter_by(username = username).one()
		room		= dbConnection.query(Room).filter_by(id = room_id).one()
		message_queue	= dbConnection.query(MessageQueue).filter_by(room = room).filter_by(user = None).first()
		if message_queue is not None:
			user.queue	= message_queue
			user.room	= room
			user.room_id	= room.id
			dbConnection.addItem(user)
			dbConnection.commit_session()
			message 	= json.dumps({'status':'success','room':user.room.exchange, 'queue': user.queue.queue_name})
			self.session['channel']	= Channel(user.room.exchange, user.queue.queue_name)
		else:
			dbConnection.rollback()
			message = json.dumps({'status':'failed'})
		self.write(message)
	
	def get(self):
		self.render("room-test-ajax.html");
		
class AjaxHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		self.application.room.publish_message(self)
		self.application.room.handler = self;


if __name__ == '__main__':
    settings = {
    	"debug": True,
	'cookie_secret':"COOKIESECRET=ajbdfjbaodbfjhbadjhfbkajhwsbdofuqbeoufb",
	"static_path": os.path.join(os.path.dirname(__file__), "static"),
	}
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/ajax", AjaxHandler),
	(r"/enter", EnterAjaxHandler),
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

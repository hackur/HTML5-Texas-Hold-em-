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
    def __init__(self,queue_name,exchange):
        # Construct a queue name we'll use for this instance only
        self.queue_name = queue_name
        self.connected	= False
        self.connecting	= False
        self.connection	= None
        self.channel	= None
        self.pending	= list()
        self.messages	= list()
        self.exchange	= exchange
        print "exchange [%s] queue [%s]" %( self.exchange, self.queue_name)

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
        self.channel.queue_bind(exchange=self.exchange,
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
                pika.log.info('PikaCient: Message receive, delivery tag #%i' % method.delivery_tag)
            # Append it to our messages list
        self.messages.append(body)
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.remove_timeout(self.handler.timeout_handle)
        self.handler.timeout_callback()

    def on_basic_cancel(self, frame):
        pika.log.info('PikaClient: Basic Cancel Ok')
        # If we don't have any more consumer processes running close
        self.connection.close()

    def on_closed(self, connection):
        # We've closed our pika connection so stop the demo
        tornado.ioloop.IOLoop.instance().stop()

    def publish_message(self, tornado_request):
        body = '%.8f: Request from %s [%s]' %  (tornado_request._start_time,
                tornado_request.remote_ip,
                tornado_request.headers.get("User-Agent"))
        body = body + tornado_request.arguments['message'][0]
        self.channel.basic_publish(exchange=self.exchange,
                routing_key='',
                body=body)
        def get_messages(self):
            output = self.messages
        self.messages = list()
        return output

class EnterAjaxHandler(tornado.web.RequestHandler):
    def post(self):
        message		= None
        dbConnection	= DatabaseConnection()
        dbConnection.start_session()
        room_id 	= self.get_argument('room_id')
        username	= self.get_argument('username')#self.session["user"]
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
            self.session['user']	= user
            self.session['channel']	= Channel(str(user.queue.queue_name), str(user.room.exchange))
            self.session['channel'].connect()
        else:
            dbConnection.rollback()
            message = json.dumps({'status':'failed'})
        self.write(message)

    def get(self):

        #print "GETSESSION"
        #getSession(self.request)
        #print "GETSESSION2"
        #self.request.session['hello'] = 'helloWorld'
        #print "GETSESSION3"

        self.render("room-test-ajax.html")
        #print "GETSESSION4"
        #saveSession(self.request)
        #print "GETSESSION5"

class BoardPostMessageHandler(tornado.web.RequestHandler):
    def post(self):
        if self.session['user'] is not None:
            self.session['channel'].publish_message(self.request)

class BoardListenMessageHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        if self.session['user'] is not None:
            channel		= self.session['channel']
            channel.handler = self
            if len(channel.get_messages()) ==0:
                ioloop = tornado.ioloop.IOLoop.instance()
                self.timeout_handle	= ioloop.add_timeout(time.time() + 4.0, self.timeout_callback)

    def timeout_callback(self):
        print "time out call back"
        messages = self.session['channel'].get_messages()
        if self.request.connection.stream.closed():
            return

        self.write(json.dumps(messages))
        self.finish()


if __name__ == '__main__':
    settings = {
            "debug": True,
            'cookie_secret':"COOKIESECRET=ajbdfjbaodbfjhbadjhfbkajhwsbdofuqbeoufb",
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            'session_storage':"file",
            }
    #initSession(settings)
    application = tornado.web.Application([
        (r"/post-board-message", BoardPostMessageHandler),
        (r"/listen-board-message", BoardListenMessageHandler),
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

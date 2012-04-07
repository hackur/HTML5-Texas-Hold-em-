import pika
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.process
from room_controller import *
from login_controller import *
from database import *
PORT = 8888

class IndexHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.render("test.html")

class IndexTestHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("room-test-ajax.html",username=self.get_argument('username'),sitno=self.get_argument('sitno'))

application = None
def on_channel_open(channel):
	pika.log.info('PikaClient: Channel Open')
	application.channel = channel

def on_connected(connection):
	print "pika connected"
	connection.channel(on_channel_open)

if __name__ == '__main__':
	settings = {
		"debug": True,
		'cookie_secret':"COOKIESECRET=ajbdfjbaodbfjhbadjhfbkajhwsbdofuqbeoufb",
		"static_path": os.path.join(os.path.dirname(__file__), "static"),
		'session_storage':"dir"
		#"session_storage":"mongodb:///db"
	}



	init_database()
	# Set our pika.log options
	pika.log.setup(color=True)
	pika.log.info("Starting Tornado HTTPServer on port %i" % PORT)
	application = tornado.web.Application([
		(r"/$", IndexHandler),
		(r"/test", IndexTestHandler),
		(r"/test.html", IndexHandler),
		(r"/sit-down", SitDownBoardHandler),
		(r"/listen-board-message", BoardListenMessageHandler),
		(r"/post-board-message", BoardActionMessageHandler),
		(r"/enter", EnterRoomHandler),
		(r"/guest-login", GuestLoginHandler),
		(r"/login", LoginHandler),
		(r"/(.*.html)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
		(r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
		], **settings)
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.bind(PORT)
	#http_server.start(8)
	http_server.start()

	pika.log.info('PikaClient: Connecting to RabbitMQ on localhost:5672')
	credentials = pika.PlainCredentials('guest', 'guest')
	param = pika.ConnectionParameters(host="localhost",
					port=5672,
					virtual_host="/",
					credentials=credentials)

	application.connection = TornadoConnection(param, on_open_callback=on_connected)

	#If we publishing message's speed is much faster than msg processed.
	# "TCP back pressure" will happen, set a huge multiplier to avoid that
	application.connection.set_backpressure_multiplier(100000)

	ioloop = tornado.ioloop.IOLoop.instance()

	ioloop.start()

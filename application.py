import pika
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.process
import tornado.websocket
from room_controller import *
from login_controller import *
from user_controller import *
from archive_controller import *
from chat_controller import *
from config_controller import *
from database import *
from thread_pool import thread_pool_init
from pika.adapters.tornado_connection import TornadoConnection
from thread_pool import thread_pool_init
PORT = 8888

class UIIndexHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("uitest.html")

class UIIndexTestHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		self.render("static/game/game.html")

class LoginPageHandler(tornado.web.RequestHandler):
	def get(self):
		if 'user_id' in self.session:
			user_id =  self.session['user_id']
			user = User.find(_id =user_id)
			if not user:
				del self.session['user_id']
			else:
				self.redirect("/static/user/user.html")
				return
		self.render("static/index/index.html")

class IndexPageHandler(tornado.web.RequestHandler):
	def get(self):
		self.redirect("/static/index/index.html")

class UserPageHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		self.render("static/user/user.html")

class IndexTestHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("room-test-ajax.html",username=self.get_argument('username'),sitno=self.get_argument('sitno'))


application = None
def on_channel_open(channel):
	pika.log.info('PikaClient: Channel Open')
	application.channel = channel
	channel.add_on_close_callback(on_close_callback)

def on_close_callback(msg1,msg2):
	print "CHANNEL CLOSED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print msg1,msg2
	exit(0)

def on_connected(connection):
	print "pika connected"
	connection.channel(on_channel_open)


import argparse
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Server...')
	parser.add_argument('--debug-mode','-D',default=1,type=int)
	parser.add_argument('--processes','-N',default=1,type=int)
	parser.add_argument('--port','-P',default=8888,type=int)
	args = parser.parse_args()
	PORT = args.port

	num_of_process =args.processes
	print args
	if args.debug_mode == 1:
		debug = True
		num_of_process = 1
	else:
		debug = False
	print debug,num_of_process

	settings = {
		"debug": debug,
		'cookie_secret':"COOKIESECRET=ajbdfjbaodbfjhbadjhfbkajhwsbdofuqbeoufb",
		"static_path2": os.path.join(os.path.dirname(__file__), "static"),
		"uploaded_image_path": os.path.join(os.path.dirname(__file__), "uploads"),
		"PokerUITest": os.path.join(os.path.dirname(__file__), "PokerUITest"),
		#'session_storage':"dir"
		"session_storage":"mongodb:///db",
		"session_age":None,
		"session_regeneration_interval":None
	}



	# Set our pika.log options
	pika.log.setup(color=False)
	pika.log.info("Starting Tornado HTTPServer on port %i" % PORT)
	application = tornado.web.Application([
		(r"/?$", IndexPageHandler),
		(r"/listen-board-message", BoardListenMessageHandler),
		(r"/post-board-message", BoardActionMessageHandler),
		(r"/static/game/game.html", UIIndexTestHandler),
		(r"/static/index/index.html", LoginPageHandler),
		(r"/static/user/user.html", UserPageHandler),
		(r"/sk",BoardListenMessageSocketHandler ),

		(r"/uitest.html", UIIndexHandler),
		(r"/sit-down", SitDownBoardHandler),
		(r"/enter", EnterRoomHandler),
		(r"/personal-archive",PersonalArchiveHandler),
		(r"/player-archive", PlayerArchiveHandler),
		(r"/head-portrait-upload",HeadPortraitHandler),
		(r"/list-email",EmailListHandler),
		(r"/send-email",EmailSendHandler),
		(r"/send-chat",SentChatMessageHandler),
		(r"/create_room",CreateRoomHandler),
		(r"/list_room",ListRoomHandler),
		(r"/fast_enter",FastEnterRoomHandler),
		(r"/buddy-info/(\w*)",BuddyInfoHandler),
		(r"/view-email",EmailViewHandler),
		(r"/config/(\w+)",ConfigHandler),


		(r"/delete-email",EmailDeleteHandler),
		(r"/userinfo", UserInfoHandler),
		(r"/guest-login", GuestLoginHandler),
		(r"/login", LoginHandler),
		(r"/logout", LogoutHandler),
        (r"/weibologin",SinaWeiboLogin),
		(r"/test", IndexTestHandler),
        (r"/weibologinCallback/?",SinaWeiboLoginBack),
		(r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path2'])),
		(r"/uploads/(.*)", tornado.web.StaticFileHandler, dict(path=settings['uploaded_image_path'])),
	#	(r"/(.*.html)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
		(r"/PokerUITest/(.*)", tornado.web.StaticFileHandler, dict(path=settings['PokerUITest'])),
		], **settings)
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.bind(PORT)
	#http_server.start(8)
	http_server.start(num_of_process)
	thread_pool_init()
	init_database()

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




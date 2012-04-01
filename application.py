import pika
import tornado.httpserver
import tornado.ioloop
import tornado.web
from room_controller import *
from login_controller import *
from database import *
PORT = 8888

def init_database():
	db_connection	= DatabaseConnection()
	db_connection.init("sqlite:///:memory:")
	db_connection.connect()
	db_connection.start_session()
	room		= Room(exchange="dealer_exchange_1")
	queue1		= MessageQueue(queue_name="queue_1",room = room)
	queue2		= MessageQueue(queue_name="queue_2",room = room)
	queue3		= MessageQueue(queue_name="queue_3",room = room)
	queue4		= MessageQueue(queue_name="queue_4",room = room)
	queue5		= MessageQueue(queue_name="queue_5",room = room)
	queue6		= MessageQueue(queue_name="queue_6",room = room)
	queue7		= MessageQueue(queue_name="queue_7",room = room)
	queue8		= MessageQueue(queue_name="queue_8",room = room)
	queue9		= MessageQueue(queue_name="queue_9",room = room)
	ting		= User(username="ting", password="123", stake = 100)
	mile		= User(username="mile", password="123", stake = 100)
	mamingcao	= User(username="mamingcao", password="123", stake = 100)
	huaqin		= User(username="huaqin", password="123", stake = 100)
	db_connection.addItem(ting)
	db_connection.addItem(mile)
	db_connection.addItem(huaqin)
	db_connection.addItem(mamingcao)
	db_connection.addItem(room)
	db_connection.addItem(queue1)
	db_connection.addItem(queue2)
	db_connection.addItem(queue3)
	db_connection.addItem(queue4)
	db_connection.addItem(queue5)
	db_connection.addItem(queue6)
	db_connection.addItem(queue7)
	ting.friends = [mile, mamingcao]
	mile.friends = [ting]
	db_connection.commit_session()
	print ting
	print mile
	print mamingcao
	print huaqin

class IndexHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.render("test.html")

class IndexTestHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("room-test-ajax.html",username=self.get_argument('username'),sitno=self.get_argument('sitno'))

if __name__ == '__main__':
	settings = {
		"debug": True,
		'cookie_secret':"COOKIESECRET=ajbdfjbaodbfjhbadjhfbkajhwsbdofuqbeoufb",
		"static_path": os.path.join(os.path.dirname(__file__), "static"),
		# 'session_storage':"dir"
		"session_storage":"mongodb:///db"
	}
	application = tornado.web.Application([
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


	init_database()
	# Set our pika.log options
	pika.log.setup(color=True)
	pika.log.info("Starting Tornado HTTPServer on port %i" % PORT)
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(PORT)
	ioloop = tornado.ioloop.IOLoop.instance()
	ioloop.start()

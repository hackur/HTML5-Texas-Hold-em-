import time
import pika
import sys
from optparse import OptionParser
import random
# import PokerController
import poker_controller
from game_room import GameRoom
from sqlalchemy.orm import sessionmaker,relationship, backref

import database
from database import DatabaseConnection,User,Room
import tornado.ioloop
from pika.adapters.tornado_connection import TornadoConnection

import json

class Dealer(object):
	#   users = []
	# waiting_list = {}
	suit = ["DIAMOND", "HEART", "SPADE", "CLUB"]
	face = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
#   room_list = []
	number_of_players = 9

	def __init__(self,queue,exchange,num_of_seats=9,blind=100,host='localhost',port=5672):
		self.queue      = queue
		self.exchange   = exchange
		self.host       = host
		self.port       = port
		self.room_list  = {}
		self.users      = []


	def init_database(self):
		database.init_database()
		self.db_connection = DatabaseConnection()

	def on_queue_bound(self, frame):
		self.channel.basic_consume(consumer_callback=self.on_message, queue=self.queue, no_ack=True)


	def on_queue_declared(self, frame):
		self.channel.queue_bind(exchange    = self.exchange,
				queue       = self.queue,
				routing_key = 'dealer',
				callback=self.on_queue_bound)


	def on_exchange_declared(self,frame):
		self.channel.queue_declare(queue    = self.queue,
				auto_delete = True,
				durable     = False,
				exclusive   = False,
				callback=self.on_queue_declared)


	def on_channel_open(self,channel):
		self.channel    = channel
		self.channel.exchange_declare(exchange = self.exchange,
				type        = 'topic',
				auto_delete = True,
				durable     = False,
				callback=self.on_exchange_declared
				)

	def on_connected(self,connection):
		connection.channel(self.on_channel_open)

	def start(self):
		credentials = pika.PlainCredentials('guest', 'guest')
		param = pika.ConnectionParameters(host="localhost",
						port=5672,
						virtual_host="/",
						credentials=credentials)

		self.connection = TornadoConnection(param, on_open_callback=self.on_connected)
		self.connection.set_backpressure_multiplier(100000)

	def cmd_action(self, args):
		#print "-------user trying to bet"
		print "action in dealer %d" % args["action"]
		current_room    = self.room_list[args["room_id"]]
		current_room.user_action(args)

	def cmd_chat(self, args):
		print args
		room	= self.room_list[args['room']]
		room.chat(args['user'], args['seat'], args['content'])

	def cmd_sit(self, args):
		print "sit received"
		self.db_connection.start_session()
		source          = args['source']
		private_key     = args['private_key']
		stake			= args['stake']
		user            = self.db_connection.query(User).filter_by(id=args['user_id']).first()
		current_room    = self.room_list[args["room_id"]]
		(status, msg)   = current_room.sit(user, int(args["seat"]), source, private_key,stake)

		if status:
			message = {"status": "success" }
		else:
			message = {"status": "failed", "msg": msg}
		self.channel.basic_publish( exchange    = self.exchange,
				routing_key = source,
				body        = json.dumps(message))

	def broadcast(self, routing_key, msg):
		self.channel.basic_publish(exchange     = self.exchange,
				routing_key = routing_key,
				body        = json.dumps(msg))

	def cmd_enter(self,args):
		if args['room_id'] not in self.room_list:
			self.cmd_create_room(args)
		print "Entered Room"

		current_room = self.room_list[args["room_id"]]
		#current_room.add_audit({'user':args["user_id"]})

		routing_key = args['source']
		message     = {'status':'success', "room":current_room.to_listener()}
		self.channel.basic_publish( exchange    = self.exchange,
				routing_key = routing_key,
				body        = json.dumps(message))

	def cmd_create_room(self, args):
		print "creating room"
		self.room_list[args['room_id']] = GameRoom(args["room_id"], args["user_id"], self)

#	def cmd_exit(self, args):
#		print "exiting room"
#		current_room = self.room_list[args["room_id"]]
#		current_room.user_action[]
#		self.room_list[args["room_id"]].exit_room(args["user_id"])
#		print room.status for room in room_list

	def on_message(self, channel, method, header, body):
		message = "message received, thanks!"
		obj = json.loads(body)
		method = getattr(self,"cmd_" + obj['method'])
		method(obj)

	def close(self):
		self.connection.close()


if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option('-q', '--queue', action='store', dest='queue_id', help='name of the queue to be assigned')
	parser.add_option('-e', '--exchange', action='store', dest='exchange_id', help='name of the exchange to be assigned')
	(options, args) = parser.parse_args(sys.argv)

	if not options.queue_id :
		options.queue_id = "dealer_queue_1"

	print "queue :" + options.queue_id

	if not options.exchange_id:
		options.exchange_id = "dealer_exchange_1"

	print "queue :" + options.exchange_id

	dealer = Dealer(queue = options.queue_id, exchange = options.exchange_id)
	dealer.init_database()


	dealer.start()
	ioloop = tornado.ioloop.IOLoop.instance()

	ioloop.start()
	# print dealer.seats


	# db = DatabaseConnection()

	# users = {}
	# for user in db.query(User):
	#   users[user.id] = user.username

	# print users
	# # print len(users)
	# players = []
	# for i in xrange(len(users)):
	#   players.append(PokerController.User())
	#   players[i].name = users[i+1]
	#   # print players[i].name
	#   i += 1

	# print len(players)
	# PokerController.PokerController.init(players)
	# PokerController.PokerController.getFlop()

	# #get the next one
	# PokerController.PokerController.getOne()

	# #get the next final card
	# PokerController.PokerController.getOne()
	# r = PokerController.PokerController.getWinner()
	# for user in r["winners"]:
	#   print "WINNER IS: " + user.name


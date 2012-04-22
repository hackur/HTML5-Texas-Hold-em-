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
from database import DatabaseConnection,User,Room, DealerInfo
import tornado.ioloop
from pika.adapters.tornado_connection import TornadoConnection

import json

class Dealer(object):
	def __init__(self,exchange,host,port):
		self.exchange   = exchange
		self.host       = host
		self.port       = port
		self.room_list  = {}


	def init_database(self):
		database.init_database()
		self.db_connection = DatabaseConnection()
		db_connection = self.db_connection
		db_connection.start_session()


		info = db_connection.query(DealerInfo).filter_by(exchange = self.exchange).first()

		if not info:
			info = DealerInfo()
		else:
			print "WARNING, dealer %s already in database" % self.exchange


		info.exchange = self.exchange
		info.rooms = 0
		db_connection.addItem(info)
		db_connection.commit_session()

	def on_queue_bound(self, frame):
		self.channel.basic_consume(
				consumer_callback=self.on_message,
				queue=self.queue_name, no_ack=True)


	def on_queue_declared(self, frame):
		self.queue_name = frame.method.queue
		self.channel.queue_bind(
				exchange    = self.exchange,
				queue       = self.queue_name,
				routing_key = 'dealer',
				callback=self.on_queue_bound)


	def on_exchange_declared(self,frame):
		self.channel.queue_declare(
				auto_delete = True,
				durable     = False,
				exclusive   = False,
				callback	=	self.on_queue_declared)


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
		param = pika.ConnectionParameters(self.host,
						port=self.port,
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
		routing_key = args['source']
		if args['room_id'] not in self.room_list:
			#self.cmd_create_room(args)
			message     = {'status':'failed'}
		else:
			print "Entered Room"
			current_room = self.room_list[args["room_id"]]

			message     = {'status':'success', "room":current_room.to_listener()}

		self.channel.basic_publish( exchange    = self.exchange,
				routing_key = routing_key,
				body        = json.dumps(message))


	def cmd_create_room(self, args):
		print "creating room"


		blind		= int(args["blind"])
		max_stake	= int(args["max_stake"])
		min_stake	= int(args["min_stake"])
		max_player	= int(args["max_player"])
		routing_key = args['source']

		db_connection = self.db_connection
		db_connection.start_session()

		newRoom = Room(self.exchange,blind,max_player,
				max_stake,
				min_stake)
		db_connection.addItem(newRoom)
		db_connection.commit_session()

		self.room_list[newRoom.id] = GameRoom(
				newRoom.id, args["user_id"], self,
				max_player,blind,min_stake,max_stake)
		print newRoom
		message = {"room_id":newRoom.id}

		self.channel.basic_publish( exchange    = self.exchange,
				routing_key = routing_key,
				body        = json.dumps(message))



	def on_message(self, channel, method, header, body):
		message = "message received, thanks!"
		obj = json.loads(body)
		method = getattr(self,"cmd_" + obj['method'])
		method(obj)

	def close(self):
		self.connection.close()


	def handle_init_file(self,fname):
		db_connection = self.db_connection
		db_connection.start_session()
		info = db_connection.query(Room).filter_by(exchange = self.exchange)
		for room in info:
			db_connection.delete(room)

		db_connection.commit_session()

		with open(fname) as f:
			for line in f:
				if line[0] == '#':
					continue

				(blind,max_stake,min_stake,max_player) = ( int(x) for x in line.strip().split(','))
				db_connection.start_session()

				newRoom = Room(self.exchange,blind,max_player,
						max_stake,
						min_stake)
				db_connection.addItem(newRoom)
				db_connection.commit_session()
				self.room_list[newRoom.id] = GameRoom(
						newRoom.id, 1, self,
						max_player,blind,min_stake,max_stake)
				print newRoom


import argparse
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Manage room creation')
	parser.add_argument('--exchange-name','-E',default='dealer_exchange_1',help="hello world")
	parser.add_argument('--rabbitmq-host','-H',default='localhost')
	parser.add_argument('--rabbitmq-port','-P',default='5672',type=int)
	parser.add_argument('--init-file','-F',default='init_rooms.txt')
	args = parser.parse_args()



	exchange_id = args.exchange_name
	rabbitmqServer = args.rabbitmq_host
	port = args.rabbitmq_port

	print exchange_id,rabbitmqServer,port


	dealer = Dealer(exchange = exchange_id,host=rabbitmqServer,port=port)
	dealer.init_database()


	dealer.start()
	dealer.handle_init_file(args.init_file)
	ioloop = tornado.ioloop.IOLoop.instance()

	ioloop.start()

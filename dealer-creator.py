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

class DealerManager(object):

	def __init__(self,queue,exchange,host='localhost',port=5672):
		self.queue      = queue
		self.exchange   = exchange
		self.host       = host
		self.port       = port


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
		self.channel.basic_qos(prefetch_count=1)


	def on_exchange_declared(self,frame):
		self.channel.queue_declare(queue    = self.queue,
				auto_delete = True,
				durable     = False,
				exclusive   = False,
				callback=self.on_queue_declared)


	def on_channel_open(self,channel):
		self.channel    = channel
		self.channel.exchange_declare(exchange = self.exchange,
				type        = 'direct',
				auto_delete = False,
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


	def on_message(self, channel, method, header, body):
		message = "message received, thanks!"
		obj = json.loads(body)
		print obj

	def close(self):
		self.connection.close()


if __name__ == "__main__":

	queue_id = "dealer_manager"

	print "queue :" + queue_id
	exchange_id = "dealer_manager_exchange"

	print "queue :" + exchange_id

	manager = DealerManager(queue = queue_id, exchange = exchange_id)
	manager.init_database()

	manager.start()
	ioloop = tornado.ioloop.IOLoop.instance()
	ioloop.start()

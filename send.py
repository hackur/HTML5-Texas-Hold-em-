#add num_of_checks in same_amount_on_table to prevent the situation that after check & fold, round finished without third player's choice.
import pika
import sys
import time

try:
    import cjson as json
except:
    import json

exchange	= 'dealer_exchange_1'
room_id		= 1

import time
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

class User(object):
	def __init__(self,user_id,seat):
		self.private_key			= ('direct.%s.%d.%d') % (exchange, room_id, user_id)
		self.user_id = user_id
		self.seat = seat


class Tester(object):
	def __init__(self,queue,exchange,host='localhost',port=5672):
		user1 = User(1,1)
		user2 = User(2,2)
		user3 = User(3,3)
		self.queue = queue
		self.exchange =exchange
		self.users = [user1,user2,user3]
		self.pKeys = {}
		self.boundQueue = 0

	def on_queue_bound(self, frame):
		self.boundQueue -= 1
		print "BOUND",self.boundQueue
		if self.boundQueue == 0:
			print "Start consume!!"
			self.channel.basic_consume(consumer_callback=self.on_message, queue=self.queue, no_ack=True)
		else:
			return

		for user in self.users:
			self.channel.basic_publish(exchange='dealer_exchange_1',
								routing_key="dealer",
								body=json.dumps({'method':'enter','source':'IAMGOD', "room_id":1, "user_id":user.user_id}))

		self.channel.basic_publish(exchange='dealer_exchange_1',
								routing_key="dealer",
								body=json.dumps({'method':'sit','source':'IAMGOD','user_id':1, "room_id":1, "seat":1,"private_key":self.users[0].private_key, "stake":200}))

		self.channel.basic_publish(exchange='dealer_exchange_1',
								routing_key="dealer",
								body=json.dumps({'method':'sit','source':'IAMGOD','user_id':2, "room_id":1, "seat":2,"private_key":self.users[1].private_key, "stake":150}))

		self.channel.basic_publish(exchange='dealer_exchange_1',
								routing_key="dealer",
								body=json.dumps({'method':'sit','source':'IAMGOD','user_id':3, "room_id":1, "seat":3,"private_key":self.users[2].private_key, "stake":500}))

	def on_queue_declared(self, frame):
		for user in self.users:
			self.boundQueue += 1
			self.channel.queue_bind(exchange='dealer_exchange_1',
						queue=self.queue,routing_key=user.private_key,
						callback=self.on_queue_bound
					)


		self.boundQueue += 1
		self.channel.queue_bind(exchange='dealer_exchange_1',
				queue=self.queue,routing_key="IAMGOD",
				callback=self.on_queue_bound
				)

		broadcast_key  = "broadcast_%s_%d.testing" % ( exchange, room_id)

		self.boundQueue += 1
		self.channel.queue_bind(exchange='dealer_exchange_1',
				queue=self.queue,routing_key=broadcast_key,
				callback=self.on_queue_bound
				)


	def on_exchange_declared(self,frame):
		self.channel.queue_declare(queue    = self.queue,
				auto_delete = True,
				durable     = True,
				exclusive   = False,
				callback=self.on_queue_declared,
				arguments = {"x-expires":15000})


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
	def on_message(self,ch, method, properties, body):
		print " [x] %r:%r" % (method.routing_key, json.loads(body),)
		msg = json.loads(body)
		if 'Cards in hand' in msg:
			self.pKeys[method.routing_key] = 1

		if len(self.pKeys) == 2:
			self.pKeys = {}
			#	print "all in!!!!!!!!!!!!!!!!!!!"
			self.channel.basic_publish(exchange='dealer_exchange_1',
						routing_key="dealer",
						body=json.dumps({'method':'action','action':2,'user_id':1,
							"room_id":1, "private_key":self.users[0].private_key, "amount":20}))

			self.channel.basic_publish(exchange='dealer_exchange_1',
						routing_key="dealer",
						body=json.dumps({'method':'action','action':2,'user_id':2,
							"room_id":1, "private_key":self.users[1].private_key, "amount":20}))

			self.channel.basic_publish(exchange='dealer_exchange_1',
						routing_key="dealer",
						body=json.dumps({'method':'action','action':3,'user_id':3,
							"room_id":1, "private_key":self.users[1].private_key, "amount":20}))

			self.channel.basic_publish(exchange='dealer_exchange_1',
						routing_key="dealer",
						body=json.dumps({'method':'action','action':3,'user_id':1,
							"room_id":1, "private_key":self.users[0].private_key, "amount":40}))

			self.channel.basic_publish(exchange='dealer_exchange_1',
						routing_key="dealer",
						body=json.dumps({'method':'action','action':2,'user_id':2,
							"room_id":1, "private_key":self.users[1].private_key, "amount":20}))

			self.channel.basic_publish(exchange='dealer_exchange_1',
						routing_key="dealer",
						body=json.dumps({'method':'action','action':2,'user_id':3,
							"room_id":1, "private_key":self.users[1].private_key, "amount":20}))

			self.channel.basic_publish(exchange='dealer_exchange_1',
						routing_key="dealer",
						body=json.dumps({'method':'action','action':3,'user_id':2,
							"room_id":1, "private_key":self.users[0].private_key, "amount":100}))

			self.channel.basic_publish(exchange='dealer_exchange_1',
						routing_key="dealer",
						body=json.dumps({'method':'action','action':3,'user_id':3,
							"room_id":1, "private_key":self.users[1].private_key, "amount":150}))

			self.channel.basic_publish(exchange='dealer_exchange_1',
						routing_key="dealer",
						body=json.dumps({'method':'action','action':2,'user_id':1,
							"room_id":1, "private_key":self.users[1].private_key, "amount":40}))

#			self.channel.basic_publish(exchange='dealer_exchange_1',
#						routing_key="dealer",
#						body=json.dumps({'method':'action','action':3,'user_id':2,
#							"room_id":1, "private_key":self.users[1].private_key, "amount":20}))

#			self.channel.basic_publish(exchange='dealer_exchange_1',
#						routing_key="dealer",
#						body=json.dumps({'method':'action','action':2,'user_id':3,
#							"room_id":1, "private_key":self.users[0].private_key, "amount":30}))


#			self.channel.basic_publish(exchange='dealer_exchange_1',
#						routing_key="dealer",
#						body=json.dumps({'method':'action','action':2,'user_id':1,
#							"room_id":1, "private_key":self.users[1].private_key}))


#			self.channel.basic_publish(exchange='dealer_exchange_1',
#						routing_key="dealer",
#						body=json.dumps({'method':'action','action':4,'user_id':2,
#							"room_id":1, "private_key":self.users[1].private_key, "amount":20}))

#			self.channel.basic_publish(exchange='dealer_exchange_1',
#						routing_key="dealer",
#						body=json.dumps({'method':'action','action':4,'user_id':3,
#							"room_id":1, "private_key":self.users[0].private_key, "amount":30}))


#			self.channel.basic_publish(exchange='dealer_exchange_1',
#						routing_key="dealer",
#						body=json.dumps({'method':'action','action':4,'user_id':1,
#							"room_id":1, "private_key":self.users[1].private_key}))
#			self.channel.basic_publish(exchange='dealer_exchange_1',
#							routing_key="dealer",
#							body=json.dumps({'method':'action','action':1,'user_id':2,
#							"room_id":1, "private_key":self.users[0].private_key}))
#
#
#			self.channel.basic_publish(exchange='dealer_exchange_1',
#							routing_key="dealer",
#						body=json.dumps({'method':'action','action':2,'user_id':1,
#						"room_id":1, "private_key":self.users[1].private_key}))

#			self.channel.basic_publish(exchange='dealer_exchange_1',
#						routing_key="dealer",
#						body=json.dumps({'method':'action','action':2,'user_id':1,
#							"room_id":1, "private_key":self.users[0].private_key}))
#
#			self.channel.basic_publish(exchange='dealer_exchange_1',
#						routing_key="dealer",
#						body=json.dumps({'method':'action','action':1,'user_id':1,
#						"room_id":1, "private_key":self.users[0].private_key}))


	#		self.channel.basic_publish(exchange='dealer_exchange_1',
	#					routing_key="dealer",
	#					body=json.dumps({'method':'action','action':1,'user_id':1,
	#						"room_id":1, "private_key":self.users[0].private_key}))

			#self.channel.basic_publish(exchange='dealer_exchange_1',
			#			routing_key="dealer",
			#			body=json.dumps({'method':'action','action':2,'user_id':1,
			#			"room_id":1, "private_key":1}))

if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option('-q', '--queue', action='store', dest='queue_id', help='name of the queue to be assigned')
	parser.add_option('-e', '--exchange', action='store', dest='exchange_id', help='name of the exchange to be assigned')
	(options, args) = parser.parse_args(sys.argv)

	if not options.queue_id :
		options.queue_id = "abc1212"

	print "queue :" + options.queue_id

	if not options.exchange_id:
		options.exchange_id = "dealer_exchange_1"

	print "queue :" + options.exchange_id

	dealer = Tester(queue = options.queue_id, exchange = options.exchange_id)


	dealer.start()
	ioloop = tornado.ioloop.IOLoop.instance()

	ioloop.start()




#if __name__ == "__main__":
#
#
#	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
#	channel = connection.channel()
#	channel.exchange_declare(exchange = exchange,
#				type			= 'topic',
#				auto_delete     = True,
#				durable         = False)
#
#	result = channel.queue_declare(exclusive=True)
#	queue_name = result.method.queue
#	broadcast_key  = "broadcast_%s_%d.testing" % ( exchange, room_id)
#
#	channel.queue_bind(exchange='dealer_exchange_1',
#				queue=queue_name,routing_key=broadcast_key)
#
#	channel.queue_bind(exchange='dealer_exchange_1',
#				queue=queue_name,routing_key="IAMGOD")
#
#
#	channel.basic_consume(callback,
#						queue=queue_name,
#						no_ack=True)
#
#	for user in users:
#		channel.queue_bind(exchange='dealer_exchange_1',
#					queue=queue_name,routing_key=user.private_key)
#
#	for user in users:
#		channel.basic_publish(exchange='dealer_exchange_1',
#							routing_key="dealer",
#							body=json.dumps({'method':'enter','source':'IAMGOD', "room_id":1, "user_id":user.user_id}))
#
#	for user in users:
#		channel.basic_publish(exchange='dealer_exchange_1',
#							routing_key="dealer",
#							body=json.dumps({'method':'sit','source':'IAMGOD','user_id':user.user_id, "room_id":1, "seat":user.seat,"private_key":user.private_key}))
#
#
#	channel.start_consuming()
#
#

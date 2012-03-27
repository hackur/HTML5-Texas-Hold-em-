import pika
import sys
from optparse import OptionParser
import random
# import PokerController
import poker_controller
from sqlalchemy.orm import sessionmaker,relationship, backref
from database import DatabaseConnection,User,Room,MessageQueue
try:
	import cpickle as pickle
except:
	import pickle


class Seat(object):
	(SEAT_EMPTY,SEAT_WAITING,SEAT_PLAYING) = (0,1,2)

	def __init__(self):
		self._user = None
		self._cards = None
		self._inAmount = 0
		self._status = Seat.SEAT_EMPTY
		pass


class Cards(object):
	def __init__(self):
		self._cards = []
		self._cardCount = 52
		for i in xrange(4):
			self._cards.append(range(1,14))

	def next(self):
		ram = random.randint(0,self._cardCount)
		for i in xrange(4):
			if ram >= len(self._cards[i]):
				ram -= len(self._cards[i])
			else:
				self._cardCount -= 1
				return self._cards[i][ram]




class Dealer(object):
	users = []
	def __init__(self,queue,exchange,num_of_seats=9,blind=100,host='localhost',port=5672):
		self.queue	= queue
		self.exchange	= exchange
		self.seats = {}
		self.host = host
		self.port = port
		for x in xrange(num_of_seats):
			self.seats[x] = Seat()


	def start(self):
		self.connection	= pika.BlockingConnection(
			pika.ConnectionParameters(host = self.host,
									port = self.port))
		self.channel	= self.connection.channel()
		self.channel.exchange_declare(exchange		= self.exchange,
				type		= 'direct',
				auto_delete	= True,
				durable		= False)
		self.channel.queue_declare(queue	= self.queue,
				auto_delete	= True,
				durable		= False,
				exclusive	= False)

		self.channel.queue_bind(exchange	= self.exchange,
				queue		= self.queue,
				routing_key	= 'dealer')
		self.channel.basic_consume(self.on_message, self.queue, no_ack=True)
		self.channel.start_consuming()

	def cmd_sit(self,args):
		print "sit received"
		""" User clicked Sit Down"""
		dbConnection	= DatabaseConnection()
		dbConnection.start_session()
		routing_key = args['source']
		user		= dbConnection.query(User).filter_by(id=args['user_id']).one()
		# print user
		user.combination = []
		user.handcards 	= []
		self.game_play(self.users, user)
		self.channel.basic_publish(exchange = self.exchange,
				routing_key=routing_key,
				body="Haven't implemented")

	def cmd_init(self,args):
		print "init received"
		""" RETURN THE ROOM's status """
		routing_key = args['source']
		self.channel.basic_publish(exchange = self.exchange,
				routing_key=routing_key,
				body="Haven't implemented")


	def on_message(self, channel, method, header, body):
		message = "message received, thanks!"
		obj = pickle.loads(body)
		print obj['method']
		method = getattr(self,"cmd_" + obj['method'])
		method(obj)

	def game_play(self, users, user):
		users.append(user)
		print "--------------------"+str(users)
		if 2 <= len(users) <= 4:
			game = poker_controller.PokerController(users)
			game.getFlop()
			for card in game.publicCard:
				print str(card.symbol)+"/"+str(card.value)+" ",
			for user in users:
				print str(user.username) + ": ",
				for cards in user.handcards:
					 print str(cards.symbol)+"/"+str(cards.value)+" ",
			# game.getOne()
			# game.getOne()
			# result = game.getWinner()
			# print result["winners"][0].username
			return
		else:
			return


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
	dealer.start()
	# print dealer.seats
	

	# db = DatabaseConnection()

	# users = {}
	# for user in db.query(User):
	# 	users[user.id] = user.username

	# print users
	# # print len(users)
	# players = []
	# for i in xrange(len(users)):
	# 	players.append(PokerController.User())
	# 	players[i].name = users[i+1]
	# 	# print players[i].name
	# 	i += 1

	# print len(players)
	# PokerController.PokerController.init(players)
	# PokerController.PokerController.getFlop()

	# #get the next one 
	# PokerController.PokerController.getOne()

	# #get the next final card
	# PokerController.PokerController.getOne()
	# r = PokerController.PokerController.getWinner()
	# for user in r["winners"]:
	# 	print "WINNER IS: " + user.name


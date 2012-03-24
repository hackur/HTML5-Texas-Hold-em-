import pika
import sys
from optparse import OptionParser
import random
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
    def __init__(self,queue,exchange,num_of_seats=9,blind=100,host='localhost'):
        self.queue	= queue
        self.exchange	= exchange
        self.seats = {}
        for x in xrange(num_of_seats):
            self.seats[x] = Seat()


    def start(self):
        self.connection	= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
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
        """ User clicked Sit Down"""
        dbConnection	= DatabaseConnection()
        dbConnection.start_session()
        routing_key = args['source']
        user		= dbConnection.query(User).filter_by(id=args['user_id']).one()
        print user
        self.channel.basic_publish(exchange = self.exchange,
                routing_key=routing_key,
                body="Haven't implemented")

    def cmd_init(self,args):
        """ RETURN THE ROOM's status """
        routing_key = args['source']
        self.channel.basic_publish(exchange = self.exchange,
                routing_key=routing_key,
                body="Haven't implemented")


    def on_message(self, channel, method, header, body):
        print "receive:" + body
        #do something
        message = "message received, thanks!"
        obj = pickle.loads(body)
        print obj['method']
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
    dealer.start()

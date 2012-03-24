import pika
import sys
from optparse import OptionParser



class Dealer(object):
	def __init__(self,queue,exchange):
		self.queue	= queue
		self.exchange	= exchange

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

	def on_message(self, channel, method, header, body):
		print "receive:" + body
		#do something
		message = "message received, thanks!"
		self.channel.basic_publish(exchange = self.exchange,
					routing_key='player*',
					body=message)
	def close(self):
		self.connection.close()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-q', '--queue', action='store', dest='queue_id', help='name of the queue to be assigned')
    parser.add_option('-e', '--exchange', action='store', dest='exchange_id', help='name of the exchange to be assigned')
    (options, args) = parser.parse_args(sys.argv)

    if(options.queue_id):
        print "queue :" + options.queue_id
    if(options.exchange_id):
        print "queue :" + options.exchange_id

    dealer = Dealer(queue = options.queue_id, exchange = options.exchange_id)
    print "YES!"
    dealer.start()
    print "YES!@"

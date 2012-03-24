import pika
import sys
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange	= 'dealer_exchange_1',
			type		= 'direct',
			auto_delete     = True,
			durable         = False)

channel.basic_publish(exchange='dealer_exchange_1',
	        routing_key='dealer',
		body='Hello World!')
connection.close()

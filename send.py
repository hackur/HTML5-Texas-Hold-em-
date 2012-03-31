import pika
import sys

try:
    import cpickle as pickle
except:
    import pickle

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange	= 'dealer_exchange_1',
                    			type		= 'direct',
                    			auto_delete     = True,
                    			durable         = False)
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='dealer_exchange_1',
            queue=queue_name,routing_key="IAMGOD")

def callback(ch, method, properties, body):
    print " [x] %r:%r" % (method.routing_key, body,)

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)
channel.basic_publish(exchange='dealer_exchange_1',
                      routing_key="dealer",
                      body=pickle.dumps({'method':'init','source':'IAMGOD', "room_id":"1", "user_id":"1"}))

channel.basic_publish(exchange='dealer_exchange_1',
                      routing_key="dealer",
                      body=pickle.dumps({'method':'sit','source':'IAMGOD','user_id':'1', "room_id":"1", "seat":1}))

channel.basic_publish(exchange='dealer_exchange_1',
                      routing_key="dealer",
                      body=pickle.dumps({'method':'sit','source':'IAMGOD','user_id':'1', "room_id":"1", "seat":2}))

channel.start_consuming()



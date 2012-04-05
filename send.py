import pika
import sys

try:
    import cpickle as pickle
except:
    import pickle

exchange	= 'dealer_exchange_1'
room_id		= 1

class User(object):
	def __init__(self,user_id,seat):
		self.private_key			= ('direct.%s.%d.%d') % (exchange, room_id, user_id)
		self.user_id = user_id
		self.seat = seat

pKeys = {}
def callback(ch, method, properties, body):
	print " [x] %r:%r" % (method.routing_key, pickle.loads(body),)
	msg = pickle.loads(body)
	if 'Cards in hand' in msg:
		pKeys[method.routing_key] = 1

	if len(pKeys) == 3:
		for user in users:
			print "all in!!!!!!!!!!!!!!!!!!!"
			channel.basic_publish(exchange='dealer_exchange_1',
						routing_key="dealer",
						body=pickle.dumps({'method':'action','action':1,'user_id':user.user_id,
						"room_id":1, "private_key":user.private_key}))





if __name__ == "__main__":
	user1 = User(1,1)
	user2 = User(2,2)
	user3 = User(3,3)
	users = [user1,user2,user3]


	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.exchange_declare(exchange = exchange,
				type			= 'topic',
				auto_delete     = True,
				durable         = False)

	result = channel.queue_declare(exclusive=True)
	queue_name = result.method.queue
	broadcast_key  = "broadcast_%s_%d.testing" % ( exchange, room_id)

	channel.queue_bind(exchange='dealer_exchange_1',
				queue=queue_name,routing_key=broadcast_key)

	channel.queue_bind(exchange='dealer_exchange_1',
				queue=queue_name,routing_key="IAMGOD")


	channel.basic_consume(callback,
						queue=queue_name,
						no_ack=True)

	for user in users:
		channel.queue_bind(exchange='dealer_exchange_1',
					queue=queue_name,routing_key=user.private_key)

	for user in users:
		channel.basic_publish(exchange='dealer_exchange_1',
							routing_key="dealer",
							body=pickle.dumps({'method':'init','source':'IAMGOD', "room_id":1, "user_id":user.user_id}))

	for user in users:
		channel.basic_publish(exchange='dealer_exchange_1',
							routing_key="dealer",
							body=pickle.dumps({'method':'sit','source':'IAMGOD','user_id':user.user_id, "room_id":1, "seat":user.seat,"private_key":user.private_key}))


	channel.start_consuming()



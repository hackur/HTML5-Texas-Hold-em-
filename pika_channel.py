import json
import pika
class Channel(object):
	tag = 0
	def __init__(self, channel, queue_name, exchange, binding_keys,
					request=None,
					durable_queue = False,
					declare_queue_only = False,
					arguments = {}):
		# Construct a queue name we'll use for this instance only
		self.channel		= channel
		self.exchange		= exchange
		self.queue_name		= queue_name
		self.binding_keys	= binding_keys
		self.durable_queue	= durable_queue
		self.messages		= list()
		self.ready_actions	= list()
		self.message_actions= list()
		self.request		= request
		self.closing		= False
		self.declare_queue_only = declare_queue_only
		self.consumer_tag   = None
		self.arguments 		= arguments

	def connect(self):
		pika.log.info('Declaring Queue')
		if self.durable_queue:
			self.channel.queue_declare(
								queue		= self.queue_name,
								auto_delete	= not self.durable_queue,
								durable		= self.durable_queue,
								exclusive	= not self.durable_queue, # durable_queue may be shared
								callback	= self.on_queue_declared,
								arguments 	= self.arguments)
		else:
			self.channel.queue_declare(
								auto_delete	= not self.durable_queue,
								durable		= self.durable_queue,
								exclusive	= not self.durable_queue, # durable_queue may be shared
								callback	= self.on_queue_declared)

		pika.log.info('PikaClient: Exchange Declared, Declaring Queue Finish')

	def on_queue_declared(self, frame):
		pika.log.info('PikaClient: Queue Declared, Binding Queue')
		#if not self.queue_name:
		self.queue_name = frame.method.queue

		print self.binding_keys
		if len(self.binding_keys) > 0:
			for key in self.binding_keys:
				print key
				self.channel.queue_bind(exchange	= self.exchange,
										queue		= self.queue_name,
										routing_key	= key,
										callback	= self.on_queue_bound)
		else:
			for element in self.ready_actions:
				element['functor'](element['argument'])

	def on_queue_bound(self, frame):
		if not self.declare_queue_only:
			pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume')
			print frame

			self.consumer_tag	= "mtag%i" % Channel.tag ## Seems pika's tag name is not that reliable
			Channel.tag += 1

			self.consumer_tag = self.channel.basic_consume(consumer_callback=self.on_room_message,
							queue=self.queue_name,
							no_ack=True,consumer_tag=self.consumer_tag)
			pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume Finish')

		for element in self.ready_actions:
			element['functor'](element['argument'])


	def on_room_message(self, channel, method, header, body):
		pika.log.info('PikaCient: Message receive, delivery tag #%i' % method.delivery_tag)
		self.messages.append(json.loads(body))
		print self.message_actions
		for element in self.message_actions:
			element['functor'](element['argument'])



	def on_basic_cancel(self, frame):
		pika.log.info('PikaClient: Basic Cancel Ok')
		print "connection close---"
		if self.request and not self.request.request.connection.stream.closed():
			if len(self.request.session['messages']) > 0:
				print self.request.session['messages']
				self.request.write(json.dumps(self.request.session['messages']));
			try:
				self.request.finish()
			except:
				print "Client connection closed"

	def close(self):
		if not self.closing:
			#self.channel.close()
			self.closing = True
			self.channel.basic_cancel(self.consumer_tag,nowait=False, callback=self.on_basic_cancel)
			if not self.request: # We need to keep the actions for BoardListenMessageHandler
				self.message_actions = ()
				self.ready_actions = ()

	def publish_message(self, routing_key, message):
		self.channel.basic_publish(exchange	= self.exchange,
					routing_key	= routing_key,
					body		= message)

	def get_messages(self):
		output = self.messages
		self.messages = list()
		return output

	def add_ready_action(self, functor, argument):
		self.ready_actions.append({'functor':functor, 'argument':argument})

	def add_message_action(self, functor, argument):
		self.message_actions.append({'functor':functor, 'argument':argument})

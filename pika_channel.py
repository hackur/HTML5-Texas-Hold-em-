import json
import pika

class Channel(object):
	tag = 0
	def __init__(self, channel, exchange):
		# Construct a queue name we'll use for this instance only
		self.channel		= channel
		self.exchange		= exchange
		self.messages		= list()
		self.ready_actions	= list()
		self.message_actions= list()
		self.closing		= False
		self.consumer_tag   = None

	def connect(self):
		pika.log.info('Declaring anonymous Queue')
		self.channel.queue_declare(
							auto_delete	= True,
							exclusive	= True,
							callback	= self.on_queue_declared)

		pika.log.info('PikaClient: Exchange Declared, Declaring Queue Finish')

	def on_queue_declared(self, frame):
		pika.log.info('PikaClient: Queue Declared, Binding Queue')
		#if not self.queue_name:
		self.queue_name = frame.method.queue
		#Just use queue name as KEY!
		self.routing_key = self.queue_name

		print self.queue_name
			#TODO May be we shouldn't bind queue everytime
			#for durable queue
		self.channel.queue_bind(exchange	= self.exchange,
								queue		= self.queue_name,
								routing_key	= self.routing_key,
								callback	= self.on_queue_bound)

	def on_queue_bound(self, frame):
		pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume')
		print self.queue_name
		self.consume()

		pika.log.info('PikaClient: Queue Bound, Issuing Basic Consume Finish')

		for element in self.ready_actions:
			element['functor'](element['argument'])

	def consume(self):
		print "CONSUME!!!!",self.queue_name
		self.consumer_tag	= "mtag%i" % Channel.tag ## Seems pika's tag name is not that reliable
		Channel.tag += 1

		self.consumer_tag = self.channel.basic_consume(
				consumer_callback=self.on_room_message,
						queue=self.queue_name,
						no_ack=True,consumer_tag=self.consumer_tag)
		print "END!!!!"


	def on_room_message(self, channel, method, header, body):
		pika.log.info('PikaCient: Message receive, delivery tag #%i' % method.delivery_tag)
		self.messages.append(json.loads(body))
		for element in self.message_actions:
			element['functor'](element['argument'])



	def on_basic_cancel(self, frame):
		pika.log.info('PikaClient: Basic Cancel Ok')
		print "connection close---"

	def close(self):
		if not self.closing:
			#self.channel.close()
			self.closing = True
			self.channel.basic_cancel(self.consumer_tag,nowait=False, callback=self.on_basic_cancel)
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

class PersistentChannel(Channel):
	def __init__(self,channel, queue_name, exchange, binding_keys,
					request = None,
					declare_queue_only = False,
					arguments = {}):


		Channel.__init__(self,channel, exchange)

		self.queue_name = queue_name
		self.binding_keys = binding_keys
		self.request = request
		self.declare_queue_only = declare_queue_only
		self.arguments = arguments

	def connect(self):
		pika.log.info('Declaring %s Queue' % self.queue_name)
		self.channel.queue_declare(
							queue		= self.queue_name,
							auto_delete	= False,
							exclusive	= False,
							callback	= self.on_queue_declared,
							arguments   = self.arguments)


	def close(self):
		if not self.closing:
			print "PersistentChannel Closing"
			#self.channel.close()
			self.closing = True
			self.channel.basic_cancel(self.consumer_tag,nowait=False, callback=self.on_basic_cancel)

	def on_queue_bound(self, frame):
		self.queue_bound += 1
		if self.queue_bound < len(self.binding_keys):
			print "QUEUE BOUND :",self.queue_bound
			return

		print "@@QUEUE BOUND :",self.queue_bound
		if self.declare_queue_only:
			for element in self.ready_actions:
				element['functor'](element['argument'])
			return

		super(PersistentChannel,self).on_queue_bound(frame)



	def on_queue_declared(self, frame):

		pika.log.info('PikaClient: Queue Declared, Binding Queue')
		self.queue_bound = 0
		for key in self.binding_keys:
			print "PersistentChannel binding ",key
			self.channel.queue_bind(exchange	= self.exchange,
								queue			= self.queue_name,
								#Just use queue name as KEY!
								routing_key	= key,
								callback	= self.on_queue_bound)


	def on_basic_cancel(self, frame):
		print "PersistentChannel Closed"
		if not self.request.request.connection.stream.closed():
			print "PersistentChannel Closed"
			if len(self.request.board_messages) > 0:
				self.request.write(json.dumps(self.request.board_messages));
			try:
				self.request.finish()
			except:
				print "Client connection closed"

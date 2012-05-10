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
		self.channel.queue_declare(
							auto_delete	= True,
							exclusive	= True,
							callback	= self.on_queue_declared)


	def on_queue_declared(self, frame):
		#if not self.queue_name:
		self.queue_name = frame.method.queue
		#Just use queue name as KEY!
		self.routing_key = self.queue_name

			#TODO May be we shouldn't bind queue everytime
			#for durable queue
		self.channel.queue_bind(exchange	= self.exchange,
								queue		= self.queue_name,
								routing_key	= self.routing_key,
								callback	= self.on_queue_bound)

	def on_queue_bound(self, frame):
		self.consume()


		for element in self.ready_actions:
			element['functor'](element['argument'])

	def consume(self):
		self.consumer_tag	= "mtag%i" % Channel.tag ## Seems pika's tag name is not that reliable
		Channel.tag += 1
		pika.log.info("Start consume %s %s",self.consumer_tag,self.queue_name)

		self.consumer_tag = self.channel.basic_consume(
				consumer_callback=self.on_room_message,
						queue=self.queue_name,
						no_ack=False,consumer_tag=self.consumer_tag)


	def on_room_message(self, channel, method, header, body):
		self.messages.append(json.loads(body))
		for element in self.message_actions:
			element['functor'](element['argument'])

		self.channel.basic_ack(method.delivery_tag)



	def on_basic_cancel(self, frame):
		pass

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
		self.closed = False

	def connect(self):
		pika.log.info('Declaring %s Queue' % self.queue_name)
		self.channel.queue_declare(
							queue		= self.queue_name,
							auto_delete	= False,
							exclusive	= True,
							callback	= self.on_queue_declared,
							arguments   = self.arguments)


	def close(self):
		pika.log.info( "Trying PersistentChannel Closing %s %s",self.queue_name,self.consumer_tag)
		if not self.closing:
			pika.log.info( "PersistentChannel Closing %s",self.queue_name)
			self.closing = True
			self.channel.basic_cancel(self.consumer_tag,nowait=False, callback=self.on_basic_cancel)
		else:
			pika.log.info("Closing already!")


	def on_queue_bound(self, frame):
		self.queue_bound += 1
		if self.queue_bound < len(self.binding_keys):
			return

		if self.declare_queue_only:
			for element in self.ready_actions:
				element['functor'](element['argument'])
			return

		super(PersistentChannel,self).on_queue_bound(frame)


	def on_room_message(self, channel, method, header, body):
		if not self.closed and not self.request.isClosed():
			super(PersistentChannel,self).on_room_message(channel,method,header,body)
		else:
			self.channel.basic_reject(method.delivery_tag)


	def on_queue_declared(self, frame):

		self.queue_bound = 0
		for key in self.binding_keys:
			key = str(key)
			self.channel.queue_bind(exchange	= self.exchange,
								queue			= self.queue_name,
								#Just use queue name as KEY!
								routing_key	= key,
								callback	= self.on_queue_bound)


	def on_basic_cancel(self, frame):
		pika.log.info( "PersistentChannel Closed %s %s",self.request.user.username,self.consumer_tag)
		self.request.cancel_ok()
		self.closed = True

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker,relationship, backref
from pprint import pprint
Base		= declarative_base()

class DatabaseConnection(object):
	__single	= None
	def __new__(clz):
		if not DatabaseConnection.__single:
			DatabaseConnection.__single = object.__new__(clz)
			
		return DatabaseConnection.__single

	def init(self, engine_string):
		self.engine	= create_engine(engine_string)
		Base.metadata.create_all(self.engine)
		self.connection	= self.engine.connect()
		self.Session	= sessionmaker(bind=self.engine)

	def connect(self):
		self.connection = self.engine.connect()
	
	def start_session(self):
		self.session	= self.Session()
	
	def commit_session(self):
		self.session.commit()

	def query(self, object):
		return self.session.query(object)
	def addItem(self, item):
		self.session.add(item)
	def rollback(self):
		self.session.rollback()

class Room(Base):
	__tablename__	= "room"
	id		= Column(Integer,primary_key=True, autoincrement=True)
	exchange	= Column(String(255))
	def __init__(self, exchange):
		self.exchange	= exchange
	def __repr__(self):
		return "<Room('%s','%s','%s','%s')>" % (self.id, self.exchange, self.queues,self.owner)

class MessageQueue(Base):
	__tablename__	= "message_queue"
	id		= Column(Integer, primary_key=True, autoincrement=True)
	room_id		= Column(Integer, ForeignKey('room.id'))
	queue_name	= Column(String(255))
	room 		= relationship("Room", backref=backref('queues', order_by=id))
	def __init__(self, queue_name, room_id = -1, room = None):
		self.queue_name	= queue_name
		self.room_id	= room_id
		self.room	= room
	def __repr__(self):
		return "<Queue('%s','%s', '%s')>" % (self.id, self.room_id, self.queue_name)

class User(Base):
	__tablename__	= "user"
	id		= Column(Integer, primary_key=True, autoincrement=True)
	username	= Column(String(255))
	password	= Column(String(255))
	queue_id	= Column(Integer, ForeignKey(MessageQueue.id))
	queue		= relationship(MessageQueue, uselist=False,backref=backref('user', uselist = False))
	room_id		= Column(Integer, ForeignKey("room.id"))
	room		= relationship("Room", backref=backref('owner', uselist=False))
	def __init__(self, username, password, queue_id = -1):
		self.username = username
		self.password = password
	def __repr__(self):
		return "<User('%s','%s', '%s', '%s')>" % (self.id, self.username, self.password, self.queue)


dbConnection	= DatabaseConnection()
dbConnection.init("sqlite:///:memory:")
dbConnection.connect()
dbConnection.start_session()
room		= Room(exchange="room_1")
queue1		= MessageQueue(queue_name="queue_1",room = room)
queue2		= MessageQueue(queue_name="queue_2",room = room)
queue3		= MessageQueue(queue_name="queue_3",room = room)
queue4		= MessageQueue(queue_name="queue_4",room = room)
queue5		= MessageQueue(queue_name="queue_5",room = room)
queue6		= MessageQueue(queue_name="queue_6",room = room)
queue7		= MessageQueue(queue_name="queue_7",room = room)
queue8		= MessageQueue(queue_name="queue_8",room = room)
queue9		= MessageQueue(queue_name="queue_9",room = room)
ting		= User(username="ting", password="123")
mile		= User(username="mile", password="123")
mamingcao	= User(username="mamingcao", password="123")
huaqin		= User(username="huaqin", password="123")
dbConnection.addItem(ting)
dbConnection.addItem(mile)
dbConnection.addItem(huaqin)
dbConnection.addItem(mamingcao)
dbConnection.addItem(room)
dbConnection.addItem(queue1)
dbConnection.addItem(queue2)
dbConnection.addItem(queue3)
dbConnection.addItem(queue4)
dbConnection.addItem(queue5)
dbConnection.addItem(queue6)
dbConnection.addItem(queue7)
dbConnection.commit_session()

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey,Text,Table
from sqlalchemy.orm import sessionmaker,relationship, backref
from pprint import pprint
Base	= declarative_base()
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

#imtermediate table
friendShip=Table("friendShip",Base.metadata,
	Column("leftFriendId",Integer,ForeignKey("user.id"),primary_key=True),
	Column("rightFriendId",Integer,ForeignKey("user.id"),primary_key=True)
)

class User(Base):
	__tablename__	= "user"
	id		= Column(Integer, primary_key=True, autoincrement=True)
	username	= Column(String(255))
	password	= Column(String(255))
	queue_id	= Column(Integer, ForeignKey(MessageQueue.id))
	queue		= relationship(MessageQueue, uselist=False,backref=backref('user', uselist = False))
	room_id		= Column(Integer, ForeignKey("room.id"))
	room		= relationship("Room", backref=backref('users'))
	family_id  	= Column(Integer,ForeignKey('family.id'))
	family		= relationship("Family",backref=backref('members',order_by=id))
	email		= Column(String(100))
	level		= Column(Integer)
	points		= Column(Integer) #need to be changed
	#type in family
	ftype_id	= Column(Integer,ForeignKey('familyType.id'))
	ftype		= relationship("FamilyType",backref=backref('members',order_by=id))
	friends		= relationship("User",
					secondary=friendShip,
					primaryjoin=id==friendShip.c.leftFriendId,
					secondaryjoin=id==friendShip.c.rightFriendId
					)
	stake		= Column(Integer)

	def __init__(self, username, password, stake, **kwargs):
		self.username = username
		self.password = password
		self.stake = stake

	def __repr__(self):
		return "<User('%s','%s', '%s', '%s', '%s')>" % (self.id, self.username, self.password, self.queue, self.friends)

class Family(Base):
	__tablename__="family"
	id	= Column(Integer, primary_key=True, autoincrement=True)
	name 	= Column(String(100))
	def __init__(self,name):
		self.name=name


class FamilyType(Base):
	__tablename__="familyType"
	id		= Column(Integer, primary_key=True, autoincrement=True)
	name		= Column(String(100))
	description	= Column(Text)

	def __init__(self,name):
		self.name=name


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
	def merge(self, object):
		self.session.merge(object)

def init_database():
	db_connection  = DatabaseConnection()
	db_connection.init("sqlite:///:memory:")
	db_connection.connect()
	db_connection.start_session()
	room        = Room(exchange="dealer_exchange_1")
	ting        = User(username="ting", password="123", stake = 100)
	mile        = User(username="mile", password="123", stake = 500)
	mamingcao   = User(username="mamingcao", password="123", stake = 200)
	huaqin      = User(username="huaqin", password="123", stake = 500)
	db_connection.addItem(ting)
	db_connection.addItem(mile)
	db_connection.addItem(huaqin)
	db_connection.addItem(mamingcao)
	db_connection.addItem(room)
	# ting.friends = [mile, mamingcao]
	# mile.friends = [ting]
	db_connection.commit_session()


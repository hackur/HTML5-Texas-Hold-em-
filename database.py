import hashlib
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey,Text,Table,DateTime
from sqlalchemy.orm import sessionmaker,relationship, backref
from datetime import datetime
from pprint import pprint
Base	= declarative_base()
class Room(Base):
	__tablename__	= "room"
	id		= Column(Integer,primary_key=True, autoincrement=True)
	exchange	= Column(String(255))
	blind		= Column(Integer)
	player		= Column(Integer)
	max_stake	= Column(Integer)
	min_stake	= Column(Integer)
	max_player	= Column(Integer)
	roomType	= Column(Integer)

	def __init__(self, exchange, blind=10,max_player=9,
			max_stake=1000,min_stake=100):
		self.exchange	= exchange
		self.max_stake = max_stake
		self.min_stake = min_stake
		self.blind = blind
		self.max_player = max_player
		self.player =	0
		self.roomType = 0

	def __repr__(self):
		return "<Room('%s','%s')>" % (self.id, self.exchange)

class HeadPortrait(Base):
	__tablename__	= "head_portrait"
	id		= Column(Integer, primary_key = True, autoincrement = True)
	path	= Column(String(255))
	url		= Column(String(255))



class DealerInfo(Base):
	__tablename__	= "dealer_info"
	id			= Column(Integer,primary_key=True, autoincrement=True)
	exchange	= Column(String(255))
	rooms		= Column(Integer)

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
	room_id		= Column(Integer, ForeignKey("room.id"))
	room		= relationship("Room", backref=backref('users'))
	family_id   = Column(Integer,ForeignKey('family.id'))
	family		= relationship("Family",backref=backref('members',order_by=id))
	#email		= Column(String(100))
	level		= Column(Integer)
	total_games = Column(Integer)
	won_games	= Column(Integer)
	max_reward	= Column(Integer)
	last_login	= Column(DateTime)
	signature	= Column(String(255))
	asset		= Column(Integer) #need to be changed
	head_portrait_id	= Column(Integer, ForeignKey("head_portrait.id"))
	head_portrait		= relationship("HeadPortrait", backref=backref('user'), uselist=False)
	#type in family
	family_position_id	= Column(Integer,ForeignKey('familyPosition.id'))
	family_position		= relationship("FamilyPosition", backref=backref('members',order_by=id))
	friends		= relationship("User",
					secondary=friendShip,
					primaryjoin=id==friendShip.c.leftFriendId,
					secondaryjoin=id==friendShip.c.rightFriendId
					)
	stake		= Column(Integer)

	def __init__(self, username, password, stake, total_games=0, won_games = 0, level = 0, asset = 0, max_reward = 0, **kwargs):
		self.username		= username
		self.password		= password
		self.stake			= stake
		self.total_games	= total_games
		self.won_games		= won_games
		self.level			= level
		self.asset			= asset
		self.max_reward		= max_reward

	def __repr__(self):
		return "<User('%s','%s', '%s', '%s')>" % (self.id, self.username, self.password, self.friends)

class Family(Base):
	__tablename__="family"
	id	= Column(Integer, primary_key=True, autoincrement=True)
	name	= Column(String(100))
	def __init__(self,name):
		self.name=name

class FamilyPosition(Base):
	__tablename__="familyPosition"
	id			= Column(Integer, primary_key=True, autoincrement=True)
	name		= Column(String(100))
	description	= Column(Text)

	def __init__(self,name):
		self.name=name

class Email(Base):
	__tablename__	= "email"
	id			= Column(Integer, primary_key=True, autoincrement=True)
	from_user_id= Column(Integer, ForeignKey("user.id"))
	from_user	= relationship("User", primaryjoin=(from_user_id==User.id), backref=backref('out_mails'))
	to_user_id	= Column(Integer, ForeignKey("user.id"))
	to_user		= relationship("User", primaryjoin=(to_user_id==User.id), backref=backref('in_mails'))
	content		= Column(Text)
	sent_date	= Column(DateTime)
	status		= Column(Integer)
	reply_to_id	= Column(Integer, ForeignKey("email.id"))
	reply_to	= relationship("Email", backref=backref('follow_emails', remote_side=[id], uselist=False))

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

	def delete(self, item):
		self.session.delete(item)

	def rollback(self):
		self.session.rollback()

	def merge(self, object):
		self.session.merge(object)

	def close(self):
		self.session.expunge_all()
		self.session.close()

def init_database():
	db_connection  = DatabaseConnection()
	db_connection.init("sqlite:///db.sqlite")
	db_connection.connect()

if __name__ == "__main__":
	import os
	os.remove("db.sqlite")
	db_connection  = DatabaseConnection()
	db_connection.init("sqlite:///db.sqlite")
	db_connection.connect()
	db_connection.start_session()
	#room        = Room(exchange="dealer_exchange_1",blind=10,max_player=9)
	ting        = User(username="ting", password=hashlib.md5("123").hexdigest(), stake = 200)
	mile        = User(username="mile", password=hashlib.md5("123").hexdigest(), stake = 100)
	mamingcao   = User(username="mamingcao", password=hashlib.md5("123").hexdigest(), stake = 200)
	huaqin      = User(username="huaqin", password=hashlib.md5("123").hexdigest(), stake = 500)
	ting.level	= 12
	ting.total_games= 100
	ting.won_games	= 40
	ting.max_reward	= 998
	ting.last_login	= datetime.strptime("2012-04-13 12:02:20", "%Y-%m-%d %H:%M:%S")
	ting.signature	= "software engineer"
	ting.asset		= 12000
	db_connection.addItem(ting)
	db_connection.addItem(mile)
	db_connection.addItem(huaqin)
	db_connection.addItem(mamingcao)
	#db_connection.addItem(room)

	email	= Email()
	email.from_user = ting
	email.to_user	= mile
	email.content	= "aassdd"
	email.send_date	= datetime.now()
	email.reply_to_id	= None
	db_connection.addItem(email)

	ting.friends = [mile, mamingcao]
	mile.friends = [ting]
	db_connection.addItem(ting)
	db_connection.addItem(mile)

	db_connection.commit_session()

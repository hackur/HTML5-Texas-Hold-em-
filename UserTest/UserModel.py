from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey,Text,Table
from sqlalchemy.orm import sessionmaker,relationship, backref
from pprint import pprint
Base		= declarative_base()

engine=create_engine("sqlite:///:memory:")



#==========================================================
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
	id			= Column(Integer, primary_key=True, autoincrement=True)
	room_id		= Column(Integer, ForeignKey('room.id'))
	queue_name	= Column(String(255))
	room 		= relationship("Room", backref=backref('queues', order_by=id))
	def __init__(self, queue_name, room_id = -1, room = None):
		self.queue_name	= queue_name
		self.room_id	= room_id
		self.room	= room
	def __repr__(self):
		return "<Queue('%s','%s', '%s')>" % (self.id, self.room_id, self.queue_name)
#=======================================================

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
	room		= relationship("Room", backref=backref('owner', uselist=False))
	family_id  	= Column(Integer,ForeignKey('family.id'))
	family      = relationship("Family",backref=backref('members',order_by=id))
	email		= Column(String(100))
	level		= Column(Integer)
	points		= Column(Integer) #need to be changed
	#type in family
	ftype_id	= Column(Integer,ForeignKey('familyType.id'))
	ftype 		= relationship("FamilyType",backref=backref('members',order_by=id))
	right_friends 	= relationship("User",
					secondary=friendShip,
					primaryjoin=id==friendShip.c.leftFriendId,
					secondaryjoin=id==friendShip.c.rightFriendId,
					backref="left_friends"
				)
	#a great deal info of the user
	#.....

	def __init__(self, username, password,**kwargs):
		self.username = username
		self.password = password

	def __repr__(self):
		return "<User('%s','%s', '%s', '%s')>" % (self.id, self.username, self.password, self.queue)

class Family(Base):
	__tablename__="family"
	id		= Column(Integer, primary_key=True, autoincrement=True)
	name 	= Column(String(100))
	#ranking1
	#ranking2

	def __init__(self,name):
		self.name=name


class FamilyType(Base):
	__tablename__="familyType"
	id			= Column(Integer, primary_key=True, autoincrement=True)
	name		= Column(String(100))
	description = Column(Text)

	def __init__(self,name):
		self.name=name

Base.metadata.create_all(engine)
connection=engine.connect()
Session=sessionmaker(bind=engine)
session=Session()


'''
u1=User(username="starry",password="123")
u2=User(username="night",password="123")
f1=Family(name="Super Sucker")
u1.family=f1
u2.family=f1

print "Super Sucker members--->",f1.members

ft1=FamilyType(name="king")
ft2=FamilyType(name="antizen")
u1.familyType=ft1
u2.familyType=ft2
print u1.familyType.name

u1.right_friends=[u2]
print u2.left_friends
session.add(u1)
session.add(u2)

session.commit()
print session.query(User)
'''
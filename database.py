import hashlib
from datetime import datetime
from pprint import pprint
import pymongo
import time
from  bson.objectid import ObjectId

class MongoDocument(object):
	def __init__(self,document=None):
		if document:
			self.__dict__['_entry'] = document
			return
		else:
			self.__dict__['_entry'] = {}


	def __getattr__(self, key):
		if key in self._entry:
			return self._entry[key]
		return None

	def __setattr__(self,key,value):
		self._entry[key] = value
		if not "_id" in self._entry:
			return

		db = DatabaseConnection()
		db[self.table()].update({"_id" : self._entry['_id']},\
				{"$set": {key:value}})

	def update_attr(self,key,valueDelta):
		db = DatabaseConnection()
		db[self.table()].update({"_id" : self._entry['_id']},\
				{"$inc": {key:valueDelta}})
		self._entry[key] += valueDelta

	def table(self):
		return type(self).table_name



	def insert(self):
		collection =  DatabaseConnection()[self.table()]
		try:
			_id = collection.insert(self._entry,safe=True)
		except Exception as e:
			print e
			return False

		self._entry["_id"] = _id;
		return True

	def remove(self):
		db = DatabaseConnection()
		db[self.table()].remove({"_id":self._id},atomic=True)


	@property
	def id(self):
		if "_id" in self._entry:
			return str(self._entry["_id"])
		else:
			return None

	@classmethod
	def get_collection(Table):
		return DatabaseConnection()[Table.table_name]

	@classmethod
	def find(Table,**kwarg):
		if "_id" in kwarg and type(kwarg['_id']) != ObjectId:
			kwarg['_id'] = ObjectId(kwarg['_id'])


		db = DatabaseConnection()[Table.table_name]
		document = db.find_one(kwarg)
		if document:
			obj = Table(document)
			return obj
		return None

	@classmethod
	def find_all(Table,**kwarg):
		if "_id" in kwarg and type(kwarg['_id']) != ObjectId:
			kwarg['_id'] = ObjectId(kwarg['_id'])

		db = DatabaseConnection()[Table.table_name]
		documents = db.find(kwarg)
		return [ Table(document) for document in documents]

class Room(MongoDocument):
	table_name	= "room"

	@staticmethod
	def new(exchange, blind = 10, max_player = 9, max_stake = 1000, min_stake = 100,roomType=0):
		room = Room()
		room.exchange	= exchange
		room.max_stake	= max_stake
		room.min_stake	= min_stake
		room.blind		= blind
		room.max_player = max_player
		room.player		= 0
		room.roomType	= roomType
		if room.insert():
			return room
		return None

	def __repr__(self):
		return "<Room('%s','%s','%s')>" % (self._id, self.exchange,self.roomType)




class DealerInfo(MongoDocument):
	table_name	= "dealer_info"

	@staticmethod
	def new(exchange):
		dealer = DealerInfo()
		dealer.exchange = exchange
		if dealer.insert():
			return dealer
		return None

	@staticmethod
	def create_index(db):
		db[User.table_name].ensure_index('rooms')


#imtermediate table


class User(MongoDocument):
	table_name	= "user"
	(USER_TYPE_NORMAL,USER_TYPE_SINA_WEIBO) = (0,1)

	@staticmethod
	def new(username, password="",asset = 3000, accountType=0,accountID=0):
		user = User()
		user.username			= username
		user.password			= password
		user.room_id			= None
		user.level				= 0
		user.total_games		= 0
		user.won_games			= 0
		user.max_reward			= 0
		user.last_login			= None
		user.signature			= None
		user.asset				= asset
		user.accountType		= accountType
		user.accountID			= accountID
		user.screen_name		= username
		user.gender				= 'M'
		user.headPortrait_path	= None
		user.headPortrait_url	= None
		user.friends			= list()
		if user.insert():
			return user
		return None


	@staticmethod
	def verify_user(username,password):
		db = DatabaseConnection()[User.table_name]
		user_document = db.find_one({'username':username,'password':password})
		if user_document:
			user = User(user_document)
			return user
		return None

	@staticmethod
	def verify_user_openID(accountType,accountID):
		db = DatabaseConnection()[User.table_name]
		user_document = db.find_one({'accountType':accountType,'accountID':accountID})
		if user_document:
			user = User(user_document)
			return user
		return None

	@staticmethod
	def create_index(db):
		db[User.table_name].ensure_index('username',unique=True)


	def __repr__(self):
		return "<User('%s','%s', '%s', '%s')>" % (self.id, self.username, self.password, self.friends)


class Email(MongoDocument):
	table_name	= "email"

	@staticmethod
	def new(from_user_id,to_user_id,content,send_date,status,sender_name):
		email = Email()
		email.from_user_id	= from_user_id
		email.to_user_id	= to_user_id
		email.content		= content
		email.send_date		= send_date
		email.status		= status
		email.sender_name = sender_name
		if email.insert():
			return email
		print "Insert failed"
		return None


class DatabaseConnection(object):
	__single	= None
	def __new__(clz):
		if not DatabaseConnection.__single:
			DatabaseConnection.__single = DatabaseConnection.__init__(object.__new__(clz))
		return DatabaseConnection.__single.db

	def __init__(self, host="127.0.0.1",port=27017,dbname='pokerdb'):
		self.db	= pymongo.Connection(host=host,port=port)[dbname]
		return self


def init_database():
	db_connection  = DatabaseConnection()

if __name__ == "__main__":
	import os

	db  = DatabaseConnection()

	for collection in db.collection_names():
		try:
			db.drop_collection(collection)
		except Exception as e:
			print e
			pass

	User.create_index(db)
	DealerInfo.create_index(db)

	for i in xrange(1,10):
		bot		= User.new(username="human%s" % i, password=hashlib.md5("123321").hexdigest())
		bot.isBot = True


	#room		= Room(exchange="dealer_exchange_1",blind=10,max_player=9)
	ting		= User.new(username="ting", password=hashlib.md5("123").hexdigest())
	mile		= User.new(username="mile", password=hashlib.md5("123").hexdigest())
	mamingcao   = User.new(username="mamingcao", password=hashlib.md5("123").hexdigest())
	huaqin		= User.new(username="huaqin", password=hashlib.md5("123").hexdigest())
	ting.level	= 12
	ting.total_games= 100
	ting.won_games	= 40
	ting.max_reward	= 998
	ting.last_login	= datetime.strptime("2012-04-13 12:02:20", "%Y-%m-%d %H:%M:%S")
	ting.signature	= "software engineer"
	ting.asset		= 12000
	mile.asset		= 1000
	mamingcao.asset	= 2000
	timeStamp = time.mktime(datetime.strptime("2012-04-13 12:02:20", "%Y-%m-%d %H:%M:%S").timetuple())
	email	= Email.new(from_user_id = ting._id,to_user_id=mile._id,\
			send_date=timeStamp,
			content="aassdd",status=0,sender_name = ting.screen_name)

#	db_connection.addItem(email)
#
	ting.friends = [mile._id, mamingcao._id]
	mile.friends = [ting._id]
#
#
#	db_connection.addItem(ting)
#	db_connection.addItem(mile)
#
#	db_connection.commit_session()

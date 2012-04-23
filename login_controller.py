import time
import json
import hashlib
import tornado.ioloop
import tornado.httpserver
import tornado.web
from datetime import datetime
from database import DatabaseConnection,User,Room

from random import random
class LoginHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		db_connection	= DatabaseConnection()
		db_connection.start_session()
		username		= self.get_argument('username')
		password		= hashlib.md5(self.get_argument('password')).hexdigest()
		user			= db_connection.query(User).filter_by(username = username).filter_by(password = password).first()
		if user is None:
			message		= {'status':'failed', 'content':'invalid username or password'}
		else:
			message		= {'status':'success'}
			self.session['user_id'] = user.id
		user.last_login	= datetime.now()
		db_connection.addItem(user)
		db_connection.commit_session()
		db_connection.close()
		self.set_header('Access-Control-Allow-Origin', '*')
		self.write(json.dumps(message))
		self.finish()

class GuestLoginHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		db_connection	= DatabaseConnection()
		db_connection.start_session()
		if self.get_argument('username', default=None) is None:
			#TODO Check whether username is exist
			username		= "GUEST_" + hashlib.md5(str(time.time()) + str(random())).hexdigest()[0:8]
			password		= hashlib.md5(str(time.time()) + str(random())).hexdigest()
			user			= User(username = username, password = hashlib.md5(password).hexdigest(), stake = 3000)
			print username,password
			db_connection.start_session()
			db_connection.addItem(user)
			db_connection.commit_session()
		else:
			username		= self.get_argument('username')
			print self.get_argument('password'),username
			password		= hashlib.md5(self.get_argument('password')).hexdigest()
			user			= db_connection.query(User).filter_by(username = username).filter_by(password = password).first()

		if user is None:
			message		= {'status':'failed', 'content':'invalid username or password'}
		else:
			message		= {'status':'success', 'username':user.username, 'password':password}
			self.session['user_id'] = user.id
			user.last_login	= datetime.now()

		self.set_header('Access-Control-Allow-Origin', '*')
		self.write(json.dumps(message))
		db_connection.commit_session()
		self.finish()

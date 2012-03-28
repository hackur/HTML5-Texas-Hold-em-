import time
import tornado.ioloop
import tornado.httpserver
import tornado.web
from database import DatabaseConnection,User,Room,MessageQueue

class LoginHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		db_connection	= DatabaseConnection()
		username		= self.get_argument('username')
		password		= self.get_argument('password')
		user			= db_connection.query(User).filter_by(username = username).filter_by(password = password).one()
		if user is None:
			message		= {'status':'failed', 'content':'invalid username or password'}
		else:
			message		= {'status':'success'}
			self.session['user'] = user
		self.set_header('Access-Control-Allow-Origin', '*')
		self.write(json.dumps(message))
		self.finish()

class GuestLoginHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		db_connection	= DatabaseConnection()
		if self.get_argument('username') is None:
			username		= str(time.time()) + '_username'
			password		= str(time.time()) + '_password'
			user			= User
			user.username	= username
			user.password	= password
			db_connection.start_session()
			db_connection.addItem(user)
			db_connection.commit_session()
		else:
			username		= self.get_argument('username')
			password		= self.get_argument('password')
			user			= db_connection.query(User).filter_by(username = username).filter_by(password = password).one()
		
		if user is None:
			message		= {'status':'failed', 'content':'invalid username or password'}
		else:
			message		= {'status':'success', 'username':user.username, 'password':user.password}
			self.session['user'] = user
		self.set_header('Access-Control-Allow-Origin', '*')
		self.write(json.dumps(message))
		self.finish()

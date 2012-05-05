# -*- coding: UTF-8 -*-
import time
import json
import hashlib
import tornado.ioloop
import tornado.httpserver
import tornado.web
from datetime import datetime
from database import DatabaseConnection,User,Room

from random import random
from thread_pool import in_thread_pool, in_ioloop, blocking

class LoginHandler(tornado.web.RequestHandler):
	def post(self):
		username		= self.get_argument('username')
		password		= hashlib.md5(self.get_argument('password')).hexdigest()
		user			= User.verify_user(username,password)
		if user is None:
			message		= {'status':'failed', 'content':'invalid username or password'}
		else:
			message		= {'status':'success'}
			self.session['user_id'] = user._id
			user.last_login	= datetime.now()
		self.set_header('Access-Control-Allow-Origin', '*')
		self.write(json.dumps(message))

class GuestLoginHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		if self.get_argument('username', default=None) is None:
			#TODO Check whether username is exist
			username		= "GUEST_" + hashlib.md5(str(time.time()) + str(random())).hexdigest()[0:8]
			password		= hashlib.md5(str(time.time()) + str(random())).hexdigest()
			user			= User.new(username = username, password = hashlib.md5(password).hexdigest())
			user.screen_name = username.replace("GUEST_",u'游客')[0:6]
		else:
			username		= self.get_argument('username')
			print self.get_argument('password'),username
			password		= hashlib.md5(self.get_argument('password')).hexdigest()
			user			= User.verify_user(username,password)

		if user is None:
			message		= {'status':'failed', 'content':'invalid username or password'}
		else:
			message		= {'status':'success', 'username':user.username, 'password':password}
			self.session['user_id'] = user._id
			user.last_login	= datetime.now()

		self.set_header('Access-Control-Allow-Origin', '*')
		self.write(json.dumps(message))
		self.finish()

from weibo import APIClient

APP_KEY = '3994352852' # app key
APP_SECRET = 'c75a6d36c510a4dae255e75a5e8cb956' # app secret
CALLBACK_URL = 'http://gigiduck.com:8888/weibologinCallback/' # callback url
class SinaWeiboLogin(tornado.web.RequestHandler):
	def get(self):
		client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
		url = client.get_authorize_url(display="mobile")
		print url
		self.redirect(url)

class SinaWeiboLoginBack(tornado.web.RequestHandler):

	@in_thread_pool
	def get_user_info(self,code):
		client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
		r = client.request_access_token(code)
		access_token = r.access_token
		expires_in = r.expires_in
		client.set_access_token(access_token, expires_in)
		uid = client.get.account__get_uid().uid
		print uid
		user_info = client.get.users__show(uid=uid)
		self.got_user_info(uid,user_info)

	@in_ioloop
	def got_user_info(self,uid,user_info):

		user  = User.verify_user_openID(accountType=User.USER_TYPE_SINA_WEIBO,\
							accountID=uid)
		if user == None:
			user = User.new(username="%s_%s" % (User.USER_TYPE_SINA_WEIBO,accountID),\
						accountType=User.USER_TYPE_SINA_WEIBO,accountID=uid)

		user.screen_name = user_info.screen_name
		user.gender	= user_info.gender
		user.headPortrait_url = user_info.profile_image_url #avatar_large?

		user.last_login	= datetime.now()
		self.session['user_id'] = user._id
		self.redirect("/static/user/user.html")

	@tornado.web.asynchronous
	def get(self):
		code = self.get_argument('code')
		self.get_user_info(code)

# -*- coding: UTF-8 -*-
import time
import json
import hashlib
import urllib
import base64
import tornado.ioloop
import tornado.httpserver
import tornado.web
from tornado.httpclient import HTTPClient
from tornado.httpclient import AsyncHTTPClient
from datetime import datetime
from database import DatabaseConnection,User,Room

from random import random
from thread_pool import in_thread_pool, in_ioloop, blocking
import time

class LoginHandler(tornado.web.RequestHandler):
	def post(self):
		username		= self.get_argument('username')
		password		= hashlib.md5(self.get_argument('password')).hexdigest()
		user			= User.verify_user(username,password)
		if user is None:
			message		= {'status':'failed', 'content':'invalid username or password'}
		else:
			message		= {'status':'success'}
			self.session['user_id'] = user.id
			if user.last_login == None:
				user.bonus_notification = 1
			else:
				print user.last_login
				last_login_date = datetime.fromtimestamp(user.last_login)
				if last_login_date.date() < datetime.today().date():
					user.bonus_notification = 1
			user.last_login	= int(time.time())

		self.set_header('Access-Control-Allow-Origin', '*')
		self.write(json.dumps(message))

class GuestLoginHandler(tornado.web.RequestHandler):
	def post(self):
		if self.get_argument('username', default=None) is None:
			#TODO Check whether username is exist
			username		= "GUEST_" + hashlib.md5(str(time.time()) + str(random())).hexdigest()[0:8]
			password		= hashlib.md5(str(time.time()) + str(random())).hexdigest()
			user			= User.new(username = username, password = hashlib.md5(password).hexdigest())
			user.screen_name = username.replace("GUEST_",u'游客')[0:6]
		else:
			username		= self.get_argument('username')
			password		= hashlib.md5(self.get_argument('password')).hexdigest()
			user			= User.verify_user(username,password)

		if user is None:
			message		= {'status':'failed', 'content':'invalid username or password'}
		else:
			message		= {'status':'success', 'username':user.username, 'password':password}
			self.session['user_id'] = user.id
			if user.last_login == None:
				user.bonus_notification = 1
			else:
				last_login_date = datetime.fromtimestamp(user.last_login)
				if last_login_date.date() < datetime.today().date():
					user.bonus_notification = 1

			user.last_login	= int(time.time())

		self.set_header('Access-Control-Allow-Origin', '*')
		self.write(json.dumps(message))

class LogoutHandler(tornado.web.RequestHandler):
	def post(self):
		if 'user_id' in self.session:
			del self.session['user_id']
			self.redirect("/static/index/index.html")

from weibo import APIClient

APP_KEY = '3994352852' # app key
APP_SECRET = 'c75a6d36c510a4dae255e75a5e8cb956' # app secret
CALLBACK_URL = 'http://gigiduck.com:8001/weibologinCallback/' # callback url
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
		print r.access_token,r.expires_in
		client.set_access_token(access_token, expires_in)
		uid = client.get.account__get_uid().uid
		print uid
		user  = User.verify_user_openID(accountType=User.USER_TYPE_SINA_WEIBO,\
							accountID=uid)
		if not user:
			user_info = client.get.users__show(uid=uid)
			user = User.new(username="%s_%s" % (User.USER_TYPE_SINA_WEIBO,uid),\
						accountType=User.USER_TYPE_SINA_WEIBO,accountID=uid)
			user.screen_name = user_info.screen_name
			user.gender	= user_info.gender
			user.headPortrait_url = user_info.profile_image_url #avatar_large?
			print user_info
			user.openIDinfo = user_info
		else:
			print "old user"

		if user.last_login == None:
			user.bonus_notification = 1
		else:
			last_login_date = datetime.fromtimestamp(user.last_login)
			if last_login_date.date() < datetime.today().date():
				user.bonus_notification = 1
		user.last_login	= int(time.time())

		self.got_user_info(uid,user)

	@in_ioloop
	def got_user_info(self,uid,user):
		self.session['user_id'] = user.id
		self.redirect("/static/user/user.html")

	@tornado.web.asynchronous
	def get(self):
		code = self.get_argument('code')
		self.get_user_info(code)


facebook_app_id		= "231740453606973"
facebook_app_secret	= "17a7bf50f0cdbfc143cb3eb63b33a874"
facebook_graph		= "https://graph.facebook.com/%s?fields=id,name,picture,gender,username"
canvas_page			= "http://gigiduck.com:8001/static/user/"
auth_url			= "https://www.facebook.com/dialog/oauth?client_id="+facebook_app_id+"&redirect_uri="+urllib.pathname2url(canvas_page)
class FaceBookLogin(tornado.web.RequestHandler):
	def get(self):
		signed_request	= self.get_argument('signed_request')
		sig, payload	= signed_request.split(u'.', 1)
		user_info		= json.loads(base64.b64decode(payload))

		if "user_id" not in user_info:
			self.finish("<script>top.location.href='" + auth_url + "'</script>")
		else:
			user  = User.verify_user_openID(accountType = User.USER_TYPE_FACEBOOK,
											accountID	= user_info["user_id"]
			if not user:
				self.finish("<script>top.location.href='" + auth_url + "'</script>")
			else:
				self._login_user(user)

	def post(self):
		signed_request	= self.get_argument('signed_request')
		sig, payload	= signed_request.split(u'.', 1)
		data			= json.loads(base64.b64decode(payload))
		if "user_id" not in user_info:
			self.finish("<script>top.location.href='" + auth_url + "'</script>")
		else:
			self.get_user_info(data)

	def get_user_info(self, data):
		graph_url	= facebook_graph % (data["user_id"])
		http_client	= AsyncHTTPClient()
		http_client.fetch(	graph_url,
							self.handle_user_info,
							method	= 'GET',
							headers	= None,
							body	= None)

	def handle_user_info(self, response):
		content	= json.loads(response.body)
		uid		= content["id"]
		user	= User.new(	username	= "%s_%s" % (User.USER_TYPE_FACEBOOK, uid),
							accountType	= User.USER_TYPE_FACEBOOK,
							accountID	= uid)
		user.gender				= content["gender"] == "mail"? "M":"F"
		user.screen_name		= content["name"]
		user.headPortrait_url	= content["picture"]
		self._login_user(user)

	def _login_user(self, user):
		if user.last_login == None:
			user.bonus_notification = 1
		else:
			last_login_date = datetime.fromtimestamp(user.last_login)
			if last_login_date.date() < datetime.today().date():
				user.bonus_notification = 1
		user.last_login	= int(time.time())
		self.session['user_id'] = user.id


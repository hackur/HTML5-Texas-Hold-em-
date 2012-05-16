import json
import os
import sys
import time
from datetime import datetime
# Detect if we're running in a git repo
from os.path import exists, normpath
if exists(normpath('../pika')):
    sys.path.insert(0, '..')

import pika
import tornado.httpserver
import tornado.ioloop
import tornado.web

import database
from database import DatabaseConnection,User,Room
from authenticate import *
from pika_channel import Channel

class UserInfoHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		user = self.user
		# 'n': username
		# 's': stake
		# 'l': level
		msg = {'n':user.username,'s':user.asset,'l':user.level,'id':user.id}
		self.write(json.dumps(msg))

class DailyBonusHandler(tornado.web.RequestHandler):
	@authentpcate
	def get(self):
		user = self.user
		last_login_date = datetime.fromtimestamp(user.last_login)
		if last_login_date.date() < datetime.today().date():
			self.user.update_attr('asset', 1000)
			self.user.last_login = time.time()
			self.write(json.dumps({'status':'success'}))
		else:
			self.write(json.dumps({'status':'failed'}))


class BotRefillHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		if self.user.isBot:
			self.user.update_attr('asset',3000)
			self.write(str(self.user.asset))
			return

		self.send_error(404)


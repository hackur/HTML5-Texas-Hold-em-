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
import re
class UserInfoHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		user = self.user
		# 'n': username
		# 's': stake
		# 'l': level
		# 'g': gender
		msg = {	'n':user.username,
				's':user.asset,
				'l':user.level,
				'id':user.id,
				'g':user.gender}
		self.write(json.dumps(msg))

	@authenticate
	def post(self):
		user	= self.user
		gender	= self.get_argument('gender')
		nickname= self.get_argument('nickname')
		if self.validate_user_info(gender, nickname):
			user.screen_name= nickname
			user.gender		= gender
			self.write(json.dumps({'status':'success'}))
		else:
			self.write(json.dumps({'status':'failed'}))

	def validate_user_info(self, gender, nickname):
		if gender not in ['M','F']:
			return False
		if re.match(r"^\b[a-zA-Z0-9_]{1,32}$", nickname) == None:
			return False
		return True


class DailyBonusHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		user = self.user
		if user.bonus_notification == 1:
			user.update_attr('asset', 1000)
			user.bonus_notification = 0
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


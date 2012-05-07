
import json
import os
import sys
import time

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


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

from sqlalchemy.orm import sessionmaker,relationship, backref
import database
from database import DatabaseConnection,User,Room
from authenticate import *
from pika_channel import Channel
try:
    import cpickle as pickle
except:
    import pickle

class UserInfoHandler(tornado.web.RequestHandler):
	@authenticate
	def get(self):
		user = self.session['user']
		# 'n': username
		# 's': stake
		# 'l': level
		msg = {'n':user.username,'s':user.stake,'l':user.level}
		self.write(json.dumps(msg))
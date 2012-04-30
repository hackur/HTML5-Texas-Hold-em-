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
from database import DatabaseConnection,User,Room, DealerInfo
from authenticate import *
from pika_channel import Channel,PersistentChannel
from sqlalchemy.sql import functions as SQLFunc

class ConfigReader(object):
	cache = {}
	objCache = {}
	@staticmethod
	def _load(name):
		f = open("./config/%s.json" % name)
		fcontent = f.read()
		ConfigReader.cache[name] = fcontent
		ConfigReader.objCache[name] = json.loads(fcontent)
		f.close()

	@staticmethod
	def get(name):
		if not name in ConfigReader.cache:
			ConfigReader._load(name)

		return ConfigReader.cache[name]

	@staticmethod
	def getObj(name):
		if not name in ConfigReader.objCache:
			ConfigReader._load(name)

		return ConfigReader.objCache[name]



class ConfigHandler(tornado.web.RequestHandler):
	AllowSet = set(('room',))
	def get(self,name):
		if name in ConfigHandler.AllowSet:
			self.write(ConfigReader.get(name))


if __name__ == "__main__":
	ConfigReader.get("room")

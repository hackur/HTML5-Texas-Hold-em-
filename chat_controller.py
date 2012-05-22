import time
import math
import os
import json
import tornado.ioloop
import tornado.httpserver
import tornado.web
from authenticate import *
from datetime import datetime
from pika_channel import *
class SentChatMessageHandler(tornado.web.RequestHandler):
	@authenticate
	def post(self):
		message				= {}
		user				= self.user
		exchange			= self.session['exchange']
		message["method"]	= "chat"
		message["seat"]		= int(self.get_argument("seat"))
		message["user"]		= user.id
		message["content"]	= self.get_argument("message")
		message["room"]		= user.room_id
		self.channel		= Channel(self.application.channel, exchange)
		self.channel.publish_message("dealer", json.dumps(message))
		self.finish()

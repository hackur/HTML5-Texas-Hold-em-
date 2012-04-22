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
		self.mongodb	= self.application.settings['_db']
		board_messages	= self.mongodb.board.find_one({"user_id": self.session['user_id']})
		if 'is_sit_down' in board_messages and board_messages['is_sit_down'] == True:
			message				= {}
			user				= self.session['user']
			exchange			= str(user.room.exchange)
			message["method"]	= "chat"
			message["seat"]		= int(self.get_argument("seat"))
			message["user"]		= user.id
			message["content"]	= self.get_argument("message")
			message["room"]		= user.room.id
			self.channel		= Channel(self.application.channel, exchange)
			self.channel.publish_message("dealer", json.dumps(message))
			result	= "{\"status\":\"success\"}"
		else:
			result	= "{\"status\":\"failed\"}"
		self.finish(result)

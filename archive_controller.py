import time
import os
import json
import tornado.ioloop
import tornado.httpserver
import tornado.web
from authenticate import *
from database import DatabaseConnection,User,Family,FamilyPosition,Email,HeadPortrait

class PersonalArchiveHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user	= self.session['user']
		message	= {
					"status": "success",
					"name": user.username,
					"head_portrait": user.head_portrait.url,
					"family": user.family.name,
					"position": user.family_position.name,
					"level": user.level,
					"asset": user.asset,
					"percentage": (user.total_games * 1.0) / use.won_games,
					"total_games": user.total_games,
					"won_games": user.won_games,
					"max_reward": user.max_reward,
					"last_login": user.last_login,
					"signature": user.signature
				}
		self.write(json.dumps(message))
		self.finish()

class HeadPortraitHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		directory		= "uploads/" + user.username
		user			= self.session['user']
		head_portrait	= self.request.files['head_portrait'][0]
		if not os.path.exists(directory):
			os.makedirs(directory)
		output_file		= open(directory + "/" + head_portrait['filename'], 'w')
		output_file.write(head_portrait['body'])

		db_connection  = DatabaseConnection()
		db_connection.start_session()
		portrait			= HeadPortrait()
		portrait.url		= "./" + directory +  head_portrait['filename']
		portrait.path		= "./" + directory +  head_portrait['filename']
		user.head_portrait	= portrait
		db_connection.addItem(portrait)
		db_connection.addItem(user)
		db_connection.commit_session()

		message = {"status":"success"}
		self.finish(json.dumps(message))

class EmailListHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user	= self.session['user']
		message = {"status":"success", "emails":user.in_mails}
		self.finish(json.dumps(message))

class EmailSendHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user			= self.session['user']
		destination		= self.get_argument('destination')
		content			= self.get_argument('conent')
		sent_date		= self.get_argument('datetime')
		email			= Email()
		email.from_id	= user.id
		email.to_id		= destination
		email.content	= content
		email.sent_date	= sent_date
		email.satus		= 0
		db_connection  = DatabaseConnection()
		db_connection.start_session()
		db_connection.addItem(email)
		db_connection.commit_session()
		message	= {"status":"success"}
		self.finish(json.dumps(message))



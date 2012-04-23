import time
import math
import os
import json
import tornado.ioloop
import tornado.httpserver
import tornado.web
from authenticate import *
from datetime import datetime
from database import DatabaseConnection,User,Family,FamilyPosition,Email,HeadPortrait

class PersonalArchiveHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user		= self.session['user']
		portrait	= "#"
		family		= "-1"
		position	= "-1"
		percentage	= 0
		if user.head_portrait is not None:
			portrait = user.head_portrait.url
		if user.family is not None:
			family	= user.family.name
			position= user.family_position.name
		if user.total_games > 0:
			percentage = (user.won_games * 1.0) / user.total_games
		message	= {
					"status": "success",
					"name": user.username,
					"head_portrait": portrait,
					"family": family,
					"position": position,
					"level": user.level,
					"asset": user.asset,
					"percentage": percentage,
					"total_games": user.total_games,
					"won_games": user.won_games,
					"max_reward": user.max_reward,
					"last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S"),
					"signature": user.signature or "This guy is too lazy to leave a signature"
				}
		self.write(json.dumps(message))
		self.finish()

class HeadPortraitHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user			= self.session['user']
		directory		= "uploads/" + user.username
		head_portrait	= self.request.files['head_portrait'][0]

		if not os.path.exists(directory):
			os.makedirs(directory)
		output_file		= open(directory + "/" + head_portrait['filename'], 'wb')
		output_file.write(head_portrait['body'])
		output_file.seek(0)
		output_file.close()

		if user.head_portrait is not None:
			old_portrait		= user.head_portrait
			db_connection.delete(old_portrait)
			os.remove(old_portrait.path)

		portrait			= HeadPortrait()
		portrait.url		= "./" + directory + '/' + head_portrait['filename']
		portrait.path		= "./" + directory + '/' + head_portrait['filename']
		user.head_portrait	= portrait
		self.db_connection.addItem(portrait)
		self.db_connection.addItem(user)
		self.db_connection.commit_session()
		message = {"status":"success","url":user.head_portrait.url}
		self.finish(json.dumps(message))

class EmailListHandler(tornado.web.RequestHandler):
	(PAGE_SIZE,PAGE_OFFSET) = (20, 19)
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		page	= self.get_argument('page', 1)
		start	= (page - 1) * self.PAGE_SIZE
		end		= start + self.PAGE_OFFSET
		user	= self.session['user']

		all_emails	= self.db_connection.query(Email).filter_by(to_user = user).order_by(Email.sent_date)

		total_emails= all_emails.count()
		pages		= math.ceil(total_emails / self.PAGE_SIZE)
		emails		= all_emails.slice(start, end)
		email_list	= list()
		for email in emails:
			email_list.append({
								"id": email.id,
								"date": email.sent_date,
								"from": email.from_user.username
							})

		message =	{
						"status": "success",
						"total": total_emails,
						"pages": pages,
						"emails": email_list
					}
		self.finish(json.dumps(message))

class EmailViewHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		email_id= self.get_argument('email')
		user	= self.session['user']
		email	= self.db_connection.query(Email).filter_by(to_user = user).filter_by(id = email_id).first()
		message	= {"status":"success", "email":email}
		self.finish(json.dumps(message))

class EmailSendHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user				= self.session['user']
		destination			= self.get_argument('destination')
		content				= self.get_argument('content')
		reply_to			= self.get_argument('reply_to', None)
		email				= Email()
		email.from_id		= user.id
		email.to_id			= destination
		email.content		= content
		email.sent_date		= datetime.now()
		email.satus			= 0
		email.reply_to_id	= reply_to
		self.db_connection.start_session()
		self.db_connection.addItem(email)
		self.db_connection.commit_session()
		message	= {"status":"success"}
		self.finish(json.dumps(message))

class BuddyInfoHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user		= self.session['user']

		message = {
			"userId": user.id,
			"friends": list()
		}
		for friend in user.friends:
			message["friends"].append({
						"id": friend.id,
						"head_portrait": "#",
						"family": friend.family,
						"name": friend.username,
						"position": "-1",
						"level": friend.level,
						"asset": friend.asset,
					})
		self.finish(json.dumps(message))


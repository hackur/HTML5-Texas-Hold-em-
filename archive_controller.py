import time
import math
import os
import json
import tornado.ioloop
import tornado.httpserver
import tornado.web
from authenticate import *
from datetime import datetime
from database import DatabaseConnection,User,Family,FamilyPosition,Email
import hashlib

class PersonalArchiveHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user		= self.user
		portrait	= None
		family		= "-1"
		position	= "-1"
		percentage	= 0
		if user.headPortrait_url is not None:
			portrait = user.headPortrait_url
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
					"percentage": "%.2f%%" % (percentage * 100),
					"total_games": user.total_games,
					"won_games": user.won_games,
					"max_reward": user.max_reward,
					"last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S"),
					"signature": user.signature or "This guy is too lazy to leave a signature"
				}
		self.write(json.dumps(message))
		self.finish()

class PlayerArchiveHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		player_id	= self.get_argument("id", -1);
		player		= self.db_connection.query(User).filter_by(id = player_id).first();
		portrait	= None
		family		= "-1"
		position	= "-1"
		percentage	= 0
		if player.headPortrait_url is not None:
			portrait = player.headPortrait_url
		if player.family is not None:
			family	= player.family.name
			position= player.family_position.name
		if player.total_games > 0:
			percentage = (player.won_games * 1.0) / player.total_games
		message	= {
					"status": "success",
					"name": player.username,
					"head_portrait": portrait,
					"family": family,
					"position": position,
					"level": player.level,
					"asset": player.asset,
					"percentage": "%.2f%%" % (percentage * 100),
					"total_games": player.total_games,
					"won_games": player.won_games,
					"max_reward": player.max_reward,
					"last_login": player.last_login.strftime("%Y-%m-%d %H:%M:%S"),
					"signature": player.signature or "This guy is too lazy to leave a signature",
					"friends": str(player.friends),
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

		m = hashlib.md5()
		m.update(head_portrait['body'])
		filename = m.hexdigest()
		output_file		= open(directory + "/" + filename, 'wb')
		output_file.write(head_portrait['body'])


		output_file.seek(0)
		output_file.close()

		user.headPortrait_url		= "/" + directory + '/' + filename
		user.headPortrait_path		= "./" + directory + '/' + filename
		self.db_connection.addItem(user)
		self.db_connection.commit_session()
		message = {"status":"success","url":user.headPortrait_url}
		self.finish(json.dumps(message))

class EmailListHandler(tornado.web.RequestHandler):
	(PAGE_SIZE,PAGE_OFFSET) = (10, 9)
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		page		= int(self.get_argument('page', 1))
		user		= self.session['user']
		all_emails	= self.db_connection.query(Email).filter_by(to_user = user).order_by(Email.send_date)
		total_emails= all_emails.count()
		pages		= math.ceil((1.0 *total_emails) / self.PAGE_SIZE)
		if page > pages:
			current = pages
		else:
			if page <= 0:
				current	= 1
			else:
				current = page
		start		= (current - 1) * self.PAGE_SIZE
		end			= start + self.PAGE_OFFSET
		print "[%d,%d, %d, %d] " % (page,pages, start, end)
		emails		= all_emails.slice(start, end)
		email_list	= list()
		for email in emails:
			email_list.append({
								"id": email.id,
								"date": email.send_date.strftime("%Y-%m-%d %H:%M:%S"),
								"sender_name": email.from_user.username,
								"sender_id":email.from_user.id,
								"message": email.content
							})

		message =	{
						"status":	"success",
						"total":	int(total_emails),
						"pages":	int(pages),
						"current":	int(current),
						"emails":	email_list
					}
		self.finish(json.dumps(message))

class EmailViewHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		email_id= self.get_argument('email')
		user	= self.session['user']
		email	= self.db_connection.query(Email).filter_by(to_user = user).filter_by(id = email_id).first()
		message	= {"status":"success", "email":str(email)}
		self.finish(json.dumps(message))

class EmailSendHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user_id				= self.session['user_id']
		destination			= self.get_argument('destination')
		content				= self.get_argument('content')
		reply_to			= self.get_argument('reply_to', None)
		email				= Email()
		email.from_user_id	= user_id
		email.to_user_id	= destination
		email.content		= content
		email.send_date		= datetime.now()
		email.status		= 0
		email.reply_to_id	= reply_to
		self.db_connection.addItem(email)
		self.db_connection.commit_session()
		message	= {"status":"success"}
		self.finish(json.dumps(message))

class EmailDeleteHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user_id = self.session['user_id']
		email_id= self.get_argument('email_id')
		self.db_connection.query(Email).filter(Email.id==email_id).filter(Email.to_user_id == user_id).delete()
		self.db_connection.commit_session()
		message = {"status":"success"}
		self.finish(json.dumps(message))


class BuddyInfoHandler(tornado.web.RequestHandler):
	def addBuddy(self):
		user = self.session["user"]
		friend_id = int(self.get_argument("user_id"))
		print "new friend ",friend_id
		friend_list = user.friends
		for friend in friend_list:
			print "old friend: ",friend.id
			if friend_id == friend.id:
				message = {"status": "friend already in the list"}
				self.finish(json.dumps(message))
				return
		friend = self.db_connection.query(User).filter(User.id == friend_id).first()
		if friend == None:
			message = {"status": "friend doesn't exist"}
			self.finish(json.dumps(message))
			return
		friend_list.append(friend)
		self.db_connection.addItem(user)
		self.db_connection.commit_session()
		message = {"status": "friend added"}
		print user.friends
		self.finish(json.dumps(message))


	@tornado.web.asynchronous
	@authenticate
	def post(self, action):
		if action == "add":
			self.addBuddy()
			return

		user = self.session['user']
		message = {
			"userId": user.id,
			"friends": list()
		}
		for friend in user.friends:
			message["friends"].append({
						"id": friend.id,
						"head_portrait": None,
						"family": friend.family,
						"name": friend.username,
						"position": "-1",
						"level": friend.level,
						"asset": friend.asset,
					})
		self.finish(json.dumps(message))



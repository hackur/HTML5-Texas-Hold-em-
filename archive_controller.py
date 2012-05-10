import time
import math
import os
import json
import tornado.ioloop
import tornado.httpserver
import tornado.web
from authenticate import *
from datetime import datetime
from database import DatabaseConnection,User,Email
import hashlib
from  bson.objectid import ObjectId

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
		if user.total_games > 0:
			percentage = (user.won_games * 1.0) / user.total_games
		message	= {
					"status": "success",
					"name": user.screen_name,
					"head_portrait": portrait,
					"family": family,
					"position": position,
					"level": user.level,
					"asset": user.asset,
					"percentage": "%.2f%%" % (percentage * 100),
					"total_games": user.total_games,
					"won_games": user.won_games,
					"max_reward": user.max_reward,
					"last_login": datetime.fromtimestamp(user.last_login).strftime("%Y-%m-%d %H:%M:%S"),
					"signature": user.signature or "This guy is too lazy to leave a signature"
				}
		self.write(json.dumps(message))
		self.finish()

class PlayerArchiveHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		player_id	= self.get_argument("id", -1);
		player		= User.find(_id = player_id)
		portrait	= None
		family		= "-1"
		position	= "-1"
		percentage	= 0
		if player.headPortrait_url is not None:
			portrait = player.headPortrait_url
		#if player.family is not None:
		#	family	= player.family.name
		#	position= player.family_position.name
		if player.total_games > 0:
			percentage = (player.won_games * 1.0) / player.total_games
		message	= {
					"status": "success",
					"name": player.screen_name,
					"head_portrait": portrait,
					"family": family,
					"position": position,
					"level": player.level,
					"asset": player.asset,
					"percentage": "%.2f%%" % (percentage * 100),
					"total_games": player.total_games,
					"won_games": player.won_games,
					"max_reward": player.max_reward,
					"last_login": datetime.fromtimestamp(player.last_login).strftime("%Y-%m-%d %H:%M:%S"),
					"signature": player.signature or "This guy is too lazy to leave a signature",
					"friends": str(player.friends),
				}
		self.write(json.dumps(message))
		self.finish()

class HeadPortraitHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user			= self.user
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
		message = {"status":"success","url":user.headPortrait_url}
		self.finish(json.dumps(message))

class EmailListHandler(tornado.web.RequestHandler):
	(PAGE_SIZE,PAGE_OFFSET) = (10, 9)
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		page		= int(self.get_argument('page', 1))
		user_id		= self.session['user_id']
		all_emails	= [ email for email in Email.find_all(to_user_id=str(user_id)) ]
			#sort=[('send_date',1)]) ]
		total_emails=  len(all_emails)
		pages		= math.ceil((1.0 *total_emails) / self.PAGE_SIZE)
		if page > pages:
			current = pages
		else:
			if page <= 0:
				current	= 1
			else:
				current = page
		start		= (current - 1) * self.PAGE_SIZE
		if start < 0:
			start = 0
		end			= start + self.PAGE_OFFSET
		print "[%d,%d, %d, %d] " % (page,pages, start, end)
		emails		= all_emails[start:end]
		email_list	= list()
		for email in emails:
			email_list.append({
								"id": email.id,
								"date": datetime.fromtimestamp(email.send_date).strftime("%Y-%m-%d %H:%M:%S"),
								"sender_name": email.sender_name,
								"sender_id":str(email.from_user_id),
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
		print 'mail id',email_id
		if not email_id:
			self.finish()

		user_id	= self.session['user_id']
		email	= Email.find(to_user_id = str(user_id), _id = email_id)
		if email == None:
			self.finish()
			return

		message	= {"status":"success", "email":str(email.content)}
		self.finish(json.dumps(message))

class EmailSendHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user_id				= self.session['user_id']
		destination			= self.get_argument('destination')
		content				= self.get_argument('content')
		timeStamp = time.mktime(datetime.now().timetuple())

		email				= Email.new(str(user_id),destination,content,timeStamp,
							0,self.user.screen_name)

		message	= {"status":"success"}
		self.finish(json.dumps(message))

class EmailDeleteHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	@authenticate
	def post(self):
		user_id = self.session['user_id']
		email_id= self.get_argument('email_id')
		Email.find(_id = email_id, to_user_id = str(user_id)).remove()
		message = {"status":"success"}
		self.finish(json.dumps(message))


class BuddyInfoHandler(tornado.web.RequestHandler):
	def addBuddy(self):
		user = self.user
		friend_id = self.get_argument("user_id")
		print "new friend ",friend_id
		friend_list = user.friends
		for friend in friend_list:
			print "old friend: ",friend
			if friend_id == friend:
				message = {"status": "friend already in the list"}
				self.finish(json.dumps(message))
				return
		friend = User.find(_id = friend_id)
		if friend == None:
			message = {"status": "friend doesn't exist"}
			self.finish(json.dumps(message))
			return
		friend_list.append(friend.id)
		user.friends = friend_list # Just for saving the result
		message = {"status": "friend added"}
		print user.friends
		self.finish(json.dumps(message))


	@tornado.web.asynchronous
	@authenticate
	def post(self, action):
		if action == "add":
			self.addBuddy()
			return

		user = self.user
		message = {
			"userId": str(user._id),
			"friends": list()
		}
		for friend_id in user.friends:
			friend = User.find(_id=friend_id)
			message["friends"].append({
						"id": str(friend._id),
						"head_portrait": None,
						"name": friend.screen_name,
						"position": "-1",
						"level": friend.level,
						"asset": friend.asset,
					})
		self.finish(json.dumps(message))



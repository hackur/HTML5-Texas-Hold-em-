from tornado.httpclient import HTTPClient
from tornado.httpclient import AsyncHTTPClient
from robot_dictionary import *
import tornado.ioloop
import urllib
import json
import pprint
import array

class Seat:
	def __init__(self, seat_id = -1, stake = 0, table = 0):
		self.id			= seat_id
		self.stake		= stake
		self.table		= table
		self.hand_cards	= []

class DecisionMaker:
	def __init__(self):
		self.deck	= 52*[0]
		suit		= 0x8000;
		index		= 0
		for i in xrange(4):
			for j in xrange(13):
				self.deck[index] = primes[j] | (j << 8) | suit | (1 << (16+j));
				index += 1
			suit >>= 1
		print self.deck

	def _rank_compare(self, left,right):
		if left[0] != right[0] :
			return left[0] - right[0]
		else:
			for i in xrange(len(left[1])):
				if left[1][i] != right[1][i]:
					return left[1][i] - right[1][i]
		return 0

	def convert_to_deck(self, card):
		_suit = 0
		_value= 0
		if len(card) == 2:
			_value= card[0]
			_suit = card[1]
		elif len(card) == 3:
			_value= "10"
			_suit = card[2]
		if _value.isdigit():
			_value = int(_value)
		else:
			if _value == "J":
				_value = 11
			elif _value == "Q":
				_value = 12
			elif _value == "K":
				_value = 13
			elif _value == "A":
				_value = 14

		if _suit == "C":
			_suit = 0
		elif _suit == "D":
			_suit = 1
		elif _suit == "H":
			_suit = 2
		elif _suit == "S":
			_suit = 3
		_value -= 2
		print _suit * 13 + _value
		return self.deck[_suit * 13 + _value]

	def findit(self, key):
		low	= 0
		high= 4887
		mid	= 0
		while low <= high:
			mid = (high+low) >> 1
		#	print "product[%d]=%d",(mid,products[mid])
			if key < products[mid]:
				high = mid - 1
			elif key > products[mid]:
				low = mid + 1
			else:
				return mid
		print "ERROR:  no match found; key = %d\n" % (key)
		return -1;

	def eval_5hand(self, c1, c2, c3, c4, c5):
		q = (c1|c2|c3|c4|c5) >> 16
		if ( c1 & c2 & c3 & c4 & c5 & 0xF000 ) > 0:
			return  flushes[q]

		s = unique5[q]
		if s > 0:
			return s
		q = (c1&0xFF) * (c2&0xFF) * (c3&0xFF) * (c4&0xFF) * (c5&0xFF)
		q = self.findit(q)
		return values[q]

	def _rank(self, cards):
		q	= 0
		best= 9999
		length = len(cards)
		sub_hand = []
		if length == 7:
			for i in xrange(21):
				for j in perm7[i]:
					sub_hand.append(cards[j])
				q = self.eval_5hand( sub_hand[0], sub_hand[1], sub_hand[2], sub_hand[3], sub_hand[4] );
				if q < best:
					best = q

		elif length == 6:
			for i in xrange():
				for j in perm6[i]:
					sub_hand.append(cards[j])
				q = self.eval_5hand( sub_hand[0], sub_hand[1], sub_hand[2], sub_hand[3], sub_hand[4] );
				if q < best:
					best = q

		elif length == 5:
			q = self.eval_5hand( cards[0], cards[1], cards[2], cards[3], cards[4] );
			if q < best:
				best = q

		return best

	def filter(self,source, exclude_list):
		result	= []
		flag	= False
		for element in source:
			for item in exclude_list:
				if element.symbol == item.symbol and  element.value == item.value :
					flag = True
					break;
			if flag == False:
				result.append(element)
			flag = False

		return result

	def _hand_strength(self, robot_cards, board_cards):
		ahead	= 0
		tied	= 0
		behind	= 0
		robot_all_cards = robot_cards + board_cards
		robot_rank		= self._rank(robot_all_cards)
		remain_cards	= filter(lambda x: x not in robot_all_cards, self.deck)
		for i in xrange(len(remain_cards) - 1):
			for j  in xrange(i + 1, len(remain_cards)):
				opp_rank = self._rank([remain_cards[i], remain_cards[j]] + board_cards)
				compare_result = opp_rank - robot_rank #self._rank_compare(robot_rank, opp_rank)
				if compare_result > 0:
					ahead	+= 1
				elif compare_result == 0:
					tied	+= 1
				else:
					behind	+= 1
	#	print "ahead = %d"%(ahead)
	#	print "tied	 = %d"%(tied)
	#	print "behind= %d"%(behind)
		return (ahead + tied / 2) / (ahead + tied + behind)

	def _hand_potential(self, robot_cards, board_cards):
		hand_potential_total = [0.0,0.0,0.0]
		hand_potential	= [3*[0.0] for x in xrange(3)]
		robot_all_cards = robot_cards + board_cards
		remain_cards	= filter(lambda x: x not in robot_all_cards, self.deck) #self.filter(self.cards, robot_all_cards)
		robot_rank		= self._rank(robot_all_cards)
		for i in xrange(len(remain_cards) - 1):
			for j in xrange(i + 1, len(remain_cards)):
				opp_cards		= [remain_cards[i], remain_cards[j]]
				opp_rank		= self._rank(opp_cards + board_cards)
				compare_result	= opp_rank - robot_rank #self._rank_compare(robot_rank, opp_rank)
				if compare_result > 0:
					index	= 0
				elif compare_result == 0:
					index	= 1
				else:
					index	= 2
				hand_potential_total[index] += 1
				temp_cards	= filter(lambda x: x not in opp_cards, remain_cards) #self.filter(remain_cards, opp_cards)
				if len(board_cards) == 3:
					for k in xrange(len(temp_cards)-1):
						for o in xrange(k + 1, len(temp_cards)):

							#print "i=[%d] j=[%d] k=[%d] o=[%d]\n"%(i,j,k,o)
							temp_board	= board_cards + [temp_cards[k],temp_cards[o]]
							robot_best	= self._rank(temp_board+robot_cards)
							opp_best	= self._rank(temp_board+opp_cards)
							best_comparison= opp_best - robot_best #self._rank_compare(robot_best, opp_best)
							if best_comparison > 0:
								hand_potential[index][0] +=1
							elif best_comparison == 0:
								hand_potential[index][1] +=1
							else:
								hand_potential[index][2] +=1
				elif len(board_cards) == 4:
					for k in xrange(len(temp_cards)-1):
						temp_board	= board_cards + [temp_cards[k]]
						robot_best	= self._rank(temp_board+robot_cards)
						opp_best	= self._rank(temp_board+opp_cards)
						best_comparison= self._rank_compare(robot_best, opp_best)
						if best_comparison > 0:
							hand_potential[index][0] +=1
						elif best_comparison == 0:
							hand_potential[index][1] +=1
						else:
							hand_potential[index][2] +=1

				else:
					return -1
		ppot	= (hand_potential[2][0] + hand_potential[2][1] / 2 + hand_potential[1][0] / 2) / (hand_potential_total[2]+hand_potential_total[1]/2 +1)
		npot	= (hand_potential[0][2] + hand_potential[1][2]/2 + hand_potential[0][1] / 2) / (hand_potential_total[0]+hand_potential_total[1]/2 +1)
		return (ppot, npot)


	def make_decision(self, seats, robot_seat, robot_cards, board_cards):
		robot_decks	= []
		board_decks = []
		print robot_cards
		print board_cards
		for card in robot_cards:
			robot_decks.append(self.convert_to_deck(card))
		print robot_decks
		for card in board_cards:
			board_decks.append(self.convert_to_deck(card))

		print board_decks
		hs			= self._hand_strength(robot_decks, board_decks)
		(ppot, npot)= self._hand_potential(robot_decks, board_decks)
		p_win		= hs*(1 - npot) + (1 - hs) * ppot
		print "win probability", p_win

class Robot:
	Login_URL_Template					= "http://%s:%d/login"
	Enter_Room_URL_Template				= "http://%s:%d/enter"
	Sit_Down_URL_Template				= "http://%s:%d/sit-down"
	Post_Board_Message_URL_Template		= "http://%s:%d/post-board-message"
	Listen_Board_Message_URL_Template	= "http://%s:%d/listen-board-message"
	Action_ALL			= 1
	Action_Call_Stake	= 2
	Action_Raise_Stake	= 3
	Action_Check_Stake	= 4
	Action_Discard_Game	= 5
	Action_Stand_Up		= 8
	def __init__(self, ip='127.0.0.1', port = 80, username=None, password=None, room=None):
		self.ip			= ip
		self.port		= port
		self.username	= username
		self.password	= password
		self.room		= room
		self.timestamp	= -1
		self.public_cards	= [0, 0, 0, 0, 0]
		self.seats			= [0, 0, 0, 0, 0, 0, 0, 0, 0]
		self.http_client	= AsyncHTTPClient()
		self.decision_maker = DecisionMaker()
		self.login_url		= Robot.Login_URL_Template % (ip, port)
		self.enter_url		= Robot.Enter_Room_URL_Template % (ip, port)
		self.sit_down_url				= Robot.Sit_Down_URL_Template % (ip, port)
		self.post_board_message_url		= Robot.Post_Board_Message_URL_Template % (ip ,port)
		self.listen_board_message_url	= Robot.Listen_Board_Message_URL_Template % (ip, port)

	def start(self):
		print "Robot login [start]"
		post_data	= {"username":self.username, "password":self.password}
		body		= urllib.urlencode(post_data)
		self.http_client.fetch(self.login_url,
								self.login_handle,
								method='POST',
								headers=None,
								body=body)
		print "Robot login [end]"

	def login_handle(self,response):
		print "Robot login handle [start]"
		content		= json.loads(response.body)
		if content["status"] == "success":
			self.cookies= response.headers['Set-Cookie'];
			self.asset	= content['s']
			self.enter()
		else:
			pass
		print "Robot login handle [end]"

	def enter(self):
		print "Robot enter [start]"
		post_data	= {"room_id":self.room}
		body		= urllib.urlencode(post_data)
		headers		= {"Cookie":self.cookies}
		self.http_client.fetch(	self.enter_url,
								self.enter_handle,
								method='POST',
								headers=headers,
								body=body)
		print "Robot enter [end]"

	def enter_handle(self, response):
		print "Robot enter handle [start]"
		content		= json.loads(response.body)
		if content["status"] == "success":
			self.cookies= response.headers['Set-Cookie'];
			self.min_stake	= content["room"]["min_stake"]
			self.max_stake	= content["room"]["max_stake"]
			for i in xrange(len(content["room"]["seats"])):
				if content["room"]["seats"][i] == None:
					self.seat = i

			if self.asset > (self.min_stake+self.max_stake)/2:
				self.stake	= (self.min_stake+self.max_stake)/2
			else:
				self.stake	= self.min_stake

			self.asset	-= self.stake
			self.sit_down()
		else:
			pass
		print "Robot enter handle [end]"


	def sit_down(self):
		print "Robot sit_down  [start]"
		post_data	= {"seat": self.seat, "stake":self.stake}
		body		= urllib.urlencode(post_data)
		headers		= {"Cookie":self.cookies}
		self.http_client.fetch(	self.sit_down_url,
								self.sit_down_handle,
								method	= "POST",
								headers	= headers,
								body	= body)

		print "Robot sit_down [end]"

	def sit_down_handle(self,response):
		print "Robot sit_down handle [start]"
		content		= json.loads(response.body)
		if content["status"] == "success":
			self.cookies= response.headers['Set-Cookie'];
			self.listen_board_message()
		else:
			pass
		print "Robot sit_down handle [end]"

	def listen_board_message(self):
		print "Robot listen board message [start]"
		post_data	= {"timestamp": self.timestamp}
		body		= urllib.urlencode(post_data)
		headers		= {"Cookie":self.cookies}
		self.http_client.fetch(	self.listen_board_message_url,
								self.listen_board_message_handle,
								method	= "POST",
								headers	= headers,
								body	= body)

		print "Robot listen board message [end]"

	def listen_board_message_handle(self, response):
		print "Robot listen board message handle [start]"
		content	= json.loads(response.body)
		print content
		for message in content:
			if message["status"] == "success":
				self.cookies= response.headers['Set-Cookie'];
				for i in xrange(len(content)):
					message			= content[i]
					self.timestamp	= message["timestamp"]
					method = getattr(self,"handle_" + message['msgType'])
					method(message)
		print "Robot listen board message handle [end]"
	def send_post_message(self):
		self.decision_maker.make_decision(self.seats, self.seat, self.hand_card, self.public_card)

	def handle_sit(self,data):
		print "handle sit [start]"
		self.seats[data["seat_no"]] = Seat()
		self.seats[data["seat_no"]].seat_id = data["seat_no"]
		self.seats[data["seat_no"]].stake = data["info"]["player_stake"]
		self.seats[data["seat_no"]].table = 0
		print "handle sit [end]"

	def handle_bhc(self,data):
		print "handle bhc [start]"
		pass
		print "handle bhc [end]"

	def handle_phc(self,data):
		print "handle phc [start]"
		self.seats[self.seat].hand_cards.extend(data["cards"])
		pass
		print "handle phc [end]"

	def handle_winner(self,data):
		print "handle winner [start]"
		pass
		print "handle winner [end]"

	def handle_next(self,data):
		print "handle next [start]"
		print "seat no =%d"%(data["seat_no"])
		print "self seat=%d"%(self.seat)
		if data["seat_no"] == self.seat:
			self.send_post_message()
		pass
		print "handle next [end]"

	def handle_action(self, data):
		print "handle action [start]"
		self.seats[data["seat_no"]].stake = data["stake"]
		self.seats[data["seat_no"]].table = data["table"]
		pass
		print "handle action [end]"

	def handle_public_card(self,data):
		print "handle public [start]"
		self.public_cards = []
		for i in xrange(len(data["cards"])):
			self.public_cards.push(data["cards"][i]);
		pass
		print "handle public [end]"

	def handle_start_game(self,data):
		print "handle start game [start]"
		self.public_cards = []
		pass
		print "handle start game [end]"

	def handle_pot(self, data):
		print "handle pot [start]"
		pass
		print "handle pot [end]"


	def handle_standup(self, data):
		print "handle stand up [start]"
		stand_up_player = filter(lambda x: "seat_no" in x,data)
		for player in stand_up_player:
			self.seat[player["seat_no"]] = None
		print "handle stand up [end]"


if __name__=="__main__":
	#robot	= Robot(ip='127.0.0.1',port=8888,username='mile',password='123',room=1)
	#robot.start()
	#ioloop	= tornado.ioloop.IOLoop.instance()
	#ioloop.start()
	decision_maker	= DecisionMaker()
	cards	= ["2C", "2D"]
	p_cards	= ["2H", "2S", "6C"]
	decision_maker.make_decision([0], 1, cards, p_cards);

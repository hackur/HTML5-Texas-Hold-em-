import time
from threading import Timer
import poker_controller

class Seat(object):
	(SEAT_EMPTY,SEAT_WAITING,SEAT_PLAYING) = (0,1,2)
	(DEALER, SMALL_BLIND, BIG_BLIND) = (0,1,2)

	def __init__(self):
		self._user = None
		self._cards = None
		self._inAmount = 0
		self._status = Seat.SEAT_EMPTY
		self._direct_key = None
		self._role = None
		self.combination = []
		self.handcards = []
		pass

	def is_empty(self):
		return self._status == Seat.SEAT_EMPTY

	def sit(self, user, direct_key, private_key):
		self._user = user
		self._status = Seat.SEAT_WAITING
		self._direct_key = direct_key
		self._private_key= private_key

	def get_user(self):
		return self._user

	def get_direct_key(self):
		return self._direct_key
	
	def get_private_key(self):
		return self._private_key

	def set_status(self, status):
		self._status = status

	def get_role(self):
		return self._role
	def set_role(self, role):
		self._role = role
	

class GameRoom(object):
	(GAME_WAIT,GAME_PLAY) = (0,1)
	def __init__(self, room_id, owner, dealer, num_of_seats = 9, blind = 10):
		self.room_id		= room_id
		self.owner		= owner
		self.status		= GameRoom.GAME_WAIT
		self.dealer		= dealer
		self.broadcast_key	= "broadcast_%s_%d.testing" %(self.dealer.exchange, self.room_id)
		self.player_list	= []
		# self.waiting_list	= []
		self.audit_list		= []
		self.seats		= []
		self.player_stake	= []
		for x in xrange(num_of_seats):
			self.seats.append(Seat())
			self.player_stake.append(None)
		self.occupied_seat	= 0
		self.suit = ["DIAMOND", "HEART", "SPADE", "CLUB"]
		self.face = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
		self.msg_count= 0
		self.blind = blind
		self.current_dealer = 0
		self.small_blind = 0
		self.big_blind = None

	def broadcast(self,msg,route_key=None):
		self.msg_count += 1
		msg['timestamp'] = self.msg_count
		print msg["timestamp"]
		if not route_key:
			route_key = self.broadcast_key
			
		self.dealer.broadcast(route_key, msg)

	def sit(self, player, seat_no, direct_key, private_key):
		print "direct_key.........................................", direct_key
		seat_no = int(seat_no)
		print "seat request =>%d\n" % (seat_no)
		if seat_no > len(self.seats):
			return (False, "Seat number is too large: %s we have %s" % (seat_no,len(self.seats)))
		if not self.seats[seat_no].is_empty():
			return (False, "Seat Occupied")
		if self.status == GameRoom.GAME_PLAY:
			return (False, "Game Ongoing")
		self.seats[seat_no].sit(player, direct_key, private_key)
		
		self.player_stake[seat_no] = player.stake	# read user's money
		print player.stake
		
		self.player_list.append(self.seats[seat_no])

		self.occupied_seat += 1

		msg_broadcast	= {'status':'success', 'seat_no': seat_no, "username": self.seats[seat_no].get_user().username}
		#stake still needed
		self.broadcast(msg_broadcast)

		if self.occupied_seat == 2:
			t = Timer(2, self.start_game)
			t.start()
		return (True, "")

	def assign_role(self):
		index = (self.current_dealer + 1) % len(self.seats)
		i = 0
		for counter in xrange(9):
			if not self.seats[index].is_empty():
				if i == 0:		
					self.current_dealer = index % len(self.seats)
				elif i == 1:
					self.small_blind = index % len(self.seats)
				elif len(self.player_list) > 2 and i == 2:
					self.big_blind = index % len(self.seats)
				i += 1
			index = (index + 1) % len(self.seats)
		print "current_dealer: ", self.current_dealer
		print "small_blind: ", self.small_blind
		print "big_blind: ", self.big_blind

	
	def start_game(self):
		self.status = GameRoom.GAME_PLAY
		game = poker_controller.PokerController(self.player_list)
		game.getFlop()
		table_card_list = []
		self.assign_role()
		
		print "-------------------------------------------------------------------"
		#Distribute cards to each player
		for seat in self.player_list:
			seat.set_status = Seat.SEAT_PLAYING
			card_list = []
			for card in seat.handcards:
				card_list.append(str(card))
			msg_sent = {"Cards in hand": card_list}
			self.broadcast(msg_sent,seat.get_private_key())
		
		# bet in big blind and small blind by default
		print self.player_stake[self.small_blind]
		if self.player_stake[self.small_blind] < self.blind/2:
			self.player_stake[self.small_blind] = 0
		else:
			self.player_stake[self.small_blind] -= self.blind/2
			print "small_blind stake: ", self.player_stake[self.small_blind]
		if isinstance(self.big_blind, int):		
			if self.player_stake[self.big_blind] < self.blind:
				self.player_stake[self.big_blind] = 0
			else:
				self.player_stake[self.big_blind] -= self.blind
				print "big_blind stake: ", self.player_stake[self.big_blind]
		

		

		#waiting for bet
		

		# Distribute cards on table
		for card in game.publicCard:
			table_card_list.append(str(card))
		msg_broadcast = {"Cards on Table": table_card_list}
		self.broadcast(msg_broadcast)	

		#
		game.getOne()
		table_card_list.append(str(game.publicCard[-1]))
		msg_broadcast = {"Cards on Table": table_card_list}
		self.broadcast(msg_broadcast)
		
		game.getOne()
		table_card_list.append(str(game.publicCard[-1]))
		msg_broadcast = {"Cards on Table": table_card_list}
		self.broadcast(msg_broadcast)

		win_lose_dict = game.getWinner()
		win_list = win_lose_dict["winners"]
		for winner in win_list: 
			msg_broadcast = {"winner":winner.get_user().username}
			self.broadcast(msg_broadcast)

		self.status = GameRoom.GAME_WAIT

	def user_bet(self, command, amount, seat_no, player):
		t = Timer(10, disard_game)
		t.start()
		if command == 1 or command == 2 or command == 3:
			if amount <= player.stake:
				self.player_stake[seat_no] = 0
			else:
				self.player_stake[seat_no] -= amount

	def discard_game(self, seat_no):
		self.seats[seat_no].set_status = Seat.SEAT_EMPTY	# set the status of this seat to empty
		self.player_list.remove(self.seats[seat_no])		# remove the player from player list
		user = self.seats[seat_no].get_user()			# get user info from database
		user.stake = self.player_stake[seat_no]			# update user's stake
		self.add_audit(user)					# add the user to audit list
		


	def add_audit(self, player):
		self.audit_list.append(player)

	def display_card(self, symbol, value):
		return "%s/%s" %(self.suit[symbol], self.face[value-2])

	def deal_card(card_obj_list):
		card_list = []
		for card in card_obj_list:
			card_list.append(str(card))
		return card_list

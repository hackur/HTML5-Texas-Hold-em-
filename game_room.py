import time
from threading import Timer
from poker_controller import PokerController

class Seat(object):
	(SEAT_EMPTY,SEAT_WAITING,SEAT_PLAYING) = (0,1,2)

	def __init__(self):
		self._user = None
		self._cards = None
		self._inAmount = 0
		self._status = Seat.SEAT_EMPTY
		self._rights = []
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


	@property
	def status(self):
		return self._status

	@status.setter
	def status(self, status):
		self._status = status

	@property
	def rights(self):
		return self._rights

	@rights.setter
	def rights(self, rights):
		self._rights = rights

	def get_role(self):
		return self._role
	def set_role(self, role):
		self._role = role
	def is_waiting(self):
		return self.status == Seat.SEAT_WAITING

class GameRoom(object):
	(GAME_WAIT,GAME_PLAY) = (0,1)
	def __init__(self, room_id, owner, dealer, num_of_seats = 9, blind = 10):
		self.room_id		= room_id
		self.owner		= owner
		self.status		= GameRoom.GAME_WAIT
		self.dealer		= dealer
		self.broadcast_key	= "broadcast_%s_%d.testing" %(self.dealer.exchange, self.room_id)
		self.player_list	= []
		self.audit_list		= []
		self.seats			= []
		self.player_stake	= []
		self.occupied_seat	= 0
		self.suit = ["DIAMOND", "HEART", "SPADE", "CLUB"]
		self.face = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
		self.msg_count= 0
		self.blind = blind
		self.min_amount = 0
		self.current_dealer = 0
		self.small_blind = 0
		self.big_blind = 0
		self.current_seat = None
		for x in xrange(num_of_seats):
			self.seats.append(Seat())
			self.player_stake.append(None)
		self.current_seat = None

		self.poker_controller = PokerController(self.seats)

	def broadcast(self,msg):
		self.msg_count += 1
		msg['timestamp'] = self.msg_count
		self.dealer.broadcast(self.broadcast_key, msg)

	def direct_message(self, msg, destination):
		self.msg_count += 1
		msg['timestamp'] = self.msg_count
		self.dealer.broadcast(destination, msg)
#####
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
		self.occupied_seat += 1
		message	= {'status':'success', 'seat_no': seat_no, "username": self.seats[seat_no].get_user().username}
		self.broadcast(message)

		if self.occupied_seat == 2:
			t = Timer(2, self.start_game)
			t.start()
		return ( True, "" )


	def start_game(self):
		self.status = GameRoom.GAME_PLAY
		self.poker_controller.start()
		self.poker_controller.getFlop()
		self.assign_role()

		#Distribute cards to each player
		for seat in self.seats:
			if seat.status != Seat.SEAT_EMPTY:
				seat.status = Seat.SEAT_PLAYING
				card_list	= []
				for card in seat.handcards:
					card_list.append(str(card))
				msg_sent = {"Cards in hand": card_list}
				self.direct_message(msg_sent,seat.get_private_key())

		# bet in big blind and small blind by default
		print self.player_stake[self.small_blind]
		if self.player_stake[self.small_blind] < self.blind/2:
			self.player_stake[self.small_blind] = 0
		else:
			self.player_stake[self.small_blind] -= self.blind/2
			print "small_blind stake: ", self.player_stake[self.small_blind]

		if self.player_stake[self.big_blind] < self.blind:
			self.player_stake[self.big_blind] = 0
		else:
			self.player_stake[self.big_blind] -= self.blind
			print "big_blind stake: ", self.player_stake[self.big_blind]

		self.current_seat = self.info_next(self.big_blind, [2,3,5])
		print "current seat =>", self.current_seat

	def get_seat(self, user_id):
		return filter(lambda seat: seat.get_user() != None and seat.get_user().id == user_id, self.seats)[0]

	def bet_stake(self, user_id, private_key, amount):
		command			= 1
		seat_no			= self.current_seat
		request_seat	= self.get_seat(user_id)
		valid_seat		= self.seats[seat_no]
		if valid_seat == request_seat:
			self.countdown.cancel()
			if self.is_proper_amount(1, amount, seat_no):
				self.player_stake[seat_no] -= amount
				self.min_amount		= amount
				self.current_seat	= self.info_next(seat_no, [2, 3, 5])

				broadcast_message	= {'status':'success', 'stake':self.player_stake[seat_no]}
				next_player_message	= {'status':'active', 'rights':[2, 3, 5]}

				self.broadcast(broadcast_message)
				self.direct_message(next_player_message,self.seats[self.current_seat].get_private_key())

	def call_stake(self, amount, seat_no, player):
		if self.current_seat == seat_no:
			self.countdown.cancel()
			amount = self.is_proper_amount(2, amount, seat_no)
		self.current_seat = self.info_next(self.current_seat, [2,3,5])

	def raise_stake(self, amount, seat_no, player):
		if self.current_seat == seat_no:
			self.countdown.cancel()
			self.min_amout = amount
			amount = self.is_proper_amount(3, amount, seat_no)
		self.current_seat = self.info_next(self.current_seat, [2,3,5])

	def check(self):
		if self.current_seat == seat_no:
			self.countdown.cancel()
		self.current_seat = self.info_next(self.current_seat, [2,3,4,5])

	def discard_game(self, seat_no):
		self.seats[seat_no].status = Seat.SEAT_WAITING	# set the status of this seat to empty
														# remove the player from player list
		user = self.seats[seat_no].get_user()			# get user info from database
		user.stake = self.player_stake[seat_no]			# update user's stake
		self.add_audit(user)							# add the user to audit list
		self.info_next(self.current_seat, self.seat[self.nect].rights)

	def info_next(self, current_position, rights):
		next = self.check_next(current_position)
		self.seats[next].rights = rights
		self.countdown = Timer(10, discard_game, args=[next])
		self.countdown.start()
		return next


	def add_audit(self, player):
		self.audit_list.append(player)

	def is_proper_amount(self, amount, seat_no):
		if command == 3:
			min_amount = 2 * self.min_amount
		max_amount = min(max(self.player_stake), self.player_stake[seat_no])
		min_amount = max(self.blind, self.min_amount)
		if amount > max_amount:
			return False
		elif amount < min_amount:
			return False
		else:
			return True


	def check_next(self, current_position):
		next = (current_position + 1) % len(self.seats)
		for x in xrange(9):
			if self.seats[next].status == Seat.SEAT_PLAYING:
				break
			else:
				next = (next + 1) % len(self.seats)
		return next

	def assign_role(self):
		number		= 0
		dealer		= -1
		small_blind = -1
		big_blind	= -1
		index		= (self.current_dealer + 1) % len(self.seats)
		for counter in xrange(9):
			if not self.seats[index].is_empty():
				number += 1
				if dealer == -1:
					dealer = index
				elif small_blind == -1:
					small_blind = index
				elif big_blind == -1:
					big_blind	= index
					break
			index = (index + 1) % len(self.seats)

		if number == 2:
			big_blind	= small_blind
			small_blind	= dealer

		self.current_dealer = dealer
		self.small_blind	= small_blind
		self.big_blind		= big_blind
		print "current_dealer: ",	dealer
		print "small_blind: ",		small_blind
		print "big_blind: ",		big_blind

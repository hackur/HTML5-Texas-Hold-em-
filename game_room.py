import time
import math
from threading import Timer
from poker_controller import PokerController
from operator import attrgetter
import sys
from tornado import ioloop
import functools

class Seat(object):
	(SEAT_EMPTY,SEAT_WAITING,SEAT_PLAYING,SEAT_ALL_IN) = (0,1,2,3)

	def __init__(self, seat_id):
		self._seat_id = seat_id
		self._user	= None
		self._cards	= None
		self._inAmount = 0
		self.status = Seat.SEAT_EMPTY
		self._rights = []
		self._role = None
		self.combination = []
		self.handcards = []
		self.table_amount = 0
		self.player_stake = 0

	def __str__(self):
		return "seat[%d], user[%d]" % (self._seat_id, self._user.id)
	def __repr__(self):
		return "seat[%d], user[%d]" % (self._seat_id, self._user.id)

	def is_empty(self):
		return self.status == Seat.SEAT_EMPTY

	def sit(self, user, private_key):
		self._user = user
		self.status = Seat.SEAT_WAITING
		self._private_key= private_key
		self.rights = None

	def get_user(self):
		return self._user

	def get_private_key(self):
		return self._private_key

	def get_role(self):
		return self._role
	def set_role(self, role):
		self._role = role
	def is_waiting(self):
		return self.status == Seat.SEAT_WAITING

	def bet(self,desire_amount):
		if self.player_stake < desire_amount:
			result = self.player_stake
		else:
			result = desire_amount

		self.player_stake -= result
		self.table_amount += result
		return result
	def to_listener(self):
		result = {}
		if not self._user:
			result['user'] = None
			return

		result['user'] = self._user.username
		result['status'] = self.status
		result['table_amount']  = self.table_amount
		result['player_stake']  = self.player_stake
		return result




class GameRoom(object):
	(GAME_WAIT,GAME_PLAY) = (0,1)
	(A_ALLIN,A_CALLSTAKE,A_RAISESTAKE,A_CHECK,A_DISCARDGAME) = (1,2,3,4,5)
	def __init__(self, room_id, owner, dealer, num_of_seats = 9, blind = 10):
		self.room_id        = room_id
		self.owner      = owner
		self.status     = GameRoom.GAME_WAIT
		self.dealer     = dealer
		self.broadcast_key  = "broadcast_%s_%d.testing" %(self.dealer.exchange, self.room_id)
		self.audit_list     = []
		self.seats          = []
		self.occupied_seat  = 0
		self.suit = ["DIAMOND", "HEART", "SPADE", "CLUB"]
		self.face = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
		self.msg_count= 0
		self.blind = blind
		self.min_amount = 0
		self.current_dealer = 0
		self.small_blind = 0
		self.big_blind = 0
		self.current_seat = None
		self.flop_flag = False
		self.all_in_flag = False
		self.prize_pool = 0
		self.pot = {}
		self.num_of_checks = 0
		self.action_counter = 0
		self.amount_limits = {}
		self.t = None
		self.ioloop = ioloop.IOLoop.instance()
		self.user_seat = {}

		for x in xrange(num_of_seats):
			self.seats.append(Seat(x))

		self.current_seat = None

		self.poker_controller = PokerController(self.seats)
		self.actions = {GameRoom.A_ALLIN		:self.all_in,
						GameRoom.A_CALLSTAKE	:self.call_stake,
						GameRoom.A_RAISESTAKE	:self.raise_stake,
						GameRoom.A_CHECK		:self.check,
						GameRoom.A_DISCARDGAME	:self.discard_game}
	def to_listener(self):
		result = {}
		result['status'] = self.status
		if self.status == GameRoom.GAME_PLAY:
			result['publicCard'] = self.poker_controller.publicCard
			result['current_seat'] = self.current_seat
		result['seats'] = [ seat.to_listener() for seat in self.seats ]
		result['timestamp'] = self.msg_count
		return result


	def broadcast(self,msg):
		self.msg_count += 1
		msg['timestamp'] = self.msg_count
		self.dealer.broadcast(self.broadcast_key, msg)

	def direct_message(self, msg, destination):
		self.msg_count += 1
		msg['timestamp'] = self.msg_count
		self.dealer.broadcast(destination, msg)

	def user_action(self,args):
		action          = args["action"]
		private_key     = args["private_key"]
		user_id         = args["user_id"]
		seat_no  = self.current_seat
	#	print "SEAT NO.......................",seat_no
	#	print "USER ID.......................", user_id
		if self.is_valid_seat(user_id, seat_no) and self.is_valid_rights(action, seat_no):
			self.clearCountDown()
			if action != GameRoom.A_RAISESTAKE:
				self.actions[action](user_id)
			else:
				amount = args['amount']
				self.actions[action](user_id,amount)

	def clearCountDown(self):
		if self.countdown:
			self.ioloop.remove_timeout(self.countdown)
			self.countdown = None

	def sit(self, player, seat_no, direct_key, private_key,stake):
		print "direct_key.........................................", direct_key
		print "seat request =>%d\n" % (seat_no)
		if seat_no > len(self.seats):
			return (False, "Seat number is too large: %s we have %s" % (seat_no,len(self.seats)))
		if not self.seats[seat_no].is_empty():
			return (False, "Seat Occupied")


		self.user_seat[player.id] = seat_no
		self.seats[seat_no].sit(player, private_key)
		self.seats[seat_no].player_stake = int(stake)
		self.occupied_seat += 1
		message = {'msgType':'sit', 'seat_no': seat_no, "info": self.seats[seat_no].to_listener()}
		self.broadcast(message)

		if self.occupied_seat == 3:
			self.t = self.ioloop.add_timeout(time.time() + 5, self.start_game)
		#	self.t = Timer(5, self.start_game)
		#	self.t.start()
		return ( True, "" )


	def start_game(self):
		self.status = GameRoom.GAME_PLAY
		self.poker_controller.start()
		self.assign_role()

		#Distribute cards to each player
		for seat in self.seats:
			if seat.status != Seat.SEAT_EMPTY:
				seat.status = Seat.SEAT_PLAYING
				card_list   = []
				for card in seat.handcards:
					card_list.append(str(card))
				msg_sent = {"Cards in hand": card_list}
				self.direct_message(msg_sent,seat.get_private_key())
				self.broadcast({"HC":seat.seat_no}) # HC for Have Card
				#self.direct_message(msg_sent,seat.get_private_key())

		# bet in big blind and small blind by default
		print self.seats[self.small_blind].player_stake
		self.seats[self.small_blind].bet(self.blind/2)
		self.seats[self.big_blind].bet(self.blind)
		print "big_blind stake: ", self.seats[self.big_blind].player_stake

		print self.seats[self.big_blind].get_user().username
		print self.seats[self.small_blind].get_user().username
		print self.seats[self.current_dealer].get_user().username

		self.min_amount = self.blind
		self.current_seat = self.info_next(self.big_blind, [1,2,3,5])
		print "next seat in action =>", self.current_seat

	def get_seat(self, user_id):
		return self.seats[self.user_seat[user_id]]
		#return filter(lambda seat: seat.get_user() != None and seat.get_user().id == user_id, self.seats)[0]

	def is_valid_seat(self, user_id, current_seat):
		request_seat = self.get_seat(user_id)
		valid_seat = self.seats[current_seat]
		if valid_seat == request_seat:
			print "VALID SEAT"
			return True
		else:
			print "INVALID SEAT"
			return False

	def is_valid_rights(self, command, seat_no):
		print command
		print self.seats[seat_no]
		if command not in self.seats[seat_no].rights:
			print "INVALID ACTION!"
			self.discard_game(seat_no)
			return False
		else:
			print "valid action"
			return True

	def no_more_stake(self):
		for x in xrange(len(self.seats)):
			print "----player stake-----"
			print self.seats[x].player_stake
			if self.seats[x].status == Seat.SEAT_PLAYING:
				if self.seats[x].player_stake > 0:
					return False
		return True

	def call_stake(self, user_id, amount = 0, inComplete_all_in_flag = False):
		print "CALL!"
		if self.num_of_checks != 0:
			self.num_of_checks = 0
		print "num_of_checks: ", self.num_of_checks
		command = GameRoom.A_CALLSTAKE

		seat_no = self.current_seat
		if not inComplete_all_in_flag:
			amount = self.min_amount - self.seats[seat_no].table_amount

		if not self.is_proper_amount(amount, command):
			print "NOOOOOOO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
			return

		print "call amount: :", amount
		self.seats[seat_no].bet(amount)
		print "player stake: ", self.seats[seat_no].player_stake
		print "table amount for seat "+ str(seat_no) + ": " + str(self.seats[seat_no].table_amount)
		self.min_amount = self.seats[seat_no].table_amount
		if self.flop_flag == False:
			if self.same_amount_on_table():
				# At end of first round, small_blind and dealer are out of money
				if len(filter(lambda seat: seat.status == Seat.SEAT_PLAYING, self.seats)) < 2:
					self.round_finish()
				else:
					self.current_seat = self.info_next(seat_no, [1,3,4,5])        # final choice goes to the person who gives the first raise
			else:
				self.current_seat = self.info_next(seat_no, [1,2,3,5])
		else:
			if self.same_amount_on_table():                 # all players have put down equal amount of money, next round
				self.round_finish()
			else:
				if inComplete_all_in_flag == False:
					self.current_seat = self.info_next(seat_no, [1,2,3,5])
				else:
					print "-----------sb before you has called all in---------------"
					self.current_seat = self.info_next(seat_no, [2,5])      # cannot re-raise after sb's all-in
		print "--------------------self.min_amount in call_stake: ", self.min_amount


		card_list = []
		for card in self.poker_controller.publicCard:
			card_list.append(str(card))
			print str(card)

		broadcast_message = {"status": "success", "public cards": card_list, "username": self.seats[seat_no].get_user().username, "stake": self.seats[seat_no].player_stake}
		next_player_message = {"status":"active", "username": self.seats[self.current_seat].get_user().username, "rights":self.seats[self.current_seat].rights}

		self.broadcast(broadcast_message)
		self.direct_message(next_player_message, self.seats[self.current_seat].get_private_key())

	def raise_stake(self, user_id,  amount):
		print "RAISE!"
		if self.num_of_checks != 0:
			self.num_of_checks = 0
		print "num_of_checks: ", self.num_of_checks
		amount          = int(amount)
		command         = 3
		seat_no         = self.current_seat
		if self.is_proper_amount(amount, command):
			print "This is a proper amount"
			self.seats[seat_no].player_stake -= amount
			self.seats[seat_no].table_amount += amount
			print "table amount for seat "+ str(seat_no) + ": " + str(self.seats[seat_no].table_amount)
			self.min_amount     = self.seats[seat_no].table_amount
			self.current_seat   = self.info_next(seat_no, [1, 2, 3, 5])

			broadcast_message   = {'status':'success', 'username': self.seats[seat_no].get_user().username, 'stake':self.seats[seat_no].player_stake}
			next_player_message = {'status':'active', 'username': self.seats[self.current_seat].get_user().username, 'rights':[1, 2, 3, 5]}

			self.broadcast(broadcast_message)
			self.direct_message(next_player_message, self.seats[self.current_seat].get_private_key())
		else:
			print "RAISE INVALID AMOUNT OF MONEY!"
			sys.exit()

	def check(self, user_id):
		print "CHECK!"
		print "flop_flag: ", self.flop_flag
		command = 4
		seat_no = self.current_seat
		player_list = filter(lambda seat: seat.status == Seat.SEAT_PLAYING, self.seats)
		self.min_amount = 0         # may cause bugs`
		if self.flop_flag == False:         #Before flop, sb. called check
			print "------------------------------", self.flop_flag
			self.round_finish()
		else:
			self.num_of_checks += 1
			print "num_of_checks: ", self.num_of_checks
			if self.num_of_checks < len(player_list):
				self.current_seat = self.info_next(seat_no, [1,3,4,5])
			else:
				self.num_of_checks = 0
				self.round_finish()

		card_list = []
		for card in self.poker_controller.publicCard:
			card_list.append(str(card))
			print str(card)

		broadcast_message = {"status": "success", "public cards": card_list, "username": self.seats[seat_no].get_user().username, "stake": self.seats[seat_no].player_stake}
		next_player_message = {"status":"active", "username": self.seats[self.current_seat].get_user().username, "rights":self.seats[self.current_seat].rights}

		self.broadcast(broadcast_message)
		self.direct_message(next_player_message, self.seats[self.current_seat].get_private_key())

	def discard_game(self, user_id):
		print "FOLD!!"
		seat_no = self.current_seat
		print self.current_seat
		self.seats[seat_no].status = Seat.SEAT_WAITING  # set the status of this seat to empty
														# remove the player from player list
		user = self.seats[seat_no].get_user()           # get user info from database
		user.stake = self.seats[seat_no].player_stake         # update user's stake
		self.add_audit(self.seats[seat_no].get_user())  # add the user to audit list

		if self.same_amount_on_table():
			self.round_finish()
		else:
			self.current_seat = self.info_next(seat_no, self.seats[seat_no].rights)

		broadcast_message = {"status": "success", "username": self.seats[seat_no].get_user().username, "stake": self.seats[seat_no].player_stake}
		next_player_message = {"status": "active", "username": self.seats[self.current_seat].get_user().username, "rights": self.seats[self.current_seat].rights}

		self.broadcast(broadcast_message)
		#self.direct_message(next_player_message, self.seats[self.current_seat].get_private_key())
		self.broadcast(next_player_message)


	def all_in(self, user_id):
		print "FULL POWER! ALL INNNNNNNNN!!!!!!!!"
		if self.num_of_checks != 0:
			self.num_of_checks = 0
		print "num_of_checks: ", self.num_of_checks
		command  = 1
		seat_no  = self.current_seat
		amount  = min(self.seats[seat_no].player_stake, self.amount_limits[GameRoom.A_ALLIN][1])
		print "self.min_amount before all in: ", self.min_amount
		print "----------------",self.min_amount == amount + self.seats[seat_no].table_amount

		print "amount to be on table: ", amount + self.seats[seat_no].table_amount
		if 0 < amount + self.seats[seat_no].table_amount < self.min_amount:
			self.seats[seat_no].player_stake = 0
			self.seats[seat_no].table_amount += amount
			# self.seats[seat_no].status = Seat.SEAT_ALL_IN
			if self.same_amount_on_table(True):
				self.round_finish()
			else:
				self.current_seat = self.info_next(seat_no, [1,2,3,5])

			broadcast_message   = {'status':'success', 'username': self.seats[seat_no].get_user().username, 'stake':self.seats[seat_no].player_stake}
			next_player_message = {'status':'active', 'username': self.seats[self.current_seat].get_user().username, 'rights':self.seats[seat_no].rights}

			self.broadcast(broadcast_message)
			self.direct_message(next_player_message, self.seats[self.current_seat].get_private_key())

		elif self.min_amount == amount + self.seats[seat_no].table_amount:
			print "going to call stake"
			self.call_stake(user_id)
		elif self.min_amount < amount + self.seats[seat_no].table_amount <= 2 * self.min_amount - self.seats[seat_no].table_amount:
			#self.seats[seat_no].status = Seat.SEAT_ALL_IN
			self.call_stake(user_id,  amount, inComplete_all_in_flag = True)
		else:
			#self.seats[seat_no].status = Seat.SEAT_ALL_IN
			self.raise_stake(user_id, amount)



	def info_next(self, current_position, rights):
		next_seat = self.check_next(current_position)
		self.seats[next_seat].rights = rights
		callback = functools.partial(self.discard_game,self.seats[next_seat].get_private_key())
		#self.countdown = Timer(20, self.discard_game, args=[self.seats[next_seat].get_private_key()])
		self.countdown = self.ioloop.add_timeout(time.time() + 10, callback)

		print "seat no. for next player: ", self.seats[next_seat].get_user().username
		self.calculate_proper_amount(next_seat, rights)
		return next_seat


	def add_audit(self, player):
		self.audit_list.append(player)

	def same_amount_on_table(self, smaller_than_min_amount=False):
		i = 0
		player_list = filter(lambda seat: seat.status == Seat.SEAT_PLAYING, self.seats)

		for seat in player_list:
			print "player names: =============:", seat.get_user().username
			if seat.table_amount == self.min_amount:
				if seat.player_stake == 0:
					seat.status = Seat.SEAT_ALL_IN
				i += 1
				continue
			else:
				if seat.player_stake == 0:
					if smaller_than_min_amount == True:
						i += 1
					seat.status = Seat.SEAT_ALL_IN
					print "all in name: >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ", seat.get_user().username
				else:
					return False
		print "length of player list in same_amount_on_table: ", len(player_list)
		print "==============================================", i
		if i == len(player_list):
			return True
		else:
			return False


	def round_finish(self):
		print "ROUND FINISHED!!!!"
		self.clearCountDown();
		player_list = filter(lambda seat: seat.status == Seat.SEAT_PLAYING or seat.status == Seat.SEAT_ALL_IN, self.seats)
		playing_list = filter(lambda seat: seat.status == Seat.SEAT_PLAYING, self.seats)
		print "-----------no more stake------------"
		print self.no_more_stake()
		print "__________len(playing_list)_________"
		print len(playing_list)
		print "_____len(public card)---------------"
		print len(self.poker_controller.publicCard)

		if self.no_more_stake() or len(playing_list) < 2 or len(self.poker_controller.publicCard) == 5:
			if len(self.poker_controller.publicCard) < 3:
				self.poker_controller.getFlop()
				self.poker_controller.getOne()
				self.poker_controller.getOne()
			elif len(self.poker_controller.publicCard) < 5:
				for x in xrange(5 - len(self.poker_controller.publicCard)):
					self.poker_controller.getOne()

			print "We have a winner!"
	#		print self.poker_controller.publicCard
			for player in player_list:
				print player.get_user().username
			self.create_pot(player_list)
#			self.poker_controller.get_winner()
			winner_dict = {}
			ante_dict = self.distribute_ante()
			winner_dict = {k:v for k, v in ante_dict.items() if v > 0} #filter(lambda seat: winner_dict[seat] != 0, ante_dict)
			print winner_dict
			if len(winner_dict) > 1:
				for seat in winner_dict.keys():
					print "seat: ", seat.get_user().username
					card_list = []
					for card in seat.handcards:
						card_list.append(str(card))
					print card_list
					broadcast_msg = {"winner": seat.get_user().username, "handcards": card_list}
					self.broadcast(broadcast_msg)

			sys.exit()
		else:
			self.create_pot(player_list)
			self.min_amount = self.blind/2
			if self.flop_flag == False:
				self.poker_controller.getFlop()
				self.flop_flag = True
			else:
				self.poker_controller.getOne()
			self.current_seat = self.info_next(self.current_dealer, [1,3,4,5])
			return

	def distribute_ante(self):
		ante_dict = {}
		rank_list = self.poker_controller.rank_users()
		for i in xrange(len(rank_list)):
			print "rank list"
			for item in rank_list[i]:
				print item.get_user().id;

			for owner, ante in self.pot.iteritems():
				share_list = filter(lambda seat: seat.get_user().id in owner and seat.status != Seat.SEAT_WAITING, rank_list[i])
				for user in share_list:
					if user in ante_dict:
						ante_dict[user] += math.floor(ante/len(share_list))
					else:
						ante_dict[user] = math.floor(ante/len(share_list))
				if len(share_list) > 0 :
					self.pot[owner] = 0

		print ante_dict
		return ante_dict


	def create_pot(self, player_list):
		pot_owner		= []
		seat_to_remove	= []

		for x in xrange(len(player_list)):
			if player_list[x].table_amount == 0:
				seat_to_remove.append(player_list[x])
		for element in seat_to_remove:
			player_list.remove(element)

		if len(player_list) == 0:
			return

		player_list = sorted(player_list, key = attrgetter("table_amount"))
		min_bet = player_list[0].table_amount
		for x in xrange(len(player_list)):
			pot_owner.append(player_list[x].get_user().id)
			print ":::::::::::::::::: ", player_list[x].get_user().id
			player_list[x].table_amount -= min_bet
			print ":::::::::::::::::: ", player_list[x].table_amount
		pot_owner = tuple(pot_owner)
		if pot_owner not in self.pot:
			self.pot[pot_owner] = 0
		self.pot[pot_owner] += min_bet * len(player_list)
		print self.pot
		self.create_pot(player_list)

	def calculate_proper_amount(self, seat_no, rights):
		total_amount_list = []
		for seat in self.seats:
			if seat.status >= Seat.SEAT_PLAYING:
				total_amount_list.append(seat.player_stake + seat.table_amount)

		total_amount_list.sort(reverse = True)
		print "length of total amount list: ", len(total_amount_list)
		if len(total_amount_list) > 1:
			max_amount = min(self.seats[seat_no].player_stake, total_amount_list[1] - self.seats[seat_no].table_amount)
		else:
			max_amount = min(self.seats[seat_no].player_stake, total_amount_list[0] - self.seats[seat_no].table_amount)

		min_amount = max(self.min_amount - self.seats[seat_no].table_amount, self.big_blind)
		if GameRoom.A_CALLSTAKE in self.seats[seat_no].rights:
			if self.seats[seat_no].player_stake < min_amount:
				self.seats[seat_no].rights.remove(GameRoom.A_CALLSTAKE)
			else:
				self.amount_limits[GameRoom.A_CALLSTAKE] = (min_amount, max_amount)

		min_amount = 2 * self.min_amount - self.seats[seat_no].table_amount
		if GameRoom.A_RAISESTAKE in self.seats[seat_no].rights:
			if self.seats[seat_no].player_stake < min_amount:
				self.seats[seat_no].rights.remove(GameRoom.A_RAISESTAKE)
				print "REMOVE----" , 'x' * 100
			else:
				self.amount_limits[GameRoom.A_RAISESTAKE] = (min_amount, max_amount)

		if GameRoom.A_ALLIN in self.seats[seat_no].rights:
			self.amount_limits[GameRoom.A_ALLIN] = (min(self.seats[seat_no].player_stake - self.seats[seat_no].table_amount, self.min_amount-self.seats[seat_no].table_amount), \
					min(self.seats[seat_no].player_stake, total_amount_list[1] - self.seats[seat_no].table_amount))

		print self.amount_limits
		return self.amount_limits


	def is_proper_amount(self, amount, command):
		print amount
		print self.amount_limits[command][1]
		print self.amount_limits[command][0]
		if amount > self.amount_limits[command][1]:
			self.amount_limits.clear()
			return False
		elif amount < self.amount_limits[command][0]:
			self.amount_limits.clear()
			return False
		else:
			self.amount_limits.clear()
			return True


	def check_next(self, current_position):
		num_of_players = 0
		print "------------------------------", current_position
		next_seat = (current_position + 1) % len(self.seats)
		for x in xrange(9):
			if self.seats[next_seat].status == Seat.SEAT_PLAYING:
				num_of_players += 1
				break
			else:
				next_seat = (next_seat + 1) % len(self.seats)
		print "+++++++++++++++++++++++++++++++++", next_seat
		return next_seat

	def assign_role(self):
		number      = 0
		dealer      = -1
		small_blind = -1
		big_blind   = -1
		index       = (self.current_dealer + 1) % len(self.seats)
		for counter in xrange(9):
			if not self.seats[index].is_empty():
				number += 1
				if dealer == -1:
					dealer = index
				elif small_blind == -1:
					small_blind = index
				elif big_blind == -1:
					big_blind   = index
					break
			index = (index + 1) % len(self.seats)

		if number == 2:
			big_blind   = small_blind
			small_blind = dealer

		self.current_dealer = dealer
		self.small_blind    = small_blind
		self.big_blind      = big_blind
		print "current_dealer: ",   dealer
		print "small_blind: ",      small_blind
		print "big_blind: ",        big_blind

#class Pot(object):
#    def __init__(owner_list, amount):
#        self.owner_list = owner_list
#        self.amount = amount

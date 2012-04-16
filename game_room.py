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
		self.seat_id = seat_id
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
		return "seat[%d], user[%d]" % (self.seat_id, self._user.id)
	def __repr__(self):
		return "seat[%d], user[%d]" % (self.seat_id, self._user.id)

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

		result['uid'] = self._user.id
		result['user'] = self._user.username
		result['status'] = self.status
		result['table_amount']  = self.table_amount
		result['player_stake']  = self.player_stake
		return result




class GameRoom(object):
	(GAME_WAIT,GAME_PLAY) = (0,1)
	(A_ALLIN,A_CALLSTAKE,A_RAISESTAKE,A_CHECK,A_DISCARDGAME,A_BIGBLIND,A_SMALLBLIND) = (1,2,3,4,5,6,7)

	(MSG_SIT,MSG_BHC,MSG_PHC,MSG_WINNER,MSG_NEXT,MSG_ACTION,MSG_PUBLIC_CARD,MSG_START,MSG_POT,MSG_STAND_UP,MSG_SHOWDOWN) \
				= ('sit','bhc','phc','winner','next','action','public','start','pot','standup','showdown')
	def __init__(self, room_id, owner, dealer, num_of_seats = 9, blind = 10,min_stake=100,max_stake=2000):
		self.room_id    = room_id
		self.owner      = owner
		self.status     = GameRoom.GAME_WAIT
		self.dealer     = dealer
		self.broadcast_key  = "broadcast_%s_%d.testing" % (self.dealer.exchange, self.room_id)
		self.audit_list     = []
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
		self.pot = {}
		self.num_of_checks = 0
		self.amount_limits = {}
		self.t = None
		self.ioloop = ioloop.IOLoop.instance()
		self.user_seat = {}
		self.min_stake = min_stake
		self.max_stake = max_stake
		self.raise_amount = blind
		self.big_blind_move = False
		self.inComplete_all_in_flag = False

		self.seats = [ Seat(x) for x in xrange(num_of_seats) ]

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
			card_list = [ str(card) for card in self.poker_controller.publicCard ]
			result['publicCard'] = card_list
			result['current_seat'] = self.current_seat

		result['seats'] = [ seat.to_listener() for seat in self.seats ]
		result['min_stake'] = self.min_stake
		result['max_stake'] = self.max_stake
		result['blind']     = self.blind
		result['timestamp'] = self.msg_count
		return result


	def broadcast(self,msg,msgType):
		self.msg_count += 1
		msg['timestamp'] = self.msg_count
		msg['msgType'] = msgType
		self.dealer.broadcast(self.broadcast_key, msg)

	def direct_message(self, msg, destination,msgType):
		self.msg_count += 1
		msg['timestamp'] = self.msg_count
		msg['msgType'] = msgType
		self.dealer.broadcast(destination, msg)

	def user_action(self,args):
		action          = args["action"]
		private_key     = args["private_key"]
		user_id         = args["user_id"]
		seat_no  = self.current_seat
		if self.is_valid_seat(user_id, seat_no) and self.is_valid_rights(action, seat_no):
			self.clearCountDown()
			seat = self.seats[seat_no]
			if action != GameRoom.A_RAISESTAKE:
				if action in self.amount_limits:
					broadcast_msg = {'action':action, 'seat_no':seat_no,'stake':seat.player_stake-self.amount_limits[action],\
							'table':seat.table_amount+self.amount_limits[action]}
				else:
					broadcast_msg = {'action':action, 'seat_no':seat_no,'stake':seat.player_stake,'table':seat.table_amount}
				self.broadcast(broadcast_msg,GameRoom.MSG_ACTION)
				self.actions[action](user_id)
			else:
				amount = int(args['amount'])
				broadcast_msg = {'action':action, 'seat_no':seat_no,'stake':seat.player_stake-amount,'table':seat.table_amount+amount}
				self.broadcast(broadcast_msg,GameRoom.MSG_ACTION)
				self.actions[action](user_id,amount)


			if self.status != GameRoom.GAME_WAIT:
				next_seat = self.seats[self.current_seat]
				self.broadcast({"seat_no":next_seat.seat_id,'rights':next_seat.rights,'amount_limits':self.amount_limits},GameRoom.MSG_NEXT)

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
		self.seats[seat_no].status = Seat.SEAT_WAITING
		self.occupied_seat += 1
		message = {'seat_no': seat_no, "info": self.seats[seat_no].to_listener()}
		self.broadcast(message,GameRoom.MSG_SIT)
		print len(filter(lambda seat: not seat.is_empty() and seat.player_stake != 0, self.seats))
		if len(filter(lambda seat: not seat.is_empty() and seat.player_stake != 0, self.seats)) == 2 and not self.t:
			timeout = 5
			self.t = self.ioloop.add_timeout(time.time() + timeout, self.start_game)
			msg = {'to':timeout }
			self.broadcast(msg,GameRoom.MSG_START)
		#	self.t = Timer(5, self.start_game)
		#	self.t.start()
		return ( True, "" )


	def start_game(self):
		self.status = GameRoom.GAME_PLAY
		self.poker_controller.start()
		self.assign_role()
		self.t = None

		#Distribute cards to each player
		seat_list = []
		for seat in self.seats:
			if seat.status != Seat.SEAT_EMPTY:
				seat.status = Seat.SEAT_PLAYING
				card_list   = [ str(card) for card in seat.handcards ]
				seat_list.append(seat.seat_id)

				msg_sent = {"dealer":self.current_dealer, "small_blind":self.small_blind,"big_blind": self.big_blind, "cards": card_list,"Cards in hand": card_list}
				self.direct_message(msg_sent,seat.get_private_key(),GameRoom.MSG_PHC)

		self.broadcast({"seat_list":seat_list},GameRoom.MSG_BHC) # HC for Have Card

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

		seat = self.seats[self.small_blind]
		broadcast_msg = {'action':GameRoom.A_SMALLBLIND, 'seat_no':seat.seat_id,'stake':seat.player_stake,'table':seat.table_amount}
		self.broadcast(broadcast_msg,GameRoom.MSG_ACTION)

		seat = self.seats[self.big_blind]
		broadcast_msg = {'action':GameRoom.A_BIGBLIND, 'seat_no':seat.seat_id,'stake':seat.player_stake,'table':seat.table_amount}
		self.broadcast(broadcast_msg,GameRoom.MSG_ACTION)

		next_seat = self.seats[self.current_seat]
		self.broadcast({"seat_no":next_seat.seat_id,'rights':next_seat.rights,'amount_limits':self.amount_limits},GameRoom.MSG_NEXT)

	def get_seat(self, user_id):
		if user_id in self.user_seat:
			return self.seats[self.user_seat[user_id]]
		else:
			return None
		#return filter(lambda seat: seat.get_user() != None and seat.get_user().id == user_id, self.seats)[0]

	def is_valid_seat(self, user_id, current_seat):
		request_seat = self.get_seat(user_id)
		if not request_seat:
			return False

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
			print "INVALID ACTION!", command
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

	def call_stake(self, user_id, amount = 0):
		print "CALL!"
		print "num_of_checks: ", self.num_of_checks
		self.num_of_checks = 0
		command = GameRoom.A_CALLSTAKE

		seat_no = self.current_seat
		if not self.inComplete_all_in_flag:
			amount = self.amount_limits[GameRoom.A_CALLSTAKE]

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
				elif self.check_next(seat_no) == self.big_blind and self.big_blind_move == False:
					self.current_seat = self.info_next(seat_no, [1,3,4,5])
					self.big_blind_move = True
				else:
					self.round_finish()
			else:
				self.current_seat = self.info_next(seat_no, [1,2,3,5])
		else:
			if self.same_amount_on_table():                 # all players have put down equal amount of money, next round
				self.round_finish()
			else:
				if self.inComplete_all_in_flag == False:
					self.current_seat = self.info_next(seat_no, [1,2,3,5])
				else:
					print "-----------sb before you has called all in---------------"
					if self.seats[self.check_next(seat_no)].player_stake >= self.min_amount:
						self.current_seat = self.info_next(seat_no, [2,5])      # cannot re-raise after sb's all-in
					else:
						self.current_seat = self.info_next(seat_no, [1,5])


	def raise_stake(self, user_id,  amount):
		print "RAISE!"
		print "num_of_checks: ", self.num_of_checks
		self.num_of_checks = 0
		self.big_blind_move= True
		amount          	= int(amount)
		command         	= 3
		seat_no         	= self.current_seat
		if self.is_proper_amount(amount, command):
			print "This is a proper amount"
			self.seats[seat_no].bet(amount)
			print "table amount for seat "+ str(seat_no) + ": " + str(self.seats[seat_no].table_amount)
			self.raise_amount 	= amount
			self.min_amount     = self.seats[seat_no].table_amount
			self.current_seat   = self.info_next(seat_no, [1, 2, 3, 5])
		else:
			print "RAISE INVALID AMOUNT OF MONEY! GET OUT OF HERE!!!!"
			self.discard_game(user_id)

	def check(self, user_id):
		print "CHECK!"
		print "flop_flag: ", self.flop_flag
		command = 4
		seat_no = self.current_seat
		player_list = filter(lambda seat: seat.status == Seat.SEAT_PLAYING, self.seats)
		self.min_amount = 0         # may cause bugs`
		if self.flop_flag == False:         #Before flop, sb. called check
			self.round_finish()
		else:
			self.num_of_checks += 1
			print "num_of_checks: ", self.num_of_checks
			if self.num_of_checks < len(player_list):
				self.current_seat = self.info_next(seat_no, [1,3,4,5])
			else:
				self.round_finish()

	def discard_game_timeout(self,user_id):
		# put before discard in order to send fold msg before the potential round/game finish msg
		seat = self.seats[self.current_seat]
		broadcast_msg = {'action':GameRoom.A_DISCARDGAME, 'seat_no':self.current_seat,'stake':seat.player_stake,'table':seat.table_amount}
		self.broadcast(broadcast_msg,GameRoom.MSG_ACTION)
		self.discard_game(user_id)

		next_seat = self.seats[self.current_seat]
		print "next seat no....................................................", next_seat.seat_id
		self.broadcast({"seat_no":next_seat.seat_id,'rights':next_seat.rights,'amount_limits':self.amount_limits},GameRoom.MSG_NEXT)

	def discard_game(self, user_id):
		print "FOLD!!"
		seat_no = self.current_seat
		print self.current_seat
		self.seats[seat_no].status = Seat.SEAT_WAITING  # set the status of this seat to empty
														# remove the player from player list
		user = self.seats[seat_no].get_user()           # get user info from database

		#TODO Database update
		user.stake += self.seats[seat_no].player_stake  # update user's stake

		if self.same_amount_on_table():
			print "finishing this round after folding!!"
			self.round_finish()
		else:
			print "I'm here!!!!!"
			self.current_seat = self.info_next(seat_no, [1,2,3,5])


	def all_in(self, user_id):
		print "FULL POWER! ALL INNNNNNNNN!!!!!!!!"
		print "num_of_checks: ", self.num_of_checks
		self.num_of_checks = 0
		command  = 1
		seat_no  = self.current_seat
		amount   = self.amount_limits[GameRoom.A_ALLIN]
		print "self.min_amount before all in: ", self.min_amount
		print "----------------",self.min_amount == amount + self.seats[seat_no].table_amount

		print "amount to be on table: ", amount + self.seats[seat_no].table_amount
		if 0 < amount + self.seats[seat_no].table_amount < self.min_amount:
			self.seats[seat_no].player_stake = 0
			self.seats[seat_no].table_amount += amount
			# self.seats[seat_no].status = Seat.SEAT_ALL_I
			if self.flop_flag == False:
				if self.same_amount_on_table(True):
					# At end of first round, small_blind and dealer are out of money
					if len(filter(lambda seat: seat.status == Seat.SEAT_PLAYING, self.seats)) < 2:
						self.round_finish()
					elif self.check_next(seat_no) == self.big_blind and self.big_blind_move == False:
						self.current_seat = self.info_next(seat_no, [1,3,4,5])
						self.big_blind_move = True
					else:
						self.round_finish()
				else:
					self.current_seat = self.info_next(seat_no, [1,2,3,5])
			else:
				if self.same_amount_on_table(True):                 # all players have put down equal amount of money, next round
					self.round_finish()
				else:
					if self.inComplete_all_in_flag == False:
						print "HERE HERE!"
						self.current_seat = self.info_next(seat_no, [1,2,3,5])
					else:
						print "-----------sb before you has called all in---------------"
						if self.seats[self.check_next(seat_no)].player_stake >= self.min_amount:
							self.current_seat = self.info_next(seat_no, [2,5])      # cannot re-raise after sb's all-in
						else:
							self.current_seat = self.info_next(seat_no, [1,5])


		elif self.min_amount == amount + self.seats[seat_no].table_amount:
			print "going to call stake"
			self.call_stake(user_id)
		elif self.min_amount < amount + self.seats[seat_no].table_amount <= 2 * self.min_amount - self.seats[seat_no].table_amount:
			#self.seats[seat_no].status = Seat.SEAT_ALL_IN
			self.call_stake(user_id,  amount)
			self.inComplete_all_in_flag = True
		else:
			#self.seats[seat_no].status = Seat.SEAT_ALL_IN
			self.raise_stake(user_id, amount)



	def info_next(self, current_position, rights):
		next_seat = self.check_next(current_position)
		self.seats[next_seat].rights = rights
		callback = functools.partial(self.discard_game_timeout,self.seats[next_seat].get_user().id)
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
		print player_list

		for seat in player_list:
			print "player names: =============:", seat.get_user().username
			if seat.table_amount == self.min_amount and self.num_of_checks == 0:
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
		player_list = filter(lambda seat: seat.table_amount > 0, self.seats)
		playing_list = filter(lambda seat: seat.status == Seat.SEAT_PLAYING, self.seats)
		print "-----------no more stake------------"
		print self.no_more_stake()
		print "__________len(playing_list)_________"
		print len(playing_list)
		print "_____len(public card)---------------"
		print len(self.poker_controller.publicCard)


		if self.no_more_stake() or len(playing_list) < 2 or len(self.poker_controller.publicCard) == 5:
			print "GAME FINISHED!!!"
			if len(self.poker_controller.publicCard) < 3:
				self.poker_controller.getFlop()
				self.poker_controller.getOne()
				self.poker_controller.getOne()
				card_list = [str(card) for card in self.poker_controller.publicCard]
				broadcast_msg = {"cards": card_list}
				self.broadcast(broadcast_msg, GameRoom.MSG_PUBLIC_CARD)
			elif len(self.poker_controller.publicCard) == 3:
				self.poker_controller.getOne()
				self.poker_controller.getOne()
				card_list = [ str(card) for card in self.poker_controller.publicCard ]

				broadcast_msg = {'cards':card_list}
				self.broadcast(broadcast_msg,GameRoom.MSG_PUBLIC_CARD)
			elif len(self.poker_controller.publicCard) == 4:
				self.poker_controller.getOne()

			print "We have a winner!"
	#		print self.poker_controller.publicCard
			self.create_pot(player_list)
			player_list = filter(lambda seat: seat.status == Seat.SEAT_PLAYING or seat.status == Seat.SEAT_ALL_IN, self.seats)

			self.broadcast_pot()

#			self.poker_controller.get_winner()
			winner_dict = {}
			msg_dict 	= {}
			ante_dict = self.distribute_ante()
			winner_dict = {k:v for k, v in ante_dict.iteritems() if v > 0} #filter(lambda seat: winner_dict[seat] != 0, ante_dict)
			print "winner_dict: ", winner_dict
			if len(player_list) > 1:
				for seat in player_list:
					card_list = [str(card) for card in seat.handcards]
					if seat in winner_dict.keys():
						seat.player_stake += winner_dict[seat]
						pot = [amount["pid"] for users, amount in self.pot.iteritems() if seat._user.id in users]
						msg_dict[seat._user.id] = {"isWin":True,"earned":winner_dict[seat],"pot": pot, "stake": seat.player_stake, "handcards": card_list}
					else:
						msg_dict[seat._user.id] = {"isWin":False, "stake":seat.player_stake, "handcards": card_list}
			else:
				card_list = [str(card) for card in winner_dict.keys()[0].handcards]
				pot = [amount["pid"] for users, amount in self.pot.iteritems() if winner_dict.keys()[0]._user.id in users]
				winner_dict.keys()[0].player_stake += winner_dict[winner_dict.keys()[0]]
				msg_dict[playing_list[0]._user.id] = {"isWin":True,"earned":winner_dict[winner_dict.keys()[0]],"pot": pot, "stake": winner_dict.keys()[0].player_stake, "handcards": card_list}
			self.broadcast(msg_dict ,GameRoom.MSG_WINNER)
			print msg_dict
			self.status = GameRoom.GAME_WAIT
			self.dispose_and_restart()
			#sys.exit()
		else:
			print "length of playing list: ", len(playing_list)
			print "number of checks: ", self.num_of_checks
			self.min_amount = self.blind/2
			self.raise_amount = self.blind/2
			self.inComplete_all_in_flag = False

			if self.flop_flag == False:
				self.poker_controller.getFlop()
				self.flop_flag = True
			else:
				self.poker_controller.getOne()
			card_list = [ str(card) for card in self.poker_controller.publicCard ]
			self.current_seat = self.info_next(self.current_dealer, [1,3,4,5])
			broadcast_msg = {'cards':card_list}
			self.broadcast(broadcast_msg, GameRoom.MSG_PUBLIC_CARD)
			if len(playing_list) != self.num_of_checks:
				self.create_pot(player_list)
				self.broadcast_pot()
			self.num_of_checks = 0
			return

	def broadcast_pot(self):
		pot_info = [ (users,info) for users,info in self.pot.iteritems() ]
		pot_msg = {'pot': pot_info}
		self.broadcast(pot_msg, GameRoom.MSG_POT)

	def distribute_ante(self):
		ante_dict = {}
		rank_list = self.poker_controller.rank_users()
		print rank_list
		for i in xrange(len(rank_list)):
			print "rank list"
			for item in rank_list[i]:
				print item.get_user().id;

			for owner, ante in self.pot.iteritems():
				ante = ante["amount"]
				share_list = filter(lambda seat: seat.get_user().id in owner and seat.status != Seat.SEAT_WAITING, rank_list[i])
				for user in share_list:
					if user in ante_dict:
						ante_dict[user] += math.floor(ante/len(share_list))
					else:
						ante_dict[user] = math.floor(ante/len(share_list))

				if len(share_list) > 0 :
					pass
					self.pot[owner]["amount"] = 0
				else:
					pass
					#raise Exception("!!!");

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
			player_list[x].table_amount -= min_bet
			print ":::::::::::::::::: ", player_list[x].table_amount
			if player_list[x].status == Seat.SEAT_PLAYING or player_list[x].status == Seat.SEAT_ALL_IN:
				pot_owner.append(player_list[x].get_user().id)
				print ":::::::::::::::::: ", player_list[x].get_user().id

		pot_owner = tuple(pot_owner)
		if pot_owner not in self.pot:
			self.pot[pot_owner] = {"amount":0,"pid":len(self.pot)}

		self.pot[pot_owner]["amount"] += min_bet * len(player_list)

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

		min_amount = self.min_amount - self.seats[seat_no].table_amount
		if GameRoom.A_CALLSTAKE in self.seats[seat_no].rights:
			if self.seats[seat_no].player_stake < min_amount:
				self.seats[seat_no].rights.remove(GameRoom.A_CALLSTAKE)
			else:
				self.amount_limits[GameRoom.A_CALLSTAKE] = min_amount
		elif GameRoom.A_CALLSTAKE in self.amount_limits:
			del self.amount_limits[GameRoom.A_CALLSTAKE]

		min_amount = 2 * self.raise_amount
		if GameRoom.A_RAISESTAKE in self.seats[seat_no].rights:
			if self.seats[seat_no].player_stake < min_amount:
				self.seats[seat_no].rights.remove(GameRoom.A_RAISESTAKE)
			elif max_amount < min_amount:
				min_amount = max_amount
				self.amount_limits[GameRoom.A_RAISESTAKE] = (min_amount, max_amount)
			else:
				self.amount_limits[GameRoom.A_RAISESTAKE] = (min_amount, max_amount)
		elif GameRoom.A_RAISESTAKE in self.amount_limits:
			del self.amount_limits[GameRoom.A_RAISESTAKE]

		if GameRoom.A_ALLIN in self.seats[seat_no].rights:
			self.amount_limits[GameRoom.A_ALLIN] = min(self.seats[seat_no].player_stake, max_amount)

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

	def dispose_and_restart(self, blind = 10, min_stake=100, max_stake=2000):
		self.blind = blind
		self.min_amount = 0
		self.flop_flag = False
		self.pot = {}
		self.num_of_checks = 0
		self.amount_limits = {}
		self.t = None
		self.min_stake = min_stake
		self.max_stake = max_stake
		self.raise_amount = blind
		self.big_blind = False
		player_list = filter(lambda seat: not seat.is_empty() and seat.player_stake != 0, self.seats)
		go_away_list = filter(lambda seat: not seat.is_empty() and seat.player_stake == 0, self.seats)
		for seat in player_list:
			seat.status = Seat.SEAT_WAITING
		for seat in go_away_list:
			self.stand_up(seat.get_user().id)
		if len(player_list) >= 2 and not self.t:
			timeout = 5
			self.t = self.ioloop.add_timeout(time.time() + timeout, self.start_game)
			msg = {'to':timeout }
			self.broadcast(msg,GameRoom.MSG_START)

	def stand_up(self, user_id):
		for seat in self.seats:
			if not seat.is_empty() and user_id == seat.get_user().id:
				seat.status = Seat.SEAT_EMPTY
				print "broadcasting standup msg"
				standup_msg = {"seat no": seat.seat_id, "user_id": user_id}
				self.broadcast(standup_msg, GameRoom.MSG_STAND_UP)
		self.audit_list.append({"user": user_id})

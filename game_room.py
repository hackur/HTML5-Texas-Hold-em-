import time
from threading import Timer
import poker_controller

class Seat(object):
	(SEAT_EMPTY,SEAT_WAITING,SEAT_PLAYING) = (0,1,2)

	def __init__(self):
		self._user = None
		self._cards = None
		self._inAmount = 0
		self._status = Seat.SEAT_EMPTY
		self._direct_key = None
		self.combination = []
		self.handcards = []
		pass

	def is_empty(self):
		return self._status == Seat.SEAT_EMPTY

	def sit(self, user, direct_key):
		self._user = user
		self._status = Seat.SEAT_WAITING
		self._direct_key = direct_key

	def get_direct_key(self):
		return self._direct_key

class GameRoom(object):
	(GAME_WAIT,GAME_PLAY) = (0,1)
	def __init__(self, room_id, owner, dealer, num_of_seats = 9):
		self.room_id		= room_id
		self.owner			= owner
		self.status			= GameRoom.GAME_WAIT
		self.dealer			= dealer
		self.broadcast_key	= "broadcast_%s_%d.testing" %(self.dealer.exchange, self.room_id)
		self.player_list	= []
		# self.waiting_list	= []
		self.audit_list		= []
		self.seats			= []
		for x in xrange(num_of_seats):
			self.seats.append(Seat())
		self.occupied_seat	= 0
		self.suit = ["DIAMOND", "HEART", "SPADE", "CLUB"]
		self.face = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
		self.msg_count= 0

	def broadcast(self,msg):
		self.msg_count += 1
		msg['timestamp'] = self.msg_count
		print msg["timestamp"]
		self.dealer.broadcast(self.broadcast_key, msg)

	def sit(self, player, seat_no, direct_key):
		print "direct_key.........................................", direct_key
		seat_no = int(seat_no)
		print "seat request =>%d\n" % (seat_no)
		if seat_no > len(self.seats):
			return (False, "Seat number is too large: %s we have %s" % (seat_no,len(self.seats)))
		if not self.seats[seat_no].is_empty():
			return (False, "Seat Occupied")
		self.seats[seat_no].sit(player, direct_key)

		self.player_list.append(self.seats[seat_no])

		self.occupied_seat += 1

		msg_broadcast	= {'status':'success', 'no_player': self.occupied_seat}
		self.broadcast(msg_broadcast)

		if self.occupied_seat == 2:
			t = Timer(5, self.start_game, args=[self.player_list])
			t.start()
		return (True, "")

	
	def start_game(self, players):
		self.status = GameRoom.GAME_PLAY
		table_card_list = []
		game = poker_controller.PokerController(players)
		game.getFlop()

		for card in game.publicCard:
			table_card_list.append(str(self.suit[card.symbol])+"/"+str(self.face[card.value-2]))
		
		msg_broadcast	= {"Cards on Table": str(table_card_list)}
		self.broadcast(msg_broadcast)	

		for seat in players:
			# print "self.get_direct_key ............................. ", seat.get_direct_key()
			print str(seat._user.username) + ": "
			for cards in seat.handcards:
				# print str(self.suit[cards.symbol])+"/"+str(self.face[cards.value-2])+" ",
				card = str(self.suit[cards.symbol])+"/"+str(self.face[cards.value-2])
				msg_sent = {"Cards": card}
				self.dealer.broadcast(seat.get_direct_key(), msg_sent)

	def add_audit(self, player):
		self.audit_list.append(player)

	def set_status(self,status):
		self.status = status

from threading import Timer

class Seat(object):
	(SEAT_EMPTY,SEAT_WAITING,SEAT_PLAYING) = (0,1,2)

	def __init__(self):
		self._user = None
		self._cards = None
		self._inAmount = 0
		self._status = Seat.SEAT_EMPTY
		self.combination = []
		self.handcards = []
		pass

	def is_empty(self):
		return self._status == SEAT_EMPTY

	def sit(self, user):
		self._user = user
		self._status = SEAT_WAITING


class GameRoom(object):
	(GAME_WAIT,GAME_PLAY) = (0,1)
	def __init__(self, room_id, owner, dealer, num_of_seats = 9):
		self.room_id = room_id
		self.owner = owner
		self.status = GAME_WAIT
		self.broadcast_key = "broadcast_" + dealer.exchange + "_" + self.room_id + "_" + "*"
		self.player_list = []
		self.waiting_list= []
		self.audit_list = []
		self.seats		=  []
		for x in xrange(num_of_seats):
			self.seats.append(Seat())
		self.occupied_seat = 0

	def sit(self,player,seat_no):
		if seat_no > len(self.seats):
			return (False, "Seat number is too large")
		if not self.seats[seat_no].is_empty():
			return (False, "Seat Occupied")
		self.seats[seat_no].sit(player)
		self.occupied_seat += 1
		if self.occupied_seat == 2:
			t = Timer(5, start_game)
			t.start()
		return (True, "")

	def start_game(self)

	def add_audit(self, player):
		self.audit_list.append(player)

	def set_status(self,status):
		self.status = status

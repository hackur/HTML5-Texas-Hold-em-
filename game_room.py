
class Seat(object):
	(SEAT_EMPTY,SEAT_WAITING,SEAT_PLAYING) = (0,1,2)

	def __init__(self):
		self._user = None
		self._cards = None
		self._inAmount = 0
		self._status = Seat.SEAT_EMPTY
		pass


class GameRoom(object):
	(GAME_WAIT,GAME_PLAY) = (0,1)
	def __init__(self,room_id,owner):
		self.room_id = room_id
		self.owner = owner
		self.status = GAME_WAIT
		self.player_list = []
		self.waiting_list= []
		self.audit_list = []
		self.seats		=  []
		for x in xrange(num_of_seats):
			self.seats.append(Seat())

	def sit(self,player):
		pass

	def set_status(self,status):
		self.status = status

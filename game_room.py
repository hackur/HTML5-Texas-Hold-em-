
class GameRoom(object):
	(GAME_WAIT,GAME_PLAY) = (0,1)
	def __init__(self,room_id,owner):
		self.room_id = room_id
		self.owner = owner
		self.status = GAME_WAIT
		self.player_list = []
		self.waiting_list= []
		self.audit_list = []

	def add_player(self,player):
		self.player_list.append(player)

	def set_status(self,status):
		self.status = status

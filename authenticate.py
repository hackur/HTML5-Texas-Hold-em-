import json
from database import *
def authenticate(functor):
	def _authenticate(self):
		if 'user_id' not in self.session:
			self.write(json.dumps('unauthenticated'))
			self.finish()
			return

		self.db_connection	= DatabaseConnection()
		self.db_connection.start_session()
		self.session['user'] = self.db_connection.query(User).filter_by(id = self.session['user_id']).one()
		self.db_connection.commit_session()
		functor(self)
		self.db_connection.close()
	_authenticate.__name__ = functor.__name__
	return _authenticate


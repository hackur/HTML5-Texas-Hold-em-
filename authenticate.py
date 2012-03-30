import json
from database import *
def authenticate(functor):
	def _authenticate(self):
		#if 'user' not in self.session:
		if False and 'user' not in self.session:
			self.write(json.dumps({'status':'failed', 'content':'unauthenticated'}))
			self.finish()
			return
		db_connection	= DatabaseConnection()
		db_connection.start_session()
		#self.session['user'] = db_connection.query(User).filter_by(id = self.session['user'].id).one()

		self.session['user'] = db_connection.query(User).filter_by(username = self.get_argument('username')).one()
		db_connection.commit_session()
		functor(self)
	_authenticate.__name__ = functor.__name__
	return _authenticate


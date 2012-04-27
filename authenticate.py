import json
from database import *
def authenticate(functor):
	def _authenticate(self):
		if not 'user_id' in self.session:
			print "REDIRECT!!!!!!!!!!!!"
			self.redirect("/static/index/index.html")
			return

		self.db_connection	= DatabaseConnection()
		self.db_connection.start_session()
		user = self.db_connection.query(User).filter_by(id = self.session['user_id']).first()
		if not user:
			self.redirect("/static/index/index.html")
			del self.session['user_id']
			return

		self.user = user
		self.session['user']  = user
		self.db_connection.commit_session()
		functor(self)
		self.db_connection.close()
	_authenticate.__name__ = functor.__name__
	return _authenticate


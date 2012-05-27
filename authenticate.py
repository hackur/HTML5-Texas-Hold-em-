import json
from database import *
def authenticate(functor):
	def _authenticate(self,*arg):
		if not 'user_id' in self.session:
			self.redirect("/static/index/index.html")
			return

		user =User.find(_id = self.session['user_id'])
		if not user:
			del self.session['user_id']
			self.redirect("/static/index/index.html")
			return

		self.user = user
		functor(self,*arg)
	_authenticate.__name__ = functor.__name__
	return _authenticate


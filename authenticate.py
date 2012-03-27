import json
def authenticate(functor):
	def _authenticate(self):
		if 'user' not in self.session:
			self.write(json.dumps({'status':'failed', 'content':'unauthenticated'}))
			self.finish()
			return
		functor(self)
	_authenticate.__name__ = functor.__name__
	return _authenticate

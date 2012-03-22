import os
import sys
import pickle
import time
import hashlib
import logging
import uuid
logger =logging.getLogger('tornado session')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
def LOG(s):
    logger.info(s)

class SessionData():
    def __init__(self, id = None):
        self._data = {}
        self._id = id
        self._is_updated = False
        self._last_time = time.time()
    def get(self,key):
        ret = None
        try:
            ret = self._data[key]
        except:
            pass
        self._last_time = time.time()
        return ret

    def __getitem__(self, key):
        ret = None
	try:
	    ret = self._data[key]
	except:
	    pass
	self._last_time = time.time()
	return ret

    def set(self, key, value):
        self._data[key] = value
        self._is_updated = True
        self._last_time = time.time()
    def __setitem__(self, key, value):
        self._data[key] = value
	self._is_updated= True
	self._last_time = time.time()


    def get_id(self):
        return self._id

    def reset_update_status(self):
        self._is_updated = False

    def is_updated(self):
        return self._is_updated

class SessionManager():
    def __init__(self):
        self._data_pool = {}
    def write_session_data(self, id, data):
        self._data_pool[id] = data
    def read_session_data(self, id):
        if id in self._data_pool.keys():
            return self._data_pool[id]
        else:
            ret = SessionData(id)
            return ret

session_manager = SessionManager()

def session(function):
    def _session(*args, **kwargs):
        self = args[0]
        if not self.get_secure_cookie("sessionid"):
            LOG('oops! no session')
            newid = hashlib.md5(str(uuid.uuid1())).hexdigest()
            sessionid = newid
            self.set_secure_cookie("sessionid", sessionid)
        else:
            sessionid = self.get_secure_cookie("sessionid")
        obj = session_manager.read_session_data(sessionid)
        LOG('SESSIONID:' + sessionid)
        self.session = obj
        self.session.reset_update_status()
        res = function(*args, **kwargs)
        if self.session.is_updated():
            LOG('!!!got update' + ' ' + sessionid)
            session_manager.write_session_data(sessionid, self.session)
        else:
            LOG('no session operation')
            pass
        return res
    return _session

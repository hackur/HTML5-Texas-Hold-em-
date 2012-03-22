import tornado.ioloop
import tornado.web
import tornado.options
import tornado.database
import re
import UserModel
from UserModel import *

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.orm import sessionmaker


'''
def ConnectDB():
    engine=create_engine("mysql://root:123@localhost/test")
    Base=declarative_base()
    connection=engine.connect()
    sessiion=sessionmaker(bind=engine)()
    return session
'''

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write("Hello, world")
        self.render("index.html")

    def post(self):
        name=self.get_argument("name") or "damn"
        pwd=self.get_argument("pwd") or "it"
        self.write(name+"--"+pwd)

class NewUserHandler(tornado.web.RequestHandler):
    def post(self):
        name=self.get_argument("name") or "damn"
        pwd=self.get_argument("pwd") or "it"
        u=User(username=name,password=pwd)
        #indicate other basic things here
        session.add(u)
        session.commit()
        #self.write(session.query(User).first())

class showAllHandler(tornado.web.RequestHandler):
    def get(self):
        print session.query(User).all()
        #self.write(len(session.query(User).all()))

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/new",NewUserHandler),
    (r"/showAll",showAllHandler)
])

if __name__ == "__main__":
    application.listen(8889)
    tornado.ioloop.IOLoop.instance().start()

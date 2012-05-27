
import tornado.web
import tornado.template

class HTMLFileHandler(tornado.web.RequestHandler):
    def get(self,filename):
        self.render("static/%s" % filename)

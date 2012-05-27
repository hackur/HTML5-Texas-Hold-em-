
import tornado.web
import tornado.template

class HTMLFileHandler(tornado.web.RequestHandler):
    def get(self,filename):
        debug = self.application.settings['debug']
        self.render("static/%s" % filename,debug=debug)

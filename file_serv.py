import pika
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.process
import tornado.websocket
from pika.adapters.tornado_connection import TornadoConnection
import os
import logging
from filehandler import HTMLFileHandler
PORT = 8888


def main():
    parser = argparse.ArgumentParser(description='Server...')
    parser.add_argument('--port','-P',default=8888,type=int)
    parser.add_argument('--debug-mode','-D',default=1,type=int)
    args = parser.parse_args()
    PORT = args.port

    num_of_process = 1
    if args.debug_mode == 1:
        debug = True
        num_of_process = 1
    else:
        debug = False
    tornado.locale.load_translations("translation")

    settings = {
            "debug": debug,
            'cookie_secret':"COOKIESECRET=ajbdfjbaodbfjhbadjhfbkajhwsbdofuqbeoufb",
            "static_path2": os.path.join(os.path.dirname(__file__), "static"),
            "uploaded_image_path": os.path.join(os.path.dirname(__file__), "uploads"),
    }



    # Set our pika.log options
    pika.log.setup(color=debug)
    logging.info("Starting Tornado HTTPServer on port %i" % PORT)
    application = tornado.web.Application([
        (r"/?$", HTMLFileHandler),
        ], **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.bind(PORT)
    #http_server.start(8)
    http_server.start(num_of_process)



    #If we publishing message's speed is much faster than msg processed.
    # "TCP back pressure" will happen, set a huge multiplier to avoid that

    ioloop = tornado.ioloop.IOLoop.instance()

    ioloop.start()


import argparse
if __name__ == '__main__':
    main()




#!/usr/bin/env python
# encoding: utf-8

""" Prototype for specator network topology. """

import os.path

import tornado.web
import tornado.websocket
from tornado.options import define, options
import zmq
import json
from zmq.eventloop.ioloop import ZMQIOLoop
from zmq.eventloop.zmqstream import ZMQStream

from updatesockethandler import UpdateSocketHandler
define("port", default=8888, help="run on the given port", type=int)
define("agents_port", default=5555, help="agents will connect to this port.", type=int)


class Application(tornado.web.Application):

    def __init__(self, agents_port):
        """
        Main spectator Tornado application.

        Data are exchanged from components in three ways:
            - Web: The application is a full web app and respond to GET request for
            rendering a static web page.
            - WebSocket: The application push back data to all connected web client
            through a web socket.
            - Push/Pull message pattern: Receive data from all connected
            monitoring agents through a zmq `push/pull` topology.

        :param agents_port The tcp port onto which agents will connect
        """
        # Create web server
        handlers = [
            (r"/", MainHandler),
            (r"/updatesocket", UpdateSocketHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind("tcp://127.0.0.1:%d" % agents_port)
        self.stream = ZMQStream(socket, io_loop=ZMQIOLoop.current())
        self.stream.on_recv(self.get_messages)

    def shutdown(self):
        """ Close all opened zmq sockets. """
        self.stream.close()

    @staticmethod
    def get_messages(messages):
        """
        ZMQStream callbakck managing the messages receptions from all connected
        agents.

        :param messages List of json encoded messages
        """
        for msg in messages:
            msg = json.loads(msg)
            UpdateSocketHandler.publish_message(msg['message'])


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html", messages=UpdateSocketHandler.cache)


def main():
    """ Start Spectator application server through command line. """
    tornado.options.parse_command_line()
    io_loop = ZMQIOLoop.instance()
    app = Application(options.agents_port)
    app.listen(options.port)
    print "Spectator server is started..."
    io_loop.start()


if __name__ == "__main__":
    main()

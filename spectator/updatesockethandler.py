#!/usr/bin/env python
# encoding: utf-8


import logging
import uuid
import json

import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket


class UpdateSocketHandler(tornado.websocket.WebSocketHandler):

    """ Handle pushing updated message to connected clients.

    New monitoring updates are pushed through this websocket.
    """
    waiters = set()
    cache = []
    cache_size = 200

    def open(self):
        UpdateSocketHandler.waiters.add(self)

    def on_close(self):
        UpdateSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, update):
        cls.cache.append(update)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, update):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(update)
            except:
                logging.error("Error sending message", exc_info=True)

    @staticmethod
    def make_message(message):
        """ Wrap message in a delivery dictonary.

        :message: A string or a dict representation of the message to send.
        :returns: A dictionnary with two keys('id' and 'body').

        """
        message = {
            "id": str(uuid.uuid4()),
            "body": json.dumps(message),
        }
        return message

    @classmethod
    def publish_message(cls, message):
        """ Publish a message via WebSocket to all connected client.

        :message: A string or a dict representation of the message to send.
        """
        # Wrap message
        message = cls.make_message(message)
        # Add to cache so new clients get the full history
        cls.update_cache(message)

        # Push the message to all waiters
        for waiter in cls.waiters:
            try:
                message["html"] = tornado.escape.to_basestring(
                    waiter.render_string("message.html", message=message))
                # note: `write_message` encodes message to json
                waiter.write_message(message)
            except:
                logging.error("Error sending message", exc_info=True)

#!/usr/bin/env python
# encoding: utf-8


import logging
import uuid

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

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

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
        """ Render a deliverable message.

        :message: String with the message to send.
        :returns: A dictionnary with two keys('id' and 'body').

        """
        message = {
            "id": str(uuid.uuid4()),
            "body": unicode(message)
        }
        return message

    @classmethod
    def publish_message(cls, message):
        """ Publish a message via WebSocket to all connected client.

        :message: A string instance.
        """
        # Add to cache so new clients get the full history
        message = cls.make_message(message)
        cls.update_cache(message)

        # Push the message to all waiters
        for waiter in cls.waiters:
            try:
                # Inject html section in message for client
                message["html"] = tornado.escape.to_basestring(
                    waiter.render_string("message.html", message=message))
                waiter.write_message(message)
            except:
                logging.error("Error sending message", exc_info=True)

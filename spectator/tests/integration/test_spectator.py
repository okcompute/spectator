#!/usr/bin/env python
# encoding: utf-8

from multiprocessing import Process
from spectator.agent import main as agent
from spectator.app import main as app

from tornado.testing import AsyncTestCase
from tornado.websocket import websocket_connect


class SpectatorTest(AsyncTestCase):

    """Integration tests for the whole spectator workflow."""

    @classmethod
    def setUpClass(cls):
        super(SpectatorTest, cls).setUpClass()
        cls.app = Process(target=app)
        cls.app.start()
        cls.agent = Process(target=agent)
        cls.agent.start()
        cls.agents_port = 5555

    @classmethod
    def tearDownClass(cls):
        cls.app.terminate()
        cls.agent.terminate()
        super(SpectatorTest, cls).tearDownClass()

    def test_websocket(self):
        websocket_connect('ws://127.0.0.1:%s/updatesocket' %
                          8888,
                          io_loop=self.io_loop,
                          callback=self.stop)
        session = self.wait().result()

        session.read_message(self.stop)
        message = self.wait().result()
        self.assertTrue("body" in message)
        self.assertTrue("id" in message)

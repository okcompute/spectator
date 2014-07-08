#!/usr/bin/env python
# encoding: utf-8

import unittest
import json

import zmq

from spectator.agent import (
    Agent,
)

""" Functional tests for spectator agent. """


class SpectatorApplicationTest(unittest.TestCase):

    def setUp(self):
        super(SpectatorApplicationTest, self).setUp()

    def tearDown(self):
        super(SpectatorApplicationTest, self).tearDown()

    def test_send_update(self):
        agent = Agent("tcp://127.0.0.1:5555")

        # PULL zmq socket to simulate app receiving updates from agent
        # data
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind("tcp://127.0.0.1:5555")

        # Simulate one heartbeat from the periodic update
        agent.send_update()

        # Socket should receive an update message
        update = json.loads(socket.recv())
        self.assertTrue("cpu" in update)
        self.assertEqual(type(update["cpu"]), float)
        self.assertTrue("memory" in update)
        self.assertEqual(type(update["memory"]), list)
        self.assertEqual(len(update["memory"]), 2)
        self.assertEqual(type(update["memory"][0]), float)
        self.assertEqual(type(update["memory"][1]), float)

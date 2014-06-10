#!/usr/bin/env python
# encoding: utf-8

import unittest
from mock import (
    MagicMock,
    call,
)

from spectator.app import (
    UpdateSocketHandler,
)


class TestUpdateSocketHandler(unittest.TestCase):

    """Functional and unit tests for spectator web socket handler"""

    def setUp(self):
        UpdateSocketHandler.waiters = set()
        UpdateSocketHandler.cache = []

    def tearDown(self):
        UpdateSocketHandler.waiters = set()
        UpdateSocketHandler.cache = []

    def test_make_message(self):
        """ Validate returned message has a body and and unique id."""
        message = UpdateSocketHandler.make_message("my message")
        self.assertEqual(type(message['id']), str)
        self.assertEqual(len(message['id']), 32 + 4)  # note: normal length of a uuid
        self.assertEqual(message['body'], "my message")

    def test_publish_message_cache_message(self):
        """ Test `pusblish_message` cache the messages received. """
        self.assertEqual(len(UpdateSocketHandler.cache), 0)
        UpdateSocketHandler.publish_message("my message")
        self.assertEqual(len(UpdateSocketHandler.cache), 1)
        self.assertEqual(UpdateSocketHandler.cache[0]['body'], "my message")

    def test_publish_message(self):
        """ Test `pusblish_message` write message to a waiter in waiters list.
        """
        # Mock a waiter
        waiter = MagicMock()
        waiter.render_string.return_value = u"test"
        UpdateSocketHandler.waiters.add(waiter)

        # Call our tested method
        UpdateSocketHandler.publish_message("my message")

        self.assertIn(call.write_message, waiter.mock_calls)
        self.assertEqual(len(UpdateSocketHandler.cache), 1)
        self.assertEqual(UpdateSocketHandler.cache[0]['body'], "my message")

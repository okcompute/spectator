#!/usr/bin/env python
# encoding: utf-8

#
# Monitoring agent

import zmq


class Agent(object):

    """
    Monitoring agent sending data to master application. This agent gather
    resource usage information from host computer for a specific process and
    returns the data via zeromq to the connected master.
    """

    def __init__(self, url, context=None):
        self.context = context or zmq.Context()

        #  Socket to talk to server
        print("Connecting to server...")
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect(url)

    def send_message(self, message):
        """Send a message to main application via zmq push socket.

        :param message: A string representing the message to be sent

        """
        self.socket.send_json(message)


def main():
    Agent("tcp://127.0.0.1:5555")


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# encoding: utf-8

import zmq
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback

from osx import ProcessMonitor

# We send state information every heartbeat
HEARTBEAT = 1000          # In msecs


class Agent(object):

    """
    Monitoring agent sending data to master application. This agent gather
    resource usage information from host computer for a specific process and
    returns the data via zeromq to the connected master.
    """

    def __init__(self, url, context=None):
        # The monitoring instance
        # TODO: Pass a PID to monitor instead of monitoring current process
        self.monitor = ProcessMonitor()

        self.context = context or zmq.Context()

        #  Socket to talk to server
        print("Connecting to server...")
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect(url)

        # setup basic reactor events
        self.loop = IOLoop.instance()
        self.heartbeat = PeriodicCallback(self.send_update, HEARTBEAT, self.loop)
        self.heartbeat.start()

    def send_update(self):
        """Send monitoring update to main application via zmq push socket.

        """
        memory_usage = self.monitor.memory_usage()
        cpu_usage = self.monitor.cpu_usage()
        message = {'memory': memory_usage,
                   'cpu': cpu_usage,
                   }
        self.socket.send_json(message)


def main():
    ioloop = IOLoop.instance()
    Agent("tcp://127.0.0.1:5555")
    print "Starting Specator agent..."
    ioloop.start()


if __name__ == '__main__':
    main()

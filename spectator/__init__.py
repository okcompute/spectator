import heapq
import itertools
import logging
import time


def generate_intervals(clock, now=None):
    old = clock()
    while True:
        new = clock()
        yield new - old
        old = new


def local_stopwatch():
    """Generate time elapsed between iterations."""
    return generate_intervals(time.clock)


def generate_deadlines(start, period, skip=0):
    while True:
        if skip > 0:
            skip -= 1
        else:
            yield start
        start += period


class Scheduler(object):
    """Efficient clock-agnostic tool to defer actions."""

    def __init__(self):
        self.queue = []
        self.index = itertools.count(start=1)

    def next_deadline(self):
        """Quickly determine when the next action is due.

        The ``AllSeeingEye`` uses this to efficiently determine how long to
        wait until the next iteration of ``elapsed()``, all but avoiding the
        need for polling."""
        if len(self.queue) < 1:
            return None
        return self.queue[0][0]

    def schedule(self, deadline, action):
        """Defer ``action`` for execution at ``deadline``.

        When ``deadline`` is reached, ``action`` will be queued into the
        ``elapsed`` iterable so that the caller can use the action."""
        heapq.heappush(self.queue, (deadline, next(self.index), action))

    def elapsed(self, now):
        """Enumerate all actions who'se deadlines elasped before ``now``.

        Actions are enumerated in order of elasped deadline, and in insertion
        order for equal deadlines, guaranteeing FIFO-like behavior of deferred
        actions, all the while respecting time constraints."""
        while len(self.queue) > 0 and now >= self.queue[0][0]:
            yield heapq.heappop(self.queue)[2]


class AllSeeingEye(object):
    """Efficient monitor aggregation."""

    def __init__(self, clock=time.clock):
        self.monitors = {}
        self.scheduler = Scheduler()
        self.clock = clock

    def time_to_wait(self):
        """Time to wait, in seconds."""
        deadline = self.scheduler.next_deadline()
        if deadline is None:
            return None
        return deadline - self.clock()

    def watching(self, label):
        return label in self.monitors

    def watch(self, label, monitor, period, notify):
        """Register for polling"""
        if self.watching(label):
            raise KeyError('Already watching "%s".' % label)
        deadlines = generate_deadlines(self.clock(), period, skip=1)

        def action():
            try:
                # Auto-cancel when desired.
                if notify(monitor()):
                    self.scheduler.schedule(next(deadlines), action)
                else:
                    del self.monitors[label]
            except Exception:
                logging.exception('Polling "%s".', label)
        self.scheduler.schedule(next(deadlines), action)
        self.monitors[label] = monitor

    def blink(self):
        """Dispatch actions for all ready monitors."""
        count = 0
        for action in self.scheduler.elapsed(self.clock()):
            action()
            count += 1
        return count

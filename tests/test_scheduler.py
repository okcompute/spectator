from datetime import datetime, timedelta
from functools import wraps
from itertools import count, repeat
from mock import patch
from nose.tools import (
    eq_,
    assert_greater_equal,
    assert_less,
)

from spectator import (
    AllSeeingEye,
    generate_deadlines,
    generate_intervals,
    local_stopwatch,
    Scheduler,
)


def count_calls(f):
    """Counts calls to decorated function."""
    @wraps(f)
    def _(*args, **kwds):
        _.calls += 1
        return f(*args, **kwds)
    _.calls = 0
    return _


def test_interval_generator():
    """Interval generation works with various types of clocks."""
    def as_function(sequence):
        sequence = iter(sequence)
        return lambda: next(sequence)
    # Counter yields step at each interval.
    interval = generate_intervals(as_function(count()))
    for i in range(100):
        eq_(next(interval), 1)
    # Repeater yields 0 at each interval.
    interval = generate_intervals(as_function(repeat(5)))
    for i in range(100):
        eq_(next(interval), 0)
    # Datetime yields timedelta objects.
    interval = generate_intervals(datetime.now)
    for i in range(100):
        assert_greater_equal(next(interval).total_seconds, 0)


def test_deadline_generator():
    """Deadline generation works with various types of clocks."""
    # Use counter as clock.
    deadline = generate_deadlines(0, 1)
    eq_(next(deadline), 0)
    eq_(next(deadline), 1)
    eq_(next(deadline), 2)
    eq_(next(deadline), 3)
    # Use date facilities as clock.
    today = datetime.today()
    deadline = generate_deadlines(today, timedelta(days=1))
    eq_(next(deadline), today)
    eq_(next(deadline), today + timedelta(days=1))
    eq_(next(deadline), today + timedelta(days=2))
    eq_(next(deadline), today + timedelta(days=3))


def test_deadline_generator_offset():
    """Deadline generation works with various types of clocks."""
    # Use date facilities as clock.
    today = datetime.today()
    deadline = generate_deadlines(today, timedelta(days=1), skip=2)
    eq_(next(deadline), today + timedelta(days=2))
    eq_(next(deadline), today + timedelta(days=3))
    eq_(next(deadline), today + timedelta(days=4))
    eq_(next(deadline), today + timedelta(days=5))


def test_local_stopwatch():
    """Local stopwatch measures wall-clock time."""
    with patch('time.clock') as clock:
        interval = local_stopwatch()
        clock.side_effect = [0.0, 0.0, 0.1, 0.2]
        next(interval)  # TODO: first interval always empty!
        assert_less(abs(0.1 - next(interval)), 0.005)
        assert_less(abs(0.1 - next(interval)), 0.005)


def test_scheduler_out_of_order_scheduling():
    """Events elapse in deadline order regardless of time of insertion."""
    scheduler = Scheduler()
    scheduler.schedule(4, 'qux')
    scheduler.schedule(1, 'foo')
    scheduler.schedule(3, 'meh')
    scheduler.schedule(2, 'bar')
    eq_(list(scheduler.elapsed(4)),
        ['foo', 'bar', 'meh', 'qux', ])


def test_scheduler_insertion_order():
    """Events with equal deadlines elapse in insertion order."""
    scheduler = Scheduler()
    scheduler.schedule(1, 'foo')
    scheduler.schedule(1, 'bar')
    scheduler.schedule(1, 'meh')
    scheduler.schedule(1, 'qux')
    eq_(list(scheduler.elapsed(1)),
        ['foo', 'bar', 'meh', 'qux', ])


def test_scheduler_next_deadline():
    """Caller can query next deadline at all times."""
    scheduler = Scheduler()
    eq_(scheduler.next_deadline(), None)
    scheduler.schedule(4, 'qux')
    scheduler.schedule(1, 'foo')
    scheduler.schedule(3, 'meh')
    scheduler.schedule(2, 'bar')
    eq_(scheduler.next_deadline(), 1)
    eq_(list(scheduler.elapsed(1)), ['foo', ])
    eq_(scheduler.next_deadline(), 2)
    eq_(list(scheduler.elapsed(2)), ['bar', ])
    eq_(scheduler.next_deadline(), 3)
    eq_(list(scheduler.elapsed(3)), ['meh', ])
    eq_(scheduler.next_deadline(), 4)
    eq_(list(scheduler.elapsed(4)), ['qux', ])
    eq_(scheduler.next_deadline(), None)


def test_all_seeing_eye_countdown():
    """Caller can countdown to execution of next action."""
    # Use monotonically increasing integer clock to avoid errors induced by
    # floating-point arithmetic precision.
    def clock():
        return clock.position
    clock.position = 0

    # Deadline is None when there is nothing to watch.
    eye = AllSeeingEye(clock)
    eq_(eye.time_to_wait(), None)

    # Model a few simple actions.
    def foo():
        pass
    foo.cancelled = False

    @count_calls
    def notify_foo(value):
        return not foo.cancelled  # automatically re-schedule.

    def bar():
        pass
    bar.cancelled = False

    @count_calls
    def notify_bar(value):
        return not bar.cancelled  # automatically re-schedule.

    # Perform a simple countdown.
    eye.watch('foo', foo, 2, notify_foo)
    eq_(eye.time_to_wait(), 2)
    clock.position += 1
    eq_(eye.time_to_wait(), 1)
    clock.position += 1
    eq_(eye.time_to_wait(), 0)
    eq_(eye.blink(), 1)
    eq_(notify_foo.calls, 1)
    eq_(notify_bar.calls, 0)
    eq_(eye.time_to_wait(), 2)


def test_all_seeing_eye_fair_queueing():
    """All seing eye exhibits fair queueing of tasks with same period."""
    # Use monotonically increasing integer clock to avoid errors induced by
    # floating-point arithmetic precision.
    def clock():
        return clock.position
    clock.position = 0

    @count_calls
    def notify(value):
        eq_(value, notify.expected_value)
        notify.expected_value = 1 - notify.expected_value
        return True  # never cancel it.
    notify.expected_value = 0

    # Model a few simple actions.
    @count_calls
    def foo():
        return 0

    @count_calls
    def bar():
        return 1

    # Deadline is None when there is nothing to watch.
    eye = AllSeeingEye(clock)
    eq_(eye.time_to_wait(), None)
    eye.watch('foo', foo, 2, notify)
    eye.watch('bar', bar, 2, notify)
    eq_(eye.time_to_wait(), 2)
    eq_(foo.calls, 0)
    eq_(bar.calls, 0)
    eq_(notify.calls, 0)

    # Round 1.
    clock.position += 2
    eq_(eye.blink(), 2)
    eq_(foo.calls, 1)
    eq_(bar.calls, 1)
    eq_(notify.calls, 2)

    # Round 2.
    clock.position += 2
    eq_(eye.blink(), 2)
    eq_(foo.calls, 2)
    eq_(bar.calls, 2)
    eq_(notify.calls, 4)

    # Round 3.
    clock.position += 2
    eq_(eye.blink(), 2)
    eq_(foo.calls, 3)
    eq_(bar.calls, 3)
    eq_(notify.calls, 6)


def test_all_seeing_eye_error_in_action():
    """Actions are never rescheduled when they crash."""
    def clock():
        return clock.position
    clock.position = 0

    @count_calls
    def notify(value):
        return True  # always reschedule.

    @count_calls
    def bad_action():
        raise KeyError('Accessing some dict key.')

    eye = AllSeeingEye(clock)
    eq_(eye.time_to_wait(), None)
    eq_(bad_action.calls, 0)
    eq_(notify.calls, 0)

    # Action crashes.
    eye.watch('bad_action', bad_action, 2, notify)
    eq_(eye.time_to_wait(), 2)
    clock.position += 2
    eq_(eye.blink(), 1)
    eq_(bad_action.calls, 1)
    eq_(notify.calls, 0)

    # Action is not rescheduled.
    eq_(eye.time_to_wait(), None)

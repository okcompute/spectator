from mock import patch
from nose.tools import assert_greater, eq_
from nose.plugins.attrib import attr

import time


@attr(platform='windows')
def test_process_monitor_real_calls():
    """Process monitor methods should appear to work."""
    from spectator.windows import ProcessMonitor
    # NOTE: verifying that the process monitor methods return meaningful
    #       results is quite complex and out of scope of this test.  Some
    #       manual testing is required to complete this analysis.
    monitor = ProcessMonitor()
    assert_greater(monitor.elapsed_time(), 0.0)
    assert_greater(monitor.memory_usage(), (0.0, 0.0))
    eq_(monitor.exit_code(), None)


@attr(platform='windows')
def test_process_monitor_exit_code():
    """Process monitor fetches exit status once the process completes."""
    import win32event
    import win32con
    from spectator.windows import ProcessMonitor
    """Process monitor methods should appear to work."""
    # Check that the process exit code is fetched correctly after the process
    # completes.  NOTE: 259 "STILL_ACTIVE" is the value returned for a process
    # that has not yet completed -- which is the case since we're monitoring
    # the current process.
    monitor = ProcessMonitor()
    with patch('win32event.WaitForSingleObject') as WaitForSingleObject:
        WaitForSingleObject.return_value = win32con.WAIT_OBJECT_0
        eq_(monitor.exit_code(), win32con.STILL_ACTIVE)


@attr(platform='windows')
def test_process_monitor_time_conversion():
    """Process monitor converts 100ns units to seconds."""
    import win32process
    from spectator.windows import ProcessMonitor
    monitor = ProcessMonitor()
    with patch('win32process.GetProcessTimes') as GetProcessTimes:
        GetProcessTimes.return_value = {
            'UserTime': 0,
            'KernelTime': 0,
        }
        eq_(monitor.elapsed_time(), 0.0)
        GetProcessTimes.return_value = {
            'UserTime':   1 * 10000000,  # 1 second.
            'KernelTime': 3 * 10000000,  # 3 seconds.
        }
        eq_(monitor.elapsed_time(), 4.0)


@attr(platform='windows')
def test_process_monitor_memory_conversion():
    """Process monitor converts bytes to gigabytes."""
    import win32process
    from spectator.windows import ProcessMonitor
    monitor = ProcessMonitor()
    with patch('win32process.GetProcessMemoryInfo') as GetProcessMemoryInfo:
        GetProcessMemoryInfo.return_value = {
            'PagefileUsage':  0,
            'WorkingSetSize': 0,
        }
        eq_(monitor.memory_usage(), (0.0, 0.0))
        GetProcessMemoryInfo.return_value = {
            'PagefileUsage':  0x40000000,  # 1 GB.
            'WorkingSetSize': 0x80000000,  # 2 GB.
        }
        eq_(monitor.memory_usage(), (1.0, 2.0))


@attr(platform='windows')
def test_remote_stopwatch():
    import win32process
    from spectator.windows import ProcessMonitor
    monitor = ProcessMonitor()
    # On an 8-processor system, 4 seconds of elapsed time
    # in 1 wall-clock second means 50% of CPU usage.
    with patch('win32api.GetSystemInfo') as GetSystemInfo:
        GetSystemInfo.return_value = {
            'dwNumberOfProcessors': 8,
        }
        cpu_usage = monitor.cpu_usage()
        with patch('win32process.GetProcessTimes') as GetProcessTimes:
            GetProcessTimes.side_effect = [{
                'UserTime':   0,
                'KernelTime': 0,
            }, {
                'UserTime':   1 * 10000000,  # 1 second.
                'KernelTime': 3 * 10000000,  # 3 seconds.
            }]
            with patch('time.clock') as clock:
                clock.side_effect = [0.0, 1.0]
                eq_(next(cpu_usage), 0.5)

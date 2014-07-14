""" Test osx platform. """
from mock import patch
from nose.tools import assert_greater, eq_
from nose.plugins.attrib import attr


@attr(platform='osx')
def test_process_monitor_real_calls():
    """Process monitor methods should appear to work."""
    from spectator.osx import ProcessMonitor
    # NOTE: verifying that the process monitor methods return meaningful
    #       results is quite complex and out of scope of this test.  Some
    #       manual testing is required to complete this analysis.
    monitor = ProcessMonitor()
    assert_greater(monitor.elapsed_time(), 0.0)
    assert_greater(monitor.memory_usage(), (0.0, 0.0))
    eq_(monitor.exit_code(), None)


@attr(platform='osx')
def test_process_monitor_exit_code():
    """Process monitor fetches exit status once the process completes."""
    from spectator.osx import ProcessMonitor
    """Process monitor methods should appear to work."""
    # On OSX, this method does not make sens since an exit code is trapped only
    # when waiting for it + the process id may already have been recycled.
    monitor = ProcessMonitor()
    eq_(monitor.exit_code(), None)


@attr(platform='osx')
def test_process_monitor_time_conversion():
    """Process monitor should add system and user cpu time."""
    from spectator.osx import ProcessMonitor
    monitor = ProcessMonitor()
    with patch('psutil.Process.cpu_times') as cpu_times:
        cpu_times.return_value = (0, 0)
        eq_(monitor.elapsed_time(), 0.0)
        cpu_times.return_value = (1, 3)
        eq_(monitor.elapsed_time(), 4.0)


@attr(platform='osx')
def test_process_monitor_memory_conversion():
    """Process monitor converts bytes to megabytes."""
    from spectator.osx import ProcessMonitor
    monitor = ProcessMonitor()
    with patch('psutil.Process.get_memory_info') as memory_info:
        memory_info.return_value = (0, 0)
        eq_(monitor.memory_usage(), (0.0, 0.0))
        memory_info.return_value = (1 * 1024 * 1024, 2 * 1024 * 1024)
        eq_(monitor.memory_usage(), (1.0, 2.0))


@attr(platform='osx')
def test_remote_stopwatch():
    from spectator.osx import ProcessMonitor
    monitor = ProcessMonitor()
    # On an 8-processor system, 4 seconds of elapsed time
    # in 1 wall-clock second means 50% of CPU usage.
    with patch('psutil.cpu_count') as mock_cpu_count:
        mock_cpu_count.return_value = 8
        cpu_usage = monitor.cpu_usage()
        with patch('psutil.Process.cpu_times') as mock_cpu_times:
            mock_cpu_times.side_effect = [
                (0.0, 0.0),
                (1.0, 3.0),
            ]
            with patch('time.clock') as mock_clock:
                mock_clock.side_effect = [0.0, 1.0]
                eq_(next(cpu_usage), 0.5)

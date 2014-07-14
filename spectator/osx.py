"""OSX-specific process monitoring support."""

import os
from itertools import izip

import psutil

from . import (
    generate_intervals,
    local_stopwatch,
)


class ProcessMonitor(object):

    """Wrapper for a process handle."""

    def __init__(self, pid=None):
        if pid is None:
            pid = os.getpid()
        self.pid = pid
        self.process = psutil.Process(self.pid)

    def exit_code(self):
        """Obtain the process' exit code, or None if still running."""
        # TODO: cannot fetch exit code on OSX. Must wait for process to
        # terminate to catch exit code
        self = self
        return None

    def elapsed_time(self):
        """Obtain the total elapsed time used by the process.

        return: the total elapsed time in seconds since startup.

        See also:

        - :term:`Elapsed time`.
        """
        times = self.process.cpu_times()
        return times[0] + times[1]

    def memory_usage(self):
        """Obtain the physical and virtual memory assigned to the process.

        The units are in GBs."""
        info = self.process.get_memory_info()
        unit = 1024.0 * 1024.0
        return (float(info[0]) / unit,
                float(info[1]) / unit)

    def cpu_usage(self):
        """Generate CPU usage in percent of total computing power.

        The computation takes into account the number of processors on the
        system.

        You should poll this function at a minimum of 0.1 seconds interval."""
        cores = psutil.cpu_count()
        elapsed_time = izip(local_stopwatch(),
                            generate_intervals(self.elapsed_time))
        while True:
            local, remote = next(elapsed_time)
            yield remote / cores / local

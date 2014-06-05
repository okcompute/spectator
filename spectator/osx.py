"""OSX-specific process monitoring support."""

import os
import psutil


def get_elapsed_time(process):
    """Get total processor time consumed by process, in seconds."""
    times = process.cpu_times()
    return times[0] + times[1]


def get_memory_usage(process):
    """Get total RAM used by a process, in MBs.

    :return: a tuple of 2 value is returned to show physical memory assigned to
    the process, as well as virtual memory reserved by the process."""
    info = process.get_memory_info()
    unit = 1024.0 * 1024.0
    return (float(info[0]) / unit,
            float(info[1]) / unit)


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
        return None

    def elapsed_time(self):
        """Obtain the total elapsed time used by the process.

        See also:

        - :term:`Elapsed time`.
        """
        return get_elapsed_time(self.process)

    def memory_usage(self):
        """Obtain the physical and virtual memory assigned to the process.

        The units are in GBs."""
        return get_memory_usage(self.process)

    def cpu_usage(self):
        """Generate CPU usage in percent of total computing power.

        The computation takes into account the number of processors on the
        system.

        You should poll this function at a minimum of 0.1 seconds interval."""
        return self.process.cpu_percent()

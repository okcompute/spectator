"""Windows-specific process monitoring support."""

import os
from itertools import izip

if os.name == 'nt':
    import win32api  # pylint: disable=import-error
    import win32con  # pylint: disable=import-error
    import win32event  # pylint: disable=import-error
    import win32file  # pylint: disable=import-error
    import win32process  # pylint: disable=import-error

from . import (
    generate_intervals,
    local_stopwatch,
)


def get_elapsed_time(process):
    """Get total processor time consumed by process, in seconds."""
    times = win32process.GetProcessTimes(process)
    return float(times['UserTime']) / 10000000.0 \
        + float(times['KernelTime']) / 10000000.0


def get_memory_usage(process):
    """Get total RAM used by a process, in GBs.

    :return: a tuple of 2 value is returned to show physical memory assigned to
        the process, as well as virtual memory reserved by the process."""
    info = win32process.GetProcessMemoryInfo(process)
    unit = 1024.0 * 1024.0 * 1024.0
    return (float(info['PagefileUsage']) / unit,
            float(info['WorkingSetSize']) / unit)


class ProcessMonitor(object):
    """Wrapper for a process handle."""

    def __init__(self, pid=None):
        if pid is None:
            pid = win32process.GetCurrentProcessId()
        self.pid = pid
        self.process = win32api.OpenProcess(
            win32con.PROCESS_ALL_ACCESS, False, self.pid,
        )

    def __del__(self):
        if self.process:
            win32file.CloseHandle(self.process)
            self.process = None

    def exit_code(self):
        """Obtain the process' exit code, or None if still running."""
        result = win32event.WaitForSingleObject(self.process, 0)
        if result == win32con.WAIT_TIMEOUT:
            return None
        else:
            return win32process.GetExitCodeProcess(self.process)

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

        You can poll this value at arbitrary intervals, but polling at a higher
        frequency increases the margin for error."""
        cores = win32api.GetSystemInfo()['dwNumberOfProcessors']
        elapsed_time = izip(local_stopwatch(),
                            generate_intervals(self.elapsed_time))
        while True:
            local, remote = next(elapsed_time)
            yield remote / cores / local

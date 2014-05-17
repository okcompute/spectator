import os
from itertools import izip

if os.name == 'nt':
    import win32api
    import win32con
    import win32event
    import win32file
    import win32process

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
    info = win32process.GetProcessMemoryInfo(process)
    unit = 1024.0 * 1024.0 * 1024.0
    return (float(info['PagefileUsage']) / unit,
            float(info['WorkingSetSize']) / unit)


class ProcessMonitor(object):
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
        result = win32event.WaitForSingleObject(self.process, 0)
        if result == win32con.WAIT_TIMEOUT:
            return None
        else:
            return win32process.GetExitCodeProcess(self.process)

    def elapsed_time(self):
        return get_elapsed_time(self.process)

    def memory_usage(self):
        return get_memory_usage(self.process)

    # Poll elapsed time at arbitraty frequency (scaling arcordingly),
    # taking into account the number of processors on the system.
    def cpu_usage(self):
        cores = win32api.GetSystemInfo()['dwNumberOfProcessors']
        elapsed_time = izip(local_stopwatch(),
                            generate_intervals(self.elapsed_time))
        while True:
            local, remote = next(elapsed_time)
            yield remote / cores / local

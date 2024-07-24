"""
opinion based time utilities.
"""

import time
import typing as t
from os import stat


def get_ctime(filepath: str, style: str = '') -> t.Union[str, float]:
    """
    REF: demos/os_demo#get_file_created_time
    """
    time_float = stat(filepath).st_ctime
    if style:
        return timestamp(style, time_float)
    else:
        return time_float


def get_mtime(filepath: str, style: str = '') -> t.Union[str, float]:
    """
    REF: demos/os_demo#get_file_created_time
    """
    time_float = stat(filepath).st_mtime
    if style:
        return timestamp(style, time_float)
    else:
        return time_float


def pretty_time(time_sec: float) -> str:
    if time_sec >= 3600:
        return '{}h{}m{}s'.format(
            int(time_sec // 3600),
            int(time_sec % 3600 // 60),
            int(time_sec % 60)
        )
    elif time_sec >= 60:
        return '{:.1f}m'.format(time_sec / 60)
    elif time_sec >= 1:
        return '{:.1f}s'.format(time_sec)
    else:
        for unit in ('ms', 'us', 'ns'):
            time_sec *= 1000
            if time_sec >= 1:
                return f'{round(time_sec)}{unit}'
        else:
            raise Exception('time too short', time_sec)


def seconds_to_hms(second: int) -> str:
    """
    REF: https://www.jb51.net/article/147479.htm
    """
    m, s = divmod(second, 60)
    h, m = divmod(m, 60)
    hms = "%02d%02d%02d" % (h, m, s)
    return hms


def timestamp(style: str = 'y-m-d h:n:s', ctime: float = 0.0) -> str:
    """
    generate a timestamp string.
    e.g. 'y-m-d h:n:s' -> '2018-12-27 15:13:45'
    """
    style = (
        style
        .replace('y', '%Y').replace('m', '%m').replace('d', '%d')
        .replace('h', '%H').replace('n', '%M').replace('s', '%S')
    )
    if ctime:
        return time.strftime(style, time.localtime(ctime))
    else:
        return time.strftime(style)


def wait(timeout: float, interval: float = 1) -> t.Iterator[int]:
    count = int(timeout / interval)
    for i in range(count):
        yield i
        time.sleep(interval)
    raise TimeoutError(f'timeout in {timeout} seconds (with {count} loops)')

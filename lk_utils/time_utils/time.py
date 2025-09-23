"""
opinion based time utilities.
"""
import time
import typing as t
from collections import namedtuple


def pretty_time(time_sec: float) -> str:
    if time_sec >= 3600:
        return '{}h{}m{}s'.format(
            int(time_sec // 3600),
            int(time_sec % 3600 // 60),
            int(time_sec % 60)
        )
    elif time_sec >= 60:
        return '{:.1f}min'.format(time_sec / 60)
    elif time_sec >= 1:
        return '{:.1f}s'.format(time_sec)
    elif time_sec == 0:
        return '0s'
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


def timestamp(style: str = 'y-m-d h:n:s', time_sec: float = None) -> str:
    """
    generate a timestamp string.
    e.g. 'y-m-d h:n:s' -> '2018-12-27 15:13:45'
    """
    style = (
        style
        .replace('y', '%Y').replace('m', '%m').replace('d', '%d')
        .replace('h', '%H').replace('n', '%M').replace('s', '%S')
    )
    if time_sec is None:
        return time.strftime(style)
    else:
        assert time_sec >= 0
        return time.strftime(style, time.localtime(time_sec))


def wait(
    timeout: float, interval: float = 1, timeout_error: bool = True
) -> t.Iterator['_ProgressInfo']:
    count = int(timeout / interval)
    for i in range(count):
        yield _ProgressInfo(count, i + 1, (i + 1) / count)
        time.sleep(interval)
    if timeout_error:
        raise TimeoutError(f'timeout in {timeout} seconds (with {count} loops)')


_ProgressInfo = namedtuple('_ProgressInfo', 'total index percent')

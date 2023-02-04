import time
from os import stat
from typing import Iterator
from typing import Union


def get_file_created_time(filepath: str, style='') -> Union[str, float]:
    """
    REF: demos/os_demo#get_file_created_time
    """
    time_float = stat(filepath).st_ctime
    if style:
        return timestamp(style, time_float)
    else:
        return time_float


def get_file_modified_time(filepath: str, style='') -> Union[str, float]:
    """
    REF: demos/os_demo#get_file_created_time
    """
    time_float = stat(filepath).st_mtime
    if style:
        return timestamp(style, time_float)
    else:
        return time_float


def seconds_to_hms(second: int) -> str:
    """
    REF: https://www.jb51.net/article/147479.htm
    """
    m, s = divmod(second, 60)
    h, m = divmod(m, 60)
    hms = "%02d%02d%02d" % (h, m, s)
    return hms


def timeout_gen(timeout: float, interval: float = 1) -> Iterator[int]:
    count = int(timeout / interval)
    for i in range(count):
        yield i
        time.sleep(interval)
    raise TimeoutError(f'timeout in {timeout} seconds (with {count} loops)')


wait = timeout_gen


def timestamp(style='y-m-d h:n:s', ctime: float = 0.0) -> str:
    """
    generate a timestamp string.
    e.g. 'y-m-d h:n:s' -> '2018-12-27 15:13:45'
    """
    style = style \
        .replace('y', '%Y').replace('m', '%m').replace('d', '%d') \
        .replace('h', '%H').replace('n', '%M').replace('s', '%S')
    if ctime:
        return time.strftime(style, time.localtime(ctime))
    else:
        return time.strftime(style)

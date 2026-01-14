import time
from contextlib import contextmanager
from typing import Callable
from typing import Iterator
from typing import Union
from collections import namedtuple


class T:
    Time = Union[int, float]


def pretty_duration(t: T.Time) -> str:
    if t >= 3600:
        return '{}h{}m{}s'.format(
            int(t // 3600),
            int(t % 3600 // 60),
            int(t % 60)
        )
    elif t >= 60:
        return '{:.1f}min'.format(t / 60)
    elif t >= 1:
        return '{:.1f}s'.format(t)
    elif t == 0:
        return '0s'
    else:
        for unit in ('ms', 'us', 'ns'):
            t *= 1000
            if t >= 1:
                return f'{round(t)}{unit}'
        else:
            raise Exception('time too short', t)


def pretty_time(t: T.Time, fmt: str = 'y-m-d h:n:s') -> str:
    return time.strftime(
        fmt
        .replace('y', '%Y').replace('m', '%m').replace('d', '%d')
        .replace('h', '%H').replace('n', '%M').replace('s', '%S'),
        time.localtime(t)
    )


@contextmanager
def timing() -> Iterator[Callable[[], None]]:
    """
    example:
        with timing() as countup:
            for i in range(...):
                sleep(...)
                countup()
        see also `test/timeit_test.py`
    """
    start = time.time()
    
    count = 0
    last_time = time.time()
    longest_index, longest_interval = (-1, -1)
    shortest_index, shortest_interval = (-1, -1)
    
    def _counting() -> None:
        nonlocal count
        nonlocal last_time
        nonlocal longest_index
        nonlocal longest_interval
        nonlocal shortest_index
        nonlocal shortest_interval
        
        index = count
        count += 1
        interval = time.time() - last_time
        
        if shortest_index == -1 or shortest_interval > interval:
            shortest_index = index
            shortest_interval = interval
        
        if longest_index == -1 or longest_interval < interval:
            longest_index = index
            longest_interval = interval
        
        last_time = time.time()
    
    yield _counting
    
    end = time.time()
    if count:
        print(
            {
                'total_time'   : pretty_duration(end - start),
                'total_calls'  : count,
                'average_call' : pretty_duration((end - start) / count),
                'longest_call' : '{} at #{}'.format(
                    pretty_duration(longest_interval), longest_index,
                ),
                'shortest_call': '{} at #{}'.format(
                    pretty_duration(shortest_interval), shortest_index,
                ),
            },
            ':r2p'
        )
    else:
        print('total_time: {}'.format(pretty_duration(end - start)), ':p')


def timestamp(fmt: str = 'y-m-d h:n:s', t: T.Time = None) -> str:
    """
    generate a timestamp string.
    e.g. 'y-m-d h:n:s' -> '2018-12-27 15:13:45'
    """
    return pretty_time(... if t is None else t, fmt)


_ProgressDatum = namedtuple('_ProgressDatum', 'total index percent')


def wait(
    timeout: float, interval: float = 1, timeout_error: bool = True
) -> Iterator[_ProgressDatum]:
    count = int(timeout / interval)
    for i in range(count):
        yield _ProgressDatum(count, i + 1, (i + 1) / count)
        time.sleep(interval)
    if timeout_error:
        raise TimeoutError(f'timeout in {timeout} seconds (with {count} loops)')

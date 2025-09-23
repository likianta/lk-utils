"""
test case: test/timeit_test.py
"""
import typing as t
from contextlib import contextmanager
from time import time
from .time import pretty_time


@contextmanager
def timing() -> t.Iterator[t.Callable[[], None]]:
    start = time()
    
    count = 0
    last_time = time()
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
        interval = time() - last_time
        
        if shortest_index == -1 or shortest_interval > interval:
            shortest_index = index
            shortest_interval = interval
        
        if longest_index == -1 or longest_interval < interval:
            longest_index = index
            longest_interval = interval
        
        last_time = time()
    
    yield _counting
    
    end = time()
    if count:
        print(
            {
                'total_time'   : pretty_time(end - start),
                'total_calls'  : count,
                'average_call' : pretty_time((end - start) / count),
                'longest_call' : '{} at #{}'.format(
                    pretty_time(longest_interval), longest_index,
                ),
                'shortest_call': '{} at #{}'.format(
                    pretty_time(shortest_interval), shortest_index,
                ),
            },
            ':r2p'
        )
    else:
        print('total_time: {}'.format(pretty_time(end - start)), ':p')

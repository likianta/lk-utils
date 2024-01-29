import atexit
import os.path
import traceback
import typing as t
from contextlib import contextmanager
from functools import partial
from functools import wraps
from inspect import currentframe
from time import time
from types import FunctionType

import rich
import rich.table


class T:
    Decorator = t.Callable
    Function = FunctionType


class TimeIt:
    records: t.Dict[str, dict]
    
    def __init__(self) -> None:
        self.records = {}
        
        @atexit.register
        def _on_exit() -> None:
            if self.records:
                self.report()
    
    def __call__(self, label: str = None) -> t.Union[
        t.ContextManager, T.Decorator
    ]:
        """
        timeit can either be used as a decorator or a context manager.
        usage 1:
            @timeit(some_label)
            def func():
                pass
        usage 2:
            with timeit(some_label):
                pass
        """
        # get source line of the caller
        # ref: https://stackoverflow.com/a/72817601
        stack = traceback.extract_stack(limit=2)
        line = stack[-2].line.lstrip()
        if line.startswith('@'):
            return partial(self._wrap_func_with_timeit, label=label)
        elif line.startswith('with '):
            return partial(self._timing, label=label)
        else:
            raise Exception('wrong usage', line)
    
    @contextmanager
    def _timing(self, label: str = None) -> None:
        if label is None:
            caller_frame = currentframe().f_back
            label = '{}:{}'.format(
                os.path.relpath(caller_frame.f_code.co_filename),
                caller_frame.f_lineno,
            )
        if label not in self.records:
            self.records[label] = {
                'count'    : 0,
                'accu_time': 0.0,
                'shortest' : 999,
                'longest'  : 0.0,
            }
        
        start = time()
        yield
        end = time()
        
        node = self.records[label]
        duration = end - start
        
        node['count'] += 1
        node['accu_time'] += duration
        if duration < node['shortest']:
            node['shortest'] = duration
        if duration > node['longest']:
            node['longest'] = duration
    
    def _wrap_func_with_timeit(
        self, func: T.Function, label: str = None
    ) -> T.Decorator:
        @wraps(func)
        def wrapper(*args, **kwargs) -> t.Any:
            with self._timing(label or func.__qualname__):
                return func(*args, **kwargs)
        
        return wrapper
    
    def report(self) -> None:
        table = rich.table.Table(
            'label/id',
            'accumulative_time',
            'call_count',
            'average_call',
            'shortest',
            'longest',
        )
        table.columns[0].style = 'cyan'
        table.columns[1].style = 'yellow'
        table.columns[2].style = 'magenta'
        table.columns[3].style = 'bold blue'
        table.columns[4].style = 'green'
        table.columns[5].style = 'red'
        for label, data in self.records.items():
            table.add_row(
                label,
                str(round(data['accu_time'], 2)) + 's',
                str(data['count']),
                str(round(data['accu_time'] / data['count'] * 1000, 2)) + 'ms',
                str(round(data['shortest'] * 1000, 2)) + 'ms',
                str(round(data['longest'] * 1000, 2)) + 'ms',
            )
        rich.print(table)


timeit = TimeIt()
report = timeit.report

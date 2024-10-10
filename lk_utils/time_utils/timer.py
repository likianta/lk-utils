import typing as t
from time import time
from functools import wraps

from lk_logger.message_formatter import formatter


class T:
    Function = t.TypeVar('Function', bound=t.Callable)


class Timer:
    
    def __init__(self) -> None:
        self._time_points = {0: time()}
        self._last_point = 0
        self._auto_point = 1000  # 0-1000 is rent for user defined
    
    def add_check_point(
        self, custom: t.Union[int, str] = None
    ) -> t.Union[int, str]:
        if custom:
            if isinstance(custom, int):
                assert 0 < custom <= 1000
            self._time_points[custom] = time()
            return custom
        else:
            self._auto_point += 1
            self._time_points[self._auto_point] = time()
            return self._auto_point
    
    def check(self, *time_points: int) -> None:
        if not time_points:
            time_points = (0,)
        now = time()
        print(':prs', *(
            formatter.fmt_time(self._time_points[p], now)
            for p in time_points
        ))
    
    def print(self, text: str, *time_points: int, t: int = None) -> int:
        if not time_points:
            time_points = (0,)
        now = time()
        print(':prs', *(
            formatter.fmt_time(self._time_points[p], now)
            for p in time_points
        ), text)
        return self.add_check_point(t)
    
    def timeit(self, label: str = None) -> t.Callable[[T.Function], T.Function]:
        def decorator(func: T.Function) -> T.Function:
            nonlocal label
            if label is None:
                label = func.__qualname__
            
            @wraps(func)
            def wrapper(*args, **kwargs) -> t.Any:
                x = self.add_check_point()
                out = func(*args, **kwargs)
                self.print(label, x)
                return out
            
            return wrapper
        return decorator


timer = Timer()

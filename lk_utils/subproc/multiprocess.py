from functools import wraps
from multiprocessing import Process
from types import FunctionType

from .. import common_typing as t


class T:
    Target = FunctionType
    Wrapper = t.Callable[[...], Process]
    Decorator = t.Callable[[Target], Wrapper]


def new_process(daemon: bool = True) -> T.Decorator:
    def decorator(func: T.Target) -> T.Wrapper:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Process:
            p = Process(target=func, args=args, kwargs=kwargs, daemon=daemon)
            p.start()
            return p
        
        return wrapper
    
    return decorator

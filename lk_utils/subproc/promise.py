import typing as t

from .threading import ThreadWorker as Thread


def defer(func: t.Callable, *args, **kwargs) -> 'Promise':
    """
    args:
        kwargs:
            self used keys:
                __instant_starting__: bool, default True.
                __daemon__: bool, default True.
            other keys will be passed to `func`.

    usage:
        def add(a: int, b: int) -> int:
            return a + b
        promise = defer(add, 1, 2).then(print)
        ...
        promise.join()  # it prints '3'
    """
    start_now = kwargs.pop('__instant_starting__', True)
    daemon = kwargs.pop('__daemon__', True)
    t = Thread(
        func, args=args, kwargs=kwargs,
        daemon=daemon, start_now=start_now
    )
    return Promise(t)


class Promise:
    _is_done: bool
    _thread: Thread
    _then: t.Optional[t.Callable]
    _result: t.Any
    
    def __init__(self, thread: Thread):
        self._is_done = False
        self._thread = thread
        self._then = None
        self._result = None
    
    def __call__(self) -> t.Any:
        return self.fulfill()
    
    def start(self) -> None:
        self._thread.start()
    
    def then(self, func, args: tuple = None, kwargs: dict = None) -> 'Promise':
        from functools import partial
        self._then = partial(func, args or (), kwargs or {})
        return self
    
    def fetch(self) -> t.Optional[t.Any]:
        if self._is_done:
            return self._result
        
        self._result = self._thread.join()
        del self._thread
        self._is_done = True
        
        if self._then:
            self._result = self._then(self._result)
        return self._result
    
    # alias
    fulfill = join = fetch
    
    @property
    def is_done(self):
        return self._is_done

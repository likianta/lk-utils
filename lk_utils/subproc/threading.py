import typing as t
from collections import defaultdict
from collections import deque
from functools import wraps
from threading import Thread as _Thread
from types import GeneratorType


class T:
    _Inherit = bool
    
    Args = t.Optional[tuple]
    Group = str  # the default group is 'default'
    Id = t.Union[str, int]
    KwArgs = t.Optional[dict]
    Result = t.Any
    Target = t.TypeVar('Target', bound=t.Callable)
    Thread = t.ForwardRef('Thread')
    
    # noinspection PyTypeHints
    Task = t.Tuple[Target, Args, KwArgs, _Inherit]
    ThreadPool = t.Dict[Group, t.Dict[Id, Thread]]


class Thread:
    _daemon: bool
    _illed: t.Optional[Exception]
    _interruptible: bool
    _is_executed: bool
    _is_running: bool
    _result: T.Result
    # noinspection PyTypeHints
    _target: T.Target
    _tasks: t.Deque[T.Task]
    _thread: _Thread
    
    class Undefined:
        pass
    
    class BrokenResult:
        def __init__(self, e: Exception) -> None:
            self.e = e
    
    def __init__(
        self,
        target: T.Target,
        args: T.Args,
        kwargs: T.KwArgs,
        daemon: bool,
        interruptible: bool = False,
        start_now: bool = True,
    ) -> None:
        self._tasks = deque()
        self._tasks.append((target, args, kwargs, False))
        self._daemon = daemon
        self._illed = None
        self._interruptible = interruptible
        self._is_executed = False
        self._is_running = False
        self._result = Thread.Undefined
        self._target = target
        if start_now:
            self.mainloop()
    
    # -------------------------------------------------------------------------
    
    @property
    def illed(self) -> t.Optional[Exception]:
        return self._illed
    
    @property
    def interruptible(self) -> bool:
        return self._interruptible
    
    @property
    def is_running(self) -> bool:
        return self._is_running
    
    # @property
    # def is_alive(self) -> bool:
    #     return self._thread.is_alive()
    
    @property
    def result(self) -> T.Result:
        if self._result is Thread.Undefined:
            raise RuntimeError('The result is not ready yet.')
        return self._result
    
    # -------------------------------------------------------------------------
    
    def start(self) -> None:
        if self._is_running:
            print('thread is already running', ':pv3')
            return
        self.mainloop()
    
    def mainloop(self) -> None:
        self._is_running = True
        
        def loop() -> None:
            while self._tasks:
                func, args, kwargs, inherit = self._tasks.popleft()
                if inherit:
                    args = (self._result, *(args or ()))
                try:
                    self._result = func(*(args or ()), **(kwargs or {}))
                except Exception as e:
                    self._illed = e
                    self._is_running = False
                    self._result = Thread.BrokenResult(e)
                    raise e
                if self._interruptible:
                    if isinstance(self._result, GeneratorType):
                        for _ in self._result:
                            if not self._is_running:
                                # a safe "break signal" emitted from the outside.
                                print('thread is safely killed', func, ':v7')
                                return
                    else:
                        print(
                            'thread is marked interruptible but there is no '
                            'break point in function', func, ':v5',
                        )
            self._is_running = False
        
        self._thread = _Thread(target=loop)
        self._thread.daemon = self._daemon
        self._thread.start()
        self._is_executed = True
    
    def add_task(self, args: tuple = None, kwargs: dict = None) -> int:
        self._tasks.append((self._target, args, kwargs, False))
        number = len(self._tasks)
        if not self._is_running:
            self.mainloop()
        return number
    
    def then(
        self,
        func: T.Target,
        args: tuple = None,
        kwargs: dict = None,
        inherit: bool = True,
    ) -> t.Self:
        self._tasks.append((func, args, kwargs, inherit))
        if not self._is_running:
            self.mainloop()
        return self
    
    def join(self, timeout: t.Optional[float] = 10e-3) -> T.Result:
        """
        params:
            timeout: None | float
                None: blocks until the thread is finished.
                    warning: the thread won't listen to KeyboardInterrupt
                    signal, it means you may never stop it if the thread is
                    run into a dead loop.
                float: blocks until the thread is finished or user presses
                    `ctrl + c`.
                ref: https://stackoverflow.com/a/3788243/9695911
        """
        if not self._is_executed:
            raise Exception('thread is never started!')
        if self._is_running:
            if timeout is None:
                self._thread.join()
            else:
                while True:
                    self._thread.join(timeout)
                    if not self._thread.is_alive():
                        break
            assert self._is_running is False
        return self.result
    
    def kill(self) -> bool:
        """
        https://stackoverflow.com/questions/6416538/how-to-check-if-an-object-is
        -a-generator-object-in-python
        """
        if self._interruptible:
            self._is_running = False
            return True
        else:
            # raise RuntimeError('the thread is not interuptable!')
            print('the thread is not interruptible!', self._thread, ':v4p')
            return False


class ThreadManager:
    thread_pool: T.ThreadPool
    
    def __init__(self) -> None:
        self.thread_pool = defaultdict(dict)
    
    def new_thread(
        self,
        ident: T.Id = None,
        group: T.Group = 'default',
        daemon: bool = True,
        singleton: bool = False,
        interruptible: bool = False,
    ) -> t.Callable[[T.Target], t.Callable[[t.Any], Thread]]:
        """a decorator wraps target function in a new thread."""
        
        def decorator(func: T.Target) -> t.Callable[[t.Any], Thread]:
            nonlocal ident
            if ident is None:
                ident = id(func)
            
            @wraps(func)
            def wrapper(*args, **kwargs) -> Thread:
                return self._create_thread_broker(
                    group,
                    ident,
                    func,
                    args,
                    kwargs,
                    daemon,
                    singleton,
                    interruptible,
                )
            
            return wrapper
        
        return decorator
    
    def run_new_thread(
        self,
        target: T.Target,
        args: T.Args = None,
        kwargs: T.KwArgs = None,
        daemon: bool = True,
        interruptible: bool = False,
    ) -> Thread:
        """run function in a new thread at once."""
        # # assert id(target) not in __thread_pool  # should i check it?
        return self._create_thread_broker(
            'default',
            id(target),
            target,
            args,
            kwargs,
            daemon,
            False,
            interruptible,
        )
    
    def _create_thread_broker(
        self,
        group: T.Group,
        ident: T.Id,
        target: T.Target,
        args: T.Args = None,
        kwargs: T.KwArgs = None,
        daemon: bool = True,
        singleton: bool = False,
        interruptible: bool = False,
    ) -> Thread:
        if singleton:
            if t := self.thread_pool[group].get(ident):
                t.add_task(args, kwargs)
                return t
        broker = self.thread_pool[group][ident] = Thread(
            target=target,
            args=args,
            kwargs=kwargs,
            daemon=daemon,
            interruptible=interruptible,
        )
        return broker
    
    # -------------------------------------------------------------------------
    
    class Delegate:
        def __init__(self, *threads: Thread):
            self.threads = threads
        
        def __len__(self) -> int:
            return len(self.threads)
        
        def fetch_one(self, index=0) -> t.Optional[Thread]:
            if self.threads:
                return self.threads[index]
            else:
                return None
        
        def join_all(self) -> None:
            for t in self.threads:
                t.join()
    
    def retrieve_thread(
        self, ident: T.Id, group: T.Group = 'default'
    ) -> t.Optional[Thread]:
        return self.thread_pool[group].get(ident)
    
    def retrieve_threads(
        self, group: T.Group = 'default'
    ) -> 'ThreadManager.Delegate':
        return ThreadManager.Delegate(*self.thread_pool[group].values())


thread_manager = ThreadManager()
new_thread = thread_manager.new_thread
run_new_thread = thread_manager.run_new_thread
retrieve_thread = thread_manager.retrieve_thread

import inspect
import typing as t
from collections import defaultdict
from functools import wraps
from threading import Thread as _Thread
from types import FrameType
from types import GeneratorType
from ..binding import Signal


class T:
    Args = tuple
    Group = str  # the default group is 'default'
    Id = t.Union[str, int]
    KwArgs = dict
    Result = t.Any
    Target = t.TypeVar('Target', bound=t.Callable)
    Thread = t.ForwardRef('Thread')
    ThreadPool = t.Dict[Group, t.Dict[Id, Thread]]


class Thread:
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
        self.on_complete = Signal()
        self._daemon = daemon
        self._illed = None  # DELETE?
        self._interruptible = interruptible
        self._is_executed = False
        self._is_running = False
        self._result = Thread.Undefined
        self._target = (target, args, kwargs)
        self._thread: t.Optional[_Thread] = None
        if start_now:
            self.mainloop()
    
    def __bool__(self) -> bool:
        return not self._is_executed or self._is_running
    
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
            raise RuntimeError('result is not evaluated out')
        return self._result
    
    # -------------------------------------------------------------------------
    
    def start(self) -> None:
        if not self._is_running:
            self.mainloop()
    
    def stop(self) -> None:
        if self._is_running:
            if self._interruptible:
                self._is_running = False
            else:
                raise Exception(
                    'thread cannot be stopped because it has no break point'
                )
    
    kill = stop
    
    def mainloop(self) -> None:
        self._is_running = True
        
        def _handle(main_caller_frame: FrameType) -> None:
            func, args, kwargs = self._target
            try:
                self._result = func(*args, **kwargs)
            except Exception as e:
                self._illed = e
                self._is_running = False
                self._result = Thread.BrokenResult(e)
                
                # https://gemini.google.com/share/7cff088615cb
                stack = []
                frame = main_caller_frame
                while frame:
                    info = inspect.getframeinfo(frame)
                    stack.append('file "{}:{}" at "{}"'.format(
                        info.filename, info.lineno, info.function
                    ))
                    frame = frame.f_back
                print(':dv8')
                print(
                    'an exception occured in a thread processing, here is its '
                    'caller stack trace:', ':v8'
                )
                for i, line in enumerate(reversed(stack)):
                    print('    {}. {}'.format(i, line), ':v8s1')
                    
                raise e
            if self._interruptible:
                # https://stackoverflow.com/questions/6416538
                if isinstance(self._result, GeneratorType):
                    for _ in self._result:
                        if not self._is_running:
                            # a safe "break signal" emitted from the outside.
                            print('thread is safely killed', func, ':v7')
                            break
                else:
                    raise Exception(
                        'thread is marked interruptible but there is no break '
                        'point in the function', func,
                    )
            self.on_complete.emit(self._result)
            self._is_running = False
        
        _frame = inspect.currentframe()
        self._thread = _Thread(target=_handle, args=(_frame,))
        self._thread.daemon = self._daemon
        self._thread.start()
        self._is_executed = True
    
    def join(self, timeout: t.Optional[float] = 10e-3) -> T.Result:
        """
        params:
            timeout: None | float
                None: blocking until thread finished.
                    warning: the thread won't listen to KeyboardInterrupt
                    signal, it means you may never stop it if the thread is run
                    into a dead loop.
                float:
                    blocking until thread finished or user presses `ctrl + c`.
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
                return self._create_thread(
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
        *args,
        daemon: bool = True,
        singleton: bool = False,
        interruptible: bool = None,
        **kwargs
    ) -> Thread:
        """run function in a new thread at once."""
        # # assert id(target) not in __thread_pool  # should i check it?
        if 'args' in kwargs or 'kwargs' in kwargs:
            print(
                ':v6',
                'deprecation warning: `run_new_thread` has changed its '
                'signature to `(func, *args, **kwargs)`, if you are passing '
                '`(func, args=..., kwargs=...)`, it may crash the process.'
            )
        return self._create_thread(
            'default',
            id(target),
            target,
            args,
            kwargs,
            daemon,
            singleton,
            interruptible
        )
    
    def _create_thread(
        self,
        group: T.Group,
        ident: T.Id,
        target: T.Target,
        args: tuple = None,
        kwargs: dict = None,
        daemon: bool = True,
        singleton: bool = False,
        interruptible: bool = False,
    ) -> Thread:
        if singleton:
            if t := self.thread_pool[group].get(ident):
                t.add_task(args, kwargs)
                return t
        out = self.thread_pool[group][ident] = Thread(
            target=target,
            args=args,
            kwargs=kwargs,
            daemon=daemon,
            interruptible=interruptible,
        )
        return out
    
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

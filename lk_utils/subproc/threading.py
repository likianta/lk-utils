from __future__ import annotations

import typing as t
from collections import defaultdict
from collections import deque
from functools import wraps
from threading import Thread
from types import GeneratorType


class T:
    Group = str  # the default group is 'default'
    Id = t.Union[str, int]
    
    # ThreadWorker
    Target = t.Callable
    Args = t.Optional[tuple]
    KwArgs = t.Optional[dict]
    _Inherit = bool
    Task = t.Tuple[Target, Args, KwArgs, _Inherit]
    
    # ThreadPool
    ThreadWorker = t.ForwardRef('ThreadWorker')
    ThreadPool = t.Dict[Group, t.Dict[Id, ThreadWorker]]


class ThreadWorker:
    _daemon: bool
    _illed: t.Optional[Exception]
    _interruptible: bool
    _is_executed: bool
    _is_running: bool
    _result: t.Any
    _target: T.Target
    _tasks: t.Deque[T.Task]
    _thread: Thread
    
    class Undefined:
        pass
    
    def __init__(
            self,
            target: T.Target,
            args: T.Args,
            kwargs: T.KwArgs,
            daemon: bool,
            interruptible: bool = False,
            start_now: bool = True
    ):
        self._tasks = deque()
        self._tasks.append((target, args, kwargs, False))
        self._daemon = daemon
        self._interruptible = interruptible
        self._is_executed = False
        self._is_running = False
        self._result = ThreadWorker.Undefined
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
    def result(self) -> t.Any:
        if self._result is ThreadWorker.Undefined:
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
                    raise e
                if self._interruptible:
                    if isinstance(self._result, GeneratorType):
                        for _ in self._result:
                            if not self._is_running:
                                # a safe "break signal" emitted from the outside.
                                print('[red dim]thread is safely killed[/]',
                                      func, ':r')
                                return
                    else:
                        print('[yellow dim]thread is marked interruptible but '
                              'there is no break point in function[/]', func,
                              ':r')
            self._is_running = False
        
        self._thread = Thread(target=loop)
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
            func: t.Callable,
            args: tuple = None,
            kwargs: dict = None,
            inherit=True
    ) -> t.Self:
        self._tasks.append((func, args, kwargs, inherit))
        if not self._is_running:
            self.mainloop()
        return self
    
    def join(self, timeout: float = None) -> t.Any:
        if not self._is_executed:
            raise Exception('thread is never started!')
        self._thread.join(timeout)
        return self._result
    
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
    
    def __init__(self):
        self.thread_pool = defaultdict(dict)
    
    def new_thread(
            self, ident: T.Id = None, group: T.Group = 'default',
            daemon=True, singleton=False, interruptible=False
    ) -> t.Callable:
        """ a decorator wraps target function in a new thread. """
        
        def decorator(func: T.Target):
            nonlocal ident
            if ident is None:
                ident = id(func)
            
            @wraps(func)
            def wrapper(*args, **kwargs) -> ThreadWorker:
                return self._create_thread_worker(
                    group, ident, func, args,
                    kwargs, daemon, singleton, interruptible
                )
            
            return wrapper
        
        return decorator
    
    def run_new_thread(
            self, target: T.Target,
            args=None, kwargs=None,
            daemon=True, interruptible=False
    ) -> ThreadWorker:
        """ run function in a new thread at once. """
        # # assert id(target) not in __thread_pool  # should i check it?
        return self._create_thread_worker(
            'default', id(target), target,
            args, kwargs, daemon, False, interruptible
        )
    
    def _create_thread_worker(
            self, group: T.Group, ident: T.Id, target: T.Target,
            args=None, kwargs=None,
            daemon=True, singleton=False, interruptible=False
    ) -> ThreadWorker:
        if singleton:
            if t := self.thread_pool[group].get(ident):
                t.add_task(args, kwargs)
                return t
        worker = self.thread_pool[group][ident] = ThreadWorker(
            target=target, args=args, kwargs=kwargs, daemon=daemon,
            interruptible=interruptible
        )
        return worker
    
    # -------------------------------------------------------------------------
    
    class Delegate:
        
        def __init__(self, *threads: ThreadWorker):
            self.threads = threads
        
        def __len__(self):
            return len(self.threads)
        
        def fetch_one(self, index=0) -> t.Optional[ThreadWorker]:
            if self.threads:
                return self.threads[index]
            else:
                return None
        
        def join_all(self):
            for t in self.threads:
                t.join()
    
    def retrieve_thread(
            self,
            ident: T.Id,
            group: T.Group = 'default'
    ) -> ThreadWorker | None:
        return self.thread_pool[group].get(ident)
    
    def retrieve_threads(
            self,
            group: T.Group = 'default'
    ) -> 'ThreadManager.Delegate':
        return ThreadManager.Delegate(*self.thread_pool[group].values())


thread_manager = ThreadManager()
new_thread = thread_manager.new_thread
run_new_thread = thread_manager.run_new_thread
retrieve_thread = thread_manager.retrieve_thread

from __future__ import annotations

from collections import defaultdict
from collections import deque

import typing as t
from functools import wraps
from threading import Thread


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
            daemon: bool
    ):
        self._tasks = deque()
        self._tasks.append((target, args, kwargs, False))
        self._daemon = daemon
        self._is_running = False
        self._result = ThreadWorker.Undefined
        self._target = target
        self.mainloop()
    
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
    
    def mainloop(self) -> None:
        self._is_running = True
        
        def loop() -> None:
            while self._tasks:
                func, args, kwargs, inherit = self._tasks.popleft()
                if inherit:
                    args = (self._result, *(args or ()))
                self._result = func(*(args or ()), **(kwargs or {}))
            self._is_running = False
        
        self._thread = Thread(target=loop)
        self._thread.daemon = self._daemon
        self._thread.start()
    
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
        self._thread.join(timeout)
        return self._result


class ThreadManager:
    thread_pool: T.ThreadPool
    
    def __init__(self):
        self.thread_pool = defaultdict(dict)
    
    def new_thread(
            self, ident: T.Id = None, group: T.Group = 'default',
            daemon=True, singleton=False
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
                    kwargs, daemon, singleton
                )
            
            return wrapper
        
        return decorator
    
    def run_new_thread(
            self, target: T.Target,
            args=None, kwargs=None,
            daemon=True
    ) -> ThreadWorker:
        """ run function in a new thread at once. """
        # # assert id(target) not in __thread_pool  # should i check it?
        return self._create_thread_worker(
            'default', id(target), target,
            args, kwargs, daemon
        )
    
    def _create_thread_worker(
            self, group: T.Group, ident: T.Id, target: T.Target,
            args=None, kwargs=None,
            daemon=True, singleton=False
    ) -> ThreadWorker:
        if singleton:
            if t := self.thread_pool[group].get(ident):
                t.add_task(args, kwargs)
                return t
        worker = self.thread_pool[group][ident] = ThreadWorker(
            target=target, args=args, kwargs=kwargs, daemon=daemon
        )
        return worker
    
    # -------------------------------------------------------------------------
    
    class _Delegate:
        
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
            ident: T.Id = None,
            group: T.Group = 'default'
    ) -> 'ThreadManager._Delegate':
        # print(':l', self.thread_pool, ident)
        dict_ = self.thread_pool[group]
        if ident is None:
            return ThreadManager._Delegate(*dict_.values())
        else:
            if t := dict_.get(ident):
                return ThreadManager._Delegate(t)
            else:
                return ThreadManager._Delegate()


thread_manager = ThreadManager()
new_thread = thread_manager.new_thread
run_new_thread = thread_manager.run_new_thread
retrieve_thread = thread_manager.retrieve_thread

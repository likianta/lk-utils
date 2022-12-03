import typing as t
from collections import defaultdict
from functools import partial
from functools import wraps
from threading import Thread as BaseThread


class T:
    Group = str  # the default group is 'default'
    Id = t.Union[str, int]
    Target = t.Callable
    Task = t.Tuple[t.Optional[tuple], t.Optional[dict]]
    Thread = t.ForwardRef('Thread')
    ThreadPool = t.Dict[Group, t.Dict[Id, Thread]]


class Thread(BaseThread):
    """
    https://stackoverflow.com/questions/6893968/how-to-get-the-return-value
    -from-a-thread-in-python
    """
    _tasks: t.List[T.Task]
    __result = None
    
    def __init__(
            self, target: t.Callable,
            args: tuple = None, kwargs: dict = None
    ):
        self._tasks = [(args, kwargs)]
        super().__init__(target=partial(self._run_tasks, target))
    
    def _run_tasks(self, func) -> t.Any:
        while self._tasks:
            args, kwargs = self._tasks.pop(0)
            self.__result = func(*(args or ()), **(kwargs or {}))
        return self.__result
    
    def add_task(self, args: tuple = None, kwargs: dict = None) -> int:
        self._tasks.append((args, kwargs))
        return len(self._tasks)
    
    def join(self, timeout: float = None) -> t.Any:
        super().join(timeout)
        return self.__result
    
    @property
    def result(self) -> t.Any:
        return self.__result


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
            def wrapper(*args, **kwargs) -> T.Thread:
                thread = self._create_thread(
                    group, ident, func, args,
                    kwargs, daemon, singleton
                )
                return thread
            
            return wrapper
        
        return decorator
    
    def run_new_thread(
            self, target: T.Target,
            args=None, kwargs=None,
            daemon=True
    ) -> T.Thread:
        """ run function in a new thread at once. """
        # # assert id(target) not in __thread_pool  # should i check it?
        thread = self._create_thread(
            'default', id(target), target,
            args, kwargs, daemon
        )
        return thread
    
    def _create_thread(
            self, group: T.Group, ident: T.Id, target: T.Target,
            args=None, kwargs=None,
            daemon=True, singleton=False
    ) -> T.Thread:
        if singleton:
            if t := self.thread_pool[group].get(ident):
                if t.is_alive():
                    t.add_task(args, kwargs)
                    return t
                # else:
                #     self.thread_pool.pop(ident)
        thread = self.thread_pool[group][ident] = Thread(
            target=target, args=args or (), kwargs=kwargs or {}
        )
        thread.daemon = daemon
        thread.start()
        return thread
    
    # -------------------------------------------------------------------------
    
    class _Delegate:
        
        def __init__(self, *threads: T.Thread):
            self.threads = threads
        
        def __len__(self):
            return len(self.threads)
        
        def fetch_one(self, index=0) -> t.Optional[T.Thread]:
            if self.threads:
                return self.threads[index]
            else:
                return None
        
        def all_join(self):
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

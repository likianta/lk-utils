from __future__ import annotations

import subprocess
import typing as t
from collections import defaultdict
from functools import wraps
from textwrap import dedent
from threading import Thread as ThreadBase


class Thread(ThreadBase):
    """
    https://stackoverflow.com/questions/6893968/how-to-get-the-return-value
        -from-a-thread-in-python
    """
    __result = None
    
    def __init__(
            self, target: t.Callable,
            args: tuple = None, kwargs: dict = None
    ):
        super().__init__(
            target=self._decorator(target),
            args=args or (),
            kwargs=kwargs or {},
        )
    
    def _decorator(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.__result = func(*args, **kwargs)
            return self.__result
        
        return wrapper
    
    def join(self, timeout: float | None = None) -> t.Any:
        super().join(timeout)
        return self.__result
    
    @property
    def result(self) -> t.Any:
        return self.__result


class T:
    Group = str  # the default group is 'default'
    Id = t.Union[str, int]
    Target = t.Callable
    Thread = Thread
    ThreadPool = t.Dict[Group, t.Dict[Id, Thread]]


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
                thread.start()
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
        thread.start()
        return thread
    
    def _create_thread(
            self, group: T.Group, ident: T.Id, target: T.Target,
            args=None, kwargs=None,
            daemon=True, singleton=False
    ) -> T.Thread:
        if singleton:
            if t := self.thread_pool[group].get(ident):
                if t.is_alive():
                    return t
                else:
                    self.thread_pool.pop(ident)
        thread = self.thread_pool[group][ident] = Thread(
            target=target, args=args or (), kwargs=kwargs or {}
        )
        thread.daemon = daemon
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


# ------------------------------------------------------------------------------

def run_cmd_shell(cmd: str, multi_lines=False, ignore_errors=False):
    """
    References:
        https://docs.python.org/zh-cn/3/library/subprocess.html
    """
    if multi_lines:
        # https://stackoverflow.com/questions/20042205/calling-multiple-commands
        #   -using-os-system-in-python
        cmd = dedent(cmd).strip().replace('\n', ' & ')
        #   TODO:
        #       replaced with '&' for windows
        #       replaced with ';' for linux (not implemented yet)
    
    try:
        '''
        subprocess.run:params
            shell=True  pass in a string, call the command as a string.
            shell=False pass in a list, the first element of the list is used
                        as the command, and the subsequent elements are used as
                        the parameters of the command.
            check=True  check return code, if finish with no exception
                        happened, the code is 0; otherwise it is a non-zero
                        number, and raise an error called `subprocess
                        .CalledProcessError`.
            capture_output=True
                        capture and retrieve stream by:
                            ret = subprocess.run(..., capture_output=True)
                            ret.stdout.read()  # -> bytes ...
                            ret.stderr.read()  # -> bytes ...
        '''
        ret = subprocess.run(
            cmd, shell=True, check=True, capture_output=True
        )
        ret = ret.stdout.decode(encoding='utf-8', errors='replace').strip()
    except subprocess.CalledProcessError as e:
        ret = e.stderr.decode(encoding='utf-8', errors='replace').strip()
        if not ignore_errors:
            raise Exception(dedent(f'''
                Command shell error happend:
                    cmd: {cmd}
                    err: {ret}
            '''))
    return ret


def run_cmd_args(*args, ignore_errors=False):
    return run_cmd_shell(' '.join(format_cmd(*args)),
                         ignore_errors=ignore_errors)


def run_bat_script(file, *args, **kwargs):
    return run_cmd_args(*format_cmd(file, *args, **kwargs))


def format_cmd(*args, **kwargs):
    out = []
    
    def _is_unwrapped(arg):
        # assert len(arg) > 0
        if ' ' in arg and not (arg[0] == '"' or arg[-1] in '"'):
            return True
        else:
            return False
    
    for i in args:
        if i is None:
            continue
        if (i := str(i).strip()) == '':
            continue
        if _is_unwrapped(i):
            i = f'"{i}"'
        out.append(i)
    
    if kwargs:
        # assert all(bool(' ' not in k) for k in kwargs)
        for k, v in zip(map(str, kwargs.keys()), map(str, kwargs.values())):
            # if k.startswith('_'):
            #     prefix = re.match(r'^_+', k).group()
            #     k = prefix.replace('_', '-') + k
            k = k.strip().replace('_', '-')
            v = v.strip()
            if v:
                if _is_unwrapped(v):
                    v = f'"{v}"'
                out.append(f'{k}={v}')
            else:
                out.append(k)
    
    return out


# -----------------------------------------------------------------------------

def defer(func, *args, **kwargs) -> 'Promise':
    """
    args:
        kwargs:
            self used keys:
                start_background_working_now: bool, default True.
                __daemon__: bool, default True.
            other keys will be passed to `func`.
    
    usage:
        def add(a: int, b: int) -> int:
            return a + b
        promise = defer(add, 1, 2).then(print)
        ...
        promise.fulfill()  # it prints '3'
    """
    start_now = kwargs.pop('start_background_working_now', True)
    daemon = kwargs.pop('__daemon__', True)
    t = Thread(target=func, args=args, kwargs=kwargs)
    t.daemon = daemon
    return Promise(t, start_now)


class Promise:
    _is_start: bool
    _is_done: bool
    _thread: Thread
    _then: t.Optional[t.Callable]
    _result: t.Any
    
    def __init__(self, thread: Thread, start_now=True):
        self._is_start = False
        self._is_done = False
        self._thread = thread
        self._then = None
        self._result = None
        if start_now:
            self.start()
    
    def __call__(self) -> t.Any:
        return self.fulfill()
    
    def start(self) -> None:
        if self._is_start: return
        self._is_start = True
        self._thread.start()
    
    def then(self, func, args: tuple = None, kwargs: dict = None) -> 'Promise':
        from functools import partial
        self._then = partial(func, args or (), kwargs or {})
        return self
    
    def fetch(self) -> t.Optional[t.Any]:
        if not self._is_start:
            self.start()
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

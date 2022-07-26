from __future__ import annotations

import os
import subprocess
import typing as t
from functools import wraps
from textwrap import dedent
from threading import Thread


class T:
    Id = t.Union[str, int]
    Target = t.Callable
    Thread = Thread
    ThreadPool = t.Dict[Id, Thread]


__thread_pool: T.ThreadPool = {}


def new_thread(ident: T.Id = None, daemon=True, singleton=False):
    """ a decorator wraps target function in a new thread. """
    
    def decorator(func: T.Target):
        nonlocal ident
        if ident is None:
            ident = id(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Thread:
            thread = _create_thread(
                ident, func, args,
                kwargs, daemon, singleton
            )
            thread.start()
            return thread
        
        return wrapper
    
    return decorator


def run_new_thread(target: T.Target, args=None, kwargs=None,
                   daemon=True) -> Thread:
    """ run function in a new thread at once. """
    # assert id(target) not in __thread_pool
    thread = _create_thread(id(target), target, args, kwargs, daemon)
    thread.start()
    return thread


def retrieve_thread(ident: T.Id) -> t.Optional[Thread]:
    # print(':l', __thread_pool, ident)
    return __thread_pool.get(ident)


def _create_thread(ident: T.Id, target: T.Target, args=None, kwargs=None,
                   daemon=True, singleton=False) -> T.Thread:
    if singleton:
        if t := __thread_pool.get(ident):
            if t.is_alive():
                return t
            else:
                __thread_pool.pop(ident)
    thread = __thread_pool[ident] = Thread(
        target=target, args=args or (), kwargs=kwargs or {}
    )
    thread.daemon = daemon
    return thread


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


# ------------------------------------------------------------------------------

def mklink(src_path, dst_path, exist_ok=False):
    """

    References:
        https://blog.walterlv.com/post/ntfs-link-comparisons.html
    """
    assert os.path.exists(src_path), src_path
    if os.path.exists(dst_path):
        if exist_ok:
            return dst_path
        else:
            raise FileExistsError(dst_path)
    
    if os.path.isdir(src_path):
        run_cmd_shell(f'mklink /J "{dst_path}" "{src_path}"')
    elif os.path.isfile(src_path):
        run_cmd_shell(f'mklink /H "{dst_path}" "{src_path}"')
    else:
        raise Exception(src_path)
    
    return dst_path


def mklinks(src_dir, dst_dir, names=None, exist_ok=False):
    out = []
    for n in (names or os.listdir(src_dir)):
        out.append(mklink(f'{src_dir}/{n}', f'{dst_dir}/{n}', exist_ok))
    return out


# -----------------------------------------------------------------------------

def defer(func, *args, **kwargs) -> 'Then':
    """
    usage:
        def add(a: int, b: int) -> int:
            return a + b
        d = defer(add, 1, 2)
        ...
        result = await d.fetch()
        print(result)  # -> 3
    """
    daemon = kwargs.pop('__daemon__', True)
    t = Thread(target=func, args=args, kwargs=kwargs)
    t.daemon = daemon
    return Then(t)


class Then:
    thread: Thread
    _promise: t.Optional['Promise']
    
    def __init__(self, thread: Thread):
        self.thread = thread
        self._promise = None
    
    def then(self, func, args: tuple = None, kwargs: dict = None):
        from functools import partial
        self._promise = Promise(
            self.thread, partial(func, args or (), kwargs or {})
        )
        return self._promise
    
    async def fetch(self):
        return self._promise.fetch()


class Promise:
    
    def __init__(self, thread: Thread, handle: t.Callable):
        """
        args:
            handle: partial function with no parameters.
        """
        self.thread = thread
        self._handle = handle
    
    async def fetch(self):
        from asyncio import sleep
        self.thread.start()
        while True:
            if self.thread.is_alive():
                await sleep(0.1)
            else:
                break
        return self._handle()

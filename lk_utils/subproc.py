import subprocess
from functools import wraps
from textwrap import dedent
from threading import Thread


def new_thread(func):
    """ New thread decorator. """
    
    @wraps(func)
    def decorate(*args, **kwargs) -> Thread:
        return run_new_thread(func, *args, **kwargs)
    
    return decorate


def run_new_thread(func, *args, **kwargs) -> Thread:
    """ Run function in a new thread at once. """
    t = Thread(target=func, args=args, kwargs=kwargs)
    t.start()
    return t


# ------------------------------------------------------------------------------

def run_cmd_shell(cmd: str, multi_lines=False, ignore_errors=False):
    if multi_lines:
        # https://stackoverflow.com/questions/20042205/calling-multiple-commands
        #   -using-os-system-in-python
        cmd = dedent(cmd).strip().replace('\n', '&&')
        #   TODO:
        #       replaced with '&' for windows
        #       replaced with ';' for linux (not implemented yet)
    
    try:
        ret = subprocess.run(
            cmd, shell=True, check=True, capture_output=True
        )
        out = ret.stdout.decode(encoding='utf-8').strip()
    except subprocess.CalledProcessError as e:
        out = e.stderr.decode(encoding='utf-8').strip()
        if not ignore_errors:
            from lk_logger import lk
            lk.logp(cmd, out)
            raise e
    return out


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
    
    for i in filter(None, map(str, args)):
        if _is_unwrapped(i):
            i = f'"{i}"'
        out.append(i)
        
    if kwargs:
        # assert all(bool(' ' not in k) for k in kwargs)
        for k, v in zip(map(str, kwargs.keys()), map(str, kwargs.values())):
            if v:
                if _is_unwrapped(v):
                    v = f'"{v}"'
                out.append(f'{k}={v}')
            else:
                out.append(k)
            
    return out

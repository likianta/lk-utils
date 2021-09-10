import os
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
            # if k.startswith('_'):
            #     prefix = re.match(r'^_+', k).group()
            #     k = prefix.replace('_', '-') + k
            k = k.replace('_', '-')
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

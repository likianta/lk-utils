from __future__ import annotations

import os
import os.path as ospath
from inspect import currentframe

_IS_WINDOWS = os.name == 'nt'


class T:
    Path = DirPath = FilePath = str


def normpath(path: T.Path, force_abspath=False) -> T.Path:
    if force_abspath:
        out = ospath.abspath(path)
    else:
        out = ospath.normpath(path)
    if _IS_WINDOWS:
        out = out.replace('\\', '/')
    return out


# ------------------------------------------------------------------------------

def dirpath(path: T.Path) -> T.DirPath:
    if ospath.isdir(path):
        return normpath(path)
    else:
        return normpath(ospath.dirname(path))


def dirname(path: T.Path) -> str:
    """ Return the directory name of path.

    Examples:
        path = 'a/b/c/d.txt' -> 'c'
        path = 'a/b/c' -> 'c'
    """
    path = normpath(path, True)
    if ospath.isfile(path):
        return ospath.basename(ospath.dirname(path))
    else:
        return ospath.basename(path)


def filename(path: T.Path, suffix=True, strict=False) -> T.Path:
    """ Return the file name from path.

    Examples:
        strict  input           output
        True    'a/b/c.txt'     'c.txt'
        True    'a/b'            error
        False   'a/b'           'b'
    """
    if strict and isdir(path):
        raise Exception('Cannot get filename from a directory!')
    if suffix:
        return ospath.basename(path)
    else:
        return ospath.splitext(ospath.basename(path))[0]


def filestem(path: T.Path) -> str:
    return ospath.splitext(ospath.basename(path))[0]


def split(path: T.Path, separate_ext=False) -> tuple[str, ...]:
    """
    return:
        `tuple[str dirpath, str filename]` or `tuple[str dirpath, str
            filename_stem, str ext]`.
        the dirpath is asserted not empty. others may be empty.
    """
    path = normpath(path, force_abspath=True)
    head, tail = ospath.split(path)
    head = head.rstrip('/')
    if separate_ext:
        tail, ext = ospath.splitext(tail)
        return head, tail, ext
    else:
        return head, tail


# ------------------------------------------------------------------------------

def isfile(filepath: T.Path) -> bool:
    """ Unsafe method judging path-like string.

    TLDR: If `filepath` looks like a filepath, will return True; otherwise
        return False.

    Judgement based:
        - Does it end with '/'? -> False
        - Does it really exist on system? -> True
        - Does it contain a dot ("xxx.xxx")? -> True

    Positive cases:
        print(isfile('D:/myprj/README.md'))  # -> True (no matter exists or not)
        print(isfile('D:/myprj/README'))  # -> True (if it really exists)
        print(isfile('D:/myprj/README'))  # -> False (if it really not exists)

    Negative cases: (the function judges seems not that good)
        print(isfile('D:/myprj/.idea'))  # -> True (it should be False)
        print(isfile('D:/!@#$%^&*/README.md'))  # -> True (it should be False)
    """
    if filepath == '':
        return False
    if filepath.endswith('/'):
        return False
    if ospath.isfile(filepath):
        return True
    if '.' in filepath.rsplit('/', 1)[-1]:
        return True
    else:
        return False


def isdir(dirpath: T.Path) -> bool:
    """ Unsafe method judging dirpath-like string.

    TLDR: If `dirpath` looks like a dirpath, will return True; otherwise return
        False.

    Judgement based:
        - Is it a dot/dot-slash/slash? -> True
        - Does it really exist on system? -> True
        - Does it end with '/'? -> False
    """
    if dirpath == '':
        return False
    if dirpath in ('.', './', '/'):
        return True
    if ospath.isdir(dirpath):
        return True
    else:
        return False


def not_empty(file: T.FilePath) -> bool:
    """
    References:
        https://www.imooc.com/wenda/detail/350036?block_id=tuijian_yw
    """
    return bool(ospath.exists(file) and ospath.getsize(file))


def currdir() -> T.Path:
    caller_frame = currentframe().f_back
    return _get_dir_info_from_caller(caller_frame)


def relpath(path: T.Path, force_abspath=True) -> T.Path:
    """ Consider relative path always based on caller's.

    References: https://blog.csdn.net/Likianta/article/details/89299937
    """
    caller_frame = currentframe().f_back
    caller_dir = _get_dir_info_from_caller(caller_frame)
    
    if path in ('', '.', './'):
        out = caller_dir
    else:
        out = ospath.abspath(ospath.join(caller_dir, path))
    
    if force_abspath:
        return normpath(out)
    else:
        return normpath(ospath.relpath(out, os.getcwd()))


def _get_dir_info_from_caller(frame, ignore_error=False) -> T.Path:
    file = frame.f_globals.get('__file__') \
           or frame.f_code.co_filename
    if file.startswith('<') and file.endswith('>'):
        if ignore_error:
            print(':v4p2', 'Unable to locate directory from caller frame! '
                           'Fallback using current working directory instead.')
            return normpath(os.getcwd())
        else:
            raise OSError('Unable to locate directory from caller frame!')
    else:
        return normpath(ospath.dirname(file))

import os
import os.path as ospath
from functools import partial
from inspect import currentframe
from types import FrameType

from .. import common_typing as t

__all__ = [
    'abspath',
    'barename',
    'basename',
    'cd_current_dir',
    'dirname',
    'dirpath',
    'exists',
    'filename',
    'filepath',
    'filesize',
    'get_current_dir',
    'isdir',
    'isfile',
    'islink',
    'normpath',
    'not_empty',
    'parent',
    'parent_path',
    'relpath',
    'replace_ext',
    'split',
    'xpath',
]

IS_WINDOWS = os.name == 'nt'
exists = ospath.exists


class T:
    Path = DirPath = FilePath = str


def normpath(path: T.Path, force_abspath: bool = False) -> T.Path:
    if force_abspath:
        out = ospath.abspath(path)
    else:
        out = ospath.normpath(path)
    if IS_WINDOWS:
        out = out.replace('\\', '/')
    return out


abspath = partial(normpath, force_abspath=True)


# ------------------------------------------------------------------------------

def parent_path(path: T.Path) -> T.DirPath:
    return normpath(ospath.dirname(path.rstrip('/\\')))


parent = parent_path  # alias


def relpath(path: T.Path, start: T.Path = None) -> T.Path:
    if not path: return ''
    return normpath(ospath.relpath(path, start))


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


def filepath(path: T.Path, suffix: bool = True, strict: bool = False) -> T.Path:
    if strict and isdir(path):
        raise Exception('Cannot get filepath from a directory!')
    if suffix:
        return normpath(path)
    else:
        return normpath(ospath.splitext(path)[0])


def filename(path: T.Path, suffix: bool = True, strict: bool = False) -> str:
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


def filesize(path: T.Path, fmt: type = int) -> t.Union[int, str]:
    size = os.path.getsize(path)
    if fmt is int:
        return size
    elif fmt is str:
        for unit in ('B', 'KB', 'MB', 'GB'):
            if size < 1024:
                return f'{size:.2f}{unit}'
            size /= 1024
        else:
            return f'{size:.2f}TB'
    else:
        raise Exception(fmt, path)


basename = filename


def barename(path: T.Path, strict: bool = False) -> str:
    return filename(path, suffix=False, strict=strict)


# ------------------------------------------------------------------------------

def isfile(path: T.Path) -> bool:
    if path.strip('./') == '':
        return False
    if ospath.isfile(path):
        return True
    if ospath.isdir(path):
        return False
    if ospath.islink(path):
        path = ospath.realpath(path)
        return isfile(path)
    # raise Exception('unknown path type', path)
    return False


def isdir(path: T.Path) -> bool:
    if path.strip('./') == '':
        return True
    if ospath.isdir(path):
        return True
    if ospath.isfile(path):
        return False
    if ospath.islink(path):
        path = ospath.realpath(path)
        return isdir(path)
    # raise Exception('unknown path type', path)
    return False


islink = ospath.islink


def not_empty(file: T.FilePath) -> bool:
    """
    References:
        https://www.imooc.com/wenda/detail/350036?block_id=tuijian_yw
    """
    return bool(ospath.exists(file) and ospath.getsize(file))


# -----------------------------------------------------------------------------


def cd_current_dir() -> T.Path:
    caller_frame = currentframe().f_back
    dir = _get_dir_of_frame(caller_frame)
    os.chdir(dir)
    return dir


def get_current_dir() -> T.Path:
    caller_frame = currentframe().f_back
    return _get_dir_of_frame(caller_frame)


def replace_ext(path: T.Path, ext: str) -> T.Path:
    """
    params:
        ext:
            recommend no dot prefiexed, like 'png'.
            but for compatibility, '.png' is also acceptable.
    """
    return ospath.splitext(path)[0] + '.' + ext.lstrip('.')


def split(path: T.Path, parts: int = 2) -> t.Tuple[str, ...]:
    path = abspath(path)
    if parts == 2:
        a, b = path.rsplit('/', 1)
        return a, b
    elif parts == 3:
        assert isfile(path)
        a, b = path.rsplit('/', 1)
        b, c = b.rsplit('.', 1)
        return a, b, c
    else:
        raise ValueError('Unsupported parts number!')


def xpath(path: T.Path, force_abspath: bool = True) -> T.Path:
    """ Consider relative path always based on caller's.

    References: https://blog.csdn.net/Likianta/article/details/89299937
    """
    caller_frame = currentframe().f_back
    caller_dir = _get_dir_of_frame(caller_frame)
    
    if path in ('', '.', './'):
        out = caller_dir
    else:
        out = ospath.abspath(ospath.join(caller_dir, path))
    
    if force_abspath:
        return normpath(out)
    else:
        return normpath(ospath.relpath(out, os.getcwd()))


def _get_dir_of_frame(frame: FrameType, ignore_error: bool = False) -> T.Path:
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

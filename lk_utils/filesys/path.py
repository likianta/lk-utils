import os
import os.path as osp
import typing as t
from functools import partial
from inspect import currentframe
from types import FrameType

from .checker import isdir
from .env import IS_WINDOWS
from ..time import pretty_time


class T:
    AbsPath = DirPath = FilePath = Path = str


def normpath(path: T.Path, force_abspath: bool = False) -> T.Path:
    if force_abspath:
        if path.startswith('/'):
            out = path
        else:
            out = osp.abspath(path)
    else:
        out = osp.normpath(path)
    if IS_WINDOWS:
        out = out.replace('\\', '/')
    return out


abspath = partial(normpath, force_abspath=True)


# ------------------------------------------------------------------------------


def parent_path(path: T.Path) -> T.DirPath:
    if IS_WINDOWS:
        if path.endswith((':', ':/', ':\\')):
            raise Exception('cannot get parent path of drive letter', path)
    elif path.startswith('/') and '/' not in path[1:]:
        raise Exception('cannot get parent path of root directory', path)
    return normpath(osp.dirname(path.rstrip('/\\')))


parent = parent_path  # alias


def relpath(path: T.Path, start: t.Optional[T.Path] = None) -> T.Path:
    return normpath(osp.relpath(path, start)) if path else ''


def dirpath(path: T.Path) -> T.DirPath:
    if osp.isdir(path):
        return normpath(path)
    else:
        return normpath(osp.dirname(path))


def dirname(path: T.Path) -> str:
    """
    return the directory name of path.
    examples:
        path = 'a/b/c/d.txt' -> 'c'
        path = 'a/b/c' -> 'c'
    """
    path = normpath(path, True)
    if osp.isfile(path):
        return osp.basename(osp.dirname(path))
    else:
        return osp.basename(path)


def filepath(path: T.Path, suffix: bool = True, strict: bool = False) -> T.Path:
    if strict and isdir(path):
        raise Exception('Cannot get filepath from a directory!')
    if suffix:
        return normpath(path)
    else:
        return normpath(osp.splitext(path)[0])


def filename(path: T.Path, suffix: bool = True, strict: bool = False) -> str:
    """Return the file name from path.

    Examples:
        strict  input           output
        True    'a/b/c.txt'     'c.txt'
        True    'a/b'            error
        False   'a/b'           'b'
    """
    if strict and isdir(path):
        raise Exception('Cannot get filename from a directory!')
    if suffix:
        return osp.basename(path)
    else:
        return osp.splitext(osp.basename(path))[0]


def filesize(path: T.Path, fmt: type = int) -> t.Union[int, str]:
    size = osp.getsize(path)
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


def filetime(
    path: T.Path,
    fmt: t.Union[t.Type, str] = int,
    recursive: bool = False,
    by: t.Literal['c', 'created', 'm', 'modified'] = 'm',
) -> t.Union[int, str]:
    if recursive and isdir(path):
        from .finder import findall_dirs
        from .finder import findall_files

        property = 'ctime' if by in ('c', 'created') else 'mtime'
        time_float_a = max((getattr(d, property) for d in findall_dirs(path)))
        time_float_b = max((getattr(f, property) for f in findall_files(path)))
        time_float = max(time_float_a, time_float_b)
    else:
        time_float = (
            os.stat(path).st_ctime
            if by in ('c', 'created')
            else os.stat(path).st_mtime
        )
    if fmt is int:
        return int(time_float)
    elif fmt is str:
        return pretty_time(time_float, 'y-m-d h:n:s')
    elif isinstance(fmt, str):
        if fmt in ('c', 'created', 'm', 'modified'):
            raise Exception('incorrect argument position', (path, fmt, by))
        return pretty_time(time_float, fmt)
    else:
        raise ValueError(fmt)


mtime = partial(filetime, by='m')
ctime = partial(filetime, by='c')

basename = filename


def barename(path: T.Path, strict: bool = False) -> str:
    return filename(path, suffix=False, strict=strict)


# -----------------------------------------------------------------------------


def cd_current_dir() -> T.AbsPath:
    caller_frame = t.cast(FrameType, currentframe().f_back)  # type: ignore
    dir = _get_frame_dir(caller_frame)
    os.chdir(dir)
    return dir


def get_current_dir() -> T.AbsPath:
    caller_frame = t.cast(FrameType, currentframe().f_back)  # type: ignore
    return _get_frame_dir(caller_frame)


def here(relpath: str = '.') -> T.AbsPath:
    caller_frame = t.cast(FrameType, currentframe().f_back)  # ty: ignore
    caller_dir = _get_frame_dir(caller_frame)
    if relpath in ('', '.', './'):
        return caller_dir
    else:
        return normpath('{}/{}'.format(caller_dir, relpath))


def replace_ext(path: T.Path, ext: str) -> T.Path:
    """
    params:
        ext:
            recommend no dot prefiexed, like 'png'.
            but for compatibility, '.png' is also acceptable.
    """
    return osp.splitext(path)[0] + '.' + ext.lstrip('.')


def split(
    path: T.Path, parts: int = 2
) -> t.Union[t.Tuple[str, str], t.Tuple[str, str, str]]:
    path = normpath(path)
    if '/' not in path:
        path = abspath(path)
    if parts == 2:
        a, b = path.rsplit('/', 1)
        return a, b
    elif parts == 3:
        a, b = path.rsplit('/', 1)
        b, c = b.rsplit('.', 1)
        #   special case: '.abc' -> ('', 'abc')
        return a, b, c
    else:
        raise ValueError(path, parts)


def there(relpath: str) -> T.AbsPath:
    assert relpath not in ('', '.', './')
    caller_frame = t.cast(FrameType, currentframe().f_back)  # ty: ignore
    caller_dir = _get_frame_dir(caller_frame)
    return normpath('{}/{}'.format(caller_dir, relpath))


# TODO: Delete this, use only `here` in future.
def xpath(relpath: T.Path) -> T.AbsPath:
    """
    given a relative path, return a resolved path of -
    `<dir_of_caller_frame>/<relpath>`.
    ref: https://blog.csdn.net/Likianta/article/details/89299937
    """
    caller_frame = t.cast(FrameType, currentframe().f_back)  # type: ignore
    caller_dir = _get_frame_dir(caller_frame)
    if relpath in ('', '.', './'):
        return caller_dir
    else:
        return normpath('{}/{}'.format(caller_dir, relpath))


def _get_frame_dir(frame: FrameType, ignore_error: bool = False) -> T.AbsPath:
    file = frame.f_globals.get('__file__') or frame.f_code.co_filename
    if file.startswith('<') and file.endswith('>'):
        if ignore_error:
            print(
                ':v8p2',
                'unable to locate directory from caller frame! '
                'fallback using current working directory instead.',
            )
            return normpath(os.getcwd(), True)
        else:
            raise OSError('unable to locate directory from caller frame!')
    else:
        return normpath(osp.dirname(file), True)

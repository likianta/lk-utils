from __future__ import annotations

import os
import os.path
from inspect import currentframe

_IS_WINDOWS = os.name == 'nt'


class T:
    import typing as t
    
    Path = DirPath = FilePath = str
    Name = DirName = FileName = str
    Paths = DirPaths = FilePaths = t.List[Path]
    Names = DirNames = FileNames = t.List[Name]
    Ext = str
    
    PathFormat = t.Literal[
        'filepath', 'dirpath', 'path', 'filename', 'dirname', 'name', 'zip',
        'dict', 'list', 'dlist'
    ]
    
    FinderReturn = t.Iterator[t.Tuple[FilePath, FileName]]
    
    Prefix = Suffix = t.Union[None, str, t.Tuple[str, ...]]


def normpath(path: T.Path, force_abspath=False) -> T.Path:
    """
    
    Examples:
        from            to
        -------------------
        ./              .
        ./a/b/          a/b
        ./a/b/c/../     a/b
    """
    if force_abspath:
        out = os.path.abspath(path)
    else:
        out = os.path.normpath(path)
    if _IS_WINDOWS:
        out = out.replace('\\', '/')
    return out


# ------------------------------------------------------------------------------

def get_dirpath(path: T.Path) -> T.DirPath:
    if os.path.isdir(path):
        return normpath(path)
    else:
        return normpath(os.path.dirname(path))


def get_dirname(path: T.Path) -> str:
    """ Return the directory name of path.
    
    Examples:
        path = 'a/b/c/d.txt' -> 'c'
        path = 'a/b/c' -> 'c'
    """
    if os.path.isfile(path):
        return os.path.basename(os.path.dirname(path))
    else:
        return os.path.basename(path)


def get_filename(path: T.Path, suffix=True, strict=False) -> T.Path:
    """ Return the file name from path.
    
    Examples:
        suffix  strict  input           output
        True    True    'a/b/c.txt'     'c.txt'
        True    True    'a/b'            error
        True    False   'a/b'           'b'
        False   True    'a/b/c.txt'     'c'
        False   True    'a/b'            error
        False   False   'a/b'           'b'
    """
    if strict and isdir(path):
        raise Exception('Cannot get filename from a directory!')
    name = os.path.basename(path)
    if suffix:
        return name
    else:
        return os.path.splitext(name)[0]


def split(path: T.Path, separate_ext=False) -> tuple[str, ...]:
    """
    return:
        `tuple[str dirpath, str filename]` or `tuple[str dirpath, str
            filename_stem, str ext]`.
        the dirpath is asserted not empty. others may be empty.
    """
    path = normpath(path, force_abspath=True)
    head, tail = os.path.split(path)
    head = head.rstrip('/')
    if separate_ext:
        tail, ext = os.path.splitext(tail)
        return head, tail, ext
    else:
        return head, tail


def __get_launch_path() -> T.Path:
    """ Get launcher's filepath.
    
    Example:
        sys.argv: ['D:/myprj/src/main.py', ...] -> 'D:/myprj/src/main.py'
    """
    from sys import argv
    path = os.path.abspath(argv[0])
    if os.path.isfile(path):
        return normpath(path)
    else:
        raise Exception


def __get_launch_dir() -> T.Path:
    return os.path.dirname(__get_launch_path())


try:
    LAUNCH_DIR = __get_launch_dir()  # launcher's dirpath
except:
    LAUNCH_DIR = normpath(os.getcwd())


# ------------------------------------------------------------------------------
# Path Finders (File Finders)

def _find_paths(
        dirpath: T.Path, path_type: int, recursive=False,
        prefix: T.Prefix = None, suffix: T.Suffix = None, filter_=None
) -> T.FinderReturn:
    """ General files/dirs finder.
    
    Args:
        dirpath:
        path_type: int[0, 1]. 0: file, 1: dir.
        suffix:
            1. each item must be string start with '.' ('.jpg', '.txt', etc.)
            2. case insensitive.
            3. param type is str or tuple[str], cannot be list[str].
        recursive:
        filter_: optional[function]
            None: no filter (everything pass through)
            function:
                def some_filter(filepath: str, filename: str) -> bool: ...
                returns True to accept the file, False to reject.
    
    Yields:
        tuple[str filepath, str filename]
    """
    dirpath = normpath(dirpath, force_abspath=True)
    for root, dirs, files in os.walk(dirpath):
        root = normpath(root)
        
        if path_type == 0:
            names = files
        else:
            names = dirs
        
        for n in names:
            p = f'{root}/{n}'
            if filter_ is not None and not filter_(p, n):
                continue
            if prefix and not n.startswith(prefix):
                continue
            if suffix and not n.endswith(suffix):
                continue
            yield p, n
        
        if not recursive:
            break


def find_files(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.FinderReturn:
    return _find_paths(
        dirpath, path_type=0, recursive=False, suffix=suffix, filter_=filter_
    )


''' discuss: why use "find_file_paths/_names" not "find_filepaths/filenames"?
    answer: for better code auto completion.
'''


def find_file_paths(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.Paths:
    return [m for m, _ in _find_paths(
        dirpath, path_type=0, recursive=False, suffix=suffix, filter_=filter_
    )]


def find_file_names(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.Names:
    return [n for _, n in _find_paths(
        dirpath, path_type=0, recursive=False, suffix=suffix, filter_=filter_
    )]


def findall_files(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.FinderReturn:
    return _find_paths(
        dirpath, path_type=0, recursive=True, suffix=suffix, filter_=filter_
    )


def findall_file_paths(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.Paths:
    return [m for m, _ in _find_paths(
        dirpath, path_type=0, recursive=True, suffix=suffix, filter_=filter_
    )]


def findall_file_names(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.Names:
    return [n for _, n in _find_paths(
        dirpath, path_type=0, recursive=True, suffix=suffix, filter_=filter_
    )]


def find_dirs(
        dirpath: T.Path, prefix=None, exclude_protected_folders=True
) -> T.FinderReturn:
    return _find_paths(
        dirpath, path_type=1, recursive=False, prefix=prefix,
        filter_=_default_dirs_filter if exclude_protected_folders else None
    )


def find_dir_paths(
        dirpath: T.Path, prefix=None, exclude_protected_folders=True
) -> T.Paths:
    return [m for m, _ in _find_paths(
        dirpath, path_type=1, recursive=False, prefix=prefix,
        filter_=_default_dirs_filter if exclude_protected_folders else None
    )]


def find_dir_names(
        dirpath: T.Path, prefix=None, exclude_protected_folders=True
) -> T.Paths:
    return [n for _, n in _find_paths(
        dirpath, path_type=1, recursive=False, prefix=prefix,
        filter_=_default_dirs_filter if exclude_protected_folders else None
    )]


def findall_dirs(
        dirpath: T.Path, prefix=None, exclude_protected_folders=True
) -> T.FinderReturn:
    return _find_paths(
        dirpath, path_type=1, recursive=True, prefix=prefix,
        filter_=_default_dirs_filter if exclude_protected_folders else None
    )


def findall_dir_paths(
        dirpath: T.Path, prefix=None, exclude_protected_folders=True
) -> T.Paths:
    return [m for m, _ in _find_paths(
        dirpath, path_type=1, recursive=True, prefix=prefix,
        filter_=_default_dirs_filter if exclude_protected_folders else None
    )]


def findall_dir_names(
        dirpath: T.Path, prefix=None, exclude_protected_folders=True
) -> T.Paths:
    return [n for _, n in _find_paths(
        dirpath, path_type=1, recursive=True, prefix=prefix,
        filter_=_default_dirs_filter if exclude_protected_folders else None
    )]


class ProtectedDirsFilter:
    
    def __init__(self):
        self._whitelist = set()
        self._blacklist = set()
    
    def reset(self):
        self._whitelist.clear()
        self._blacklist.clear()
    
    def __call__(self, path: T.Path, name: T.Name) -> bool:
        if path.startswith(tuple(self._whitelist)):
            self._whitelist.add(path + '/')
            return True
        elif path.startswith(tuple(self._blacklist)):
            self._blacklist.add(path + '/')
            return False
        
        if name.startswith(('.', '__', '~')):
            self._blacklist.add(path + '/')
            return False
        else:
            self._whitelist.add(path + '/')
            return True


_default_dirs_filter = ProtectedDirsFilter()


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
    if os.path.isfile(filepath):
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
    if os.path.isdir(dirpath):
        return True
    else:
        return False


def not_empty(file: T.FilePath) -> bool:
    """
    References:
        https://www.imooc.com/wenda/detail/350036?block_id=tuijian_yw
    """
    return bool(os.path.exists(file) and os.path.getsize(file))


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
        out = os.path.abspath(os.path.join(caller_dir, path))
    
    if force_abspath:
        return normpath(out)
    else:
        return normpath(os.path.relpath(out, os.getcwd()))


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
        return normpath(os.path.dirname(file))

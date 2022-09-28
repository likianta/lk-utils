import os
import typing as t
from dataclasses import dataclass

from .main import normpath


@dataclass
class PathKnob:
    dir: str
    path: str
    relpath: str
    name: str
    type: str
    
    @property
    def abspath(self) -> str:  # alias to 'path'
        return self.path
    
    @property
    def name_stem(self) -> str:
        return os.path.splitext(self.name)[0]


class T:
    Path = DirPath = FilePath = str
    Name = DirName = FileName = str
    Paths = DirPaths = FilePaths = t.List[Path]
    Names = DirNames = FileNames = t.List[Name]
    
    Prefix = Suffix = t.Union[None, str, t.Tuple[str, ...]]
    
    FinderReturn = t.Iterator[PathKnob]


def _find_paths(
        dirpath: T.Path, path_type: int, recursive=False,
        prefix: T.Prefix = None, suffix: T.Suffix = None, filter_=None
) -> T.FinderReturn:
    """
    args:
        path_type: int[0, 1]. 0: dir, 1: file.
        suffix:
            1. each item must be string start with '.' ('.jpg', '.txt', etc.)
            2. case insensitive.
            3. param type is str or tuple[str], cannot be list[str].
        filter_: optional[callable[str, str]]
            None: no filter (everything pass through)
            callable:
                def some_filter(filepath: str, filename: str) -> bool: ...
                return: True means filter out, False means pass through. (it's
                the same with `builtins.filter` function.)
    """
    dirpath = normpath(dirpath, force_abspath=True)
    for root, dirs, files in os.walk(dirpath):
        root = normpath(root)
        
        if path_type == 0:
            names = dirs
        else:
            names = files
        
        for n in names:
            p = f'{root}/{n}'
            if filter_ and filter_(p, n):
                continue
            if prefix and not n.startswith(prefix):
                continue
            if suffix and not n.endswith(suffix):
                continue
            yield PathKnob(
                dir=root,
                path=p,
                relpath=p[len(dirpath) + 1:],
                name=n,
                type='dir' if path_type == 0 else 'file',
            )
        
        if not recursive:
            break


# -----------------------------------------------------------------------------

def find_files(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.FinderReturn:
    return _find_paths(
        dirpath, path_type=1, recursive=False, suffix=suffix, filter_=filter_
    )


def find_file_paths(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.Paths:
    return [x.path for x in _find_paths(
        dirpath, path_type=0, recursive=False, suffix=suffix, filter_=filter_
    )]


def find_file_names(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.Paths:
    return [x.name for x in _find_paths(
        dirpath, path_type=0, recursive=False, suffix=suffix, filter_=filter_
    )]


def findall_files(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.FinderReturn:
    return _find_paths(
        dirpath, path_type=1, recursive=True, suffix=suffix, filter_=filter_
    )


def findall_file_paths(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.Paths:
    return [x.path for x in _find_paths(
        dirpath, path_type=0, recursive=True, suffix=suffix, filter_=filter_
    )]


def findall_file_names(
        dirpath: T.Path, suffix: T.Suffix = None, filter_=None
) -> T.Paths:
    return [x.name for x in _find_paths(
        dirpath, path_type=0, recursive=True, suffix=suffix, filter_=filter_
    )]


# -----------------------------------------------------------------------------

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
    return [x.path for x in _find_paths(
        dirpath, path_type=1, recursive=False, prefix=prefix,
        filter_=_default_dirs_filter if exclude_protected_folders else None
    )]


def find_dir_names(
        dirpath: T.Path, prefix=None, exclude_protected_folders=True
) -> T.Paths:
    return [x.name for x in _find_paths(
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
    return [x.path for x in _find_paths(
        dirpath, path_type=1, recursive=True, prefix=prefix,
        filter_=_default_dirs_filter if exclude_protected_folders else None
    )]


def findall_dir_names(
        dirpath: T.Path, prefix=None, exclude_protected_folders=True
) -> T.Paths:
    return [x.name for x in _find_paths(
        dirpath, path_type=1, recursive=True, prefix=prefix,
        filter_=_default_dirs_filter if exclude_protected_folders else None
    )]


# -----------------------------------------------------------------------------

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

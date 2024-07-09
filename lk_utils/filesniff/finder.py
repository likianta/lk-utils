"""
design guide: docs/filename-extension-form-in-design-thinking.zh.md
"""
import os
import re
from dataclasses import dataclass

from .main import normpath
from .. import common_typing as t

__all__ = [
    'Filter',
    'Path',
    'default_filter',
    'find_dir_names',
    'find_dir_paths',
    'find_dirs',
    'find_file_names',
    'find_file_paths',
    'find_files',
    'findall_dir_names',
    'findall_dir_paths',
    'findall_dirs',
    'findall_file_names',
    'findall_file_paths',
    'findall_files',
]


@dataclass
class Path:
    dir: str
    path: str
    relpath: str
    name: str
    type: t.Literal['dir', 'file']
    
    @property
    def abspath(self) -> str:  # alias to 'path'
        return self.path
    
    @property
    def stem(self) -> str:
        return os.path.splitext(self.name)[0]
    
    @property
    def ext(self) -> str:
        return os.path.splitext(self.name)[1][1:].lower()
    
    # make it sortable.
    def __lt__(self, other: 'Path') -> bool:
        return self.path < other.path


class PathType:
    FILE = 0
    DIR = 1


class T:
    _Path = Path
    
    DirPath = str
    Filter = t.Union[None, True, t.Iterable[str], 'Filter']
    FinderResult = t.Iterator[_Path]
    PathType = int
    
    Prefix = t.Union[str, t.Tuple[str, ...]]
    Suffix = t.Union[str, t.Tuple[str, ...]]
    #   suffix supported formats:
    #       '.png'
    #       ('.png', '.jpg')
    
    SortBy = t.Literal['name', 'path', 'time']


def _find_paths(
    dirpath: T.DirPath,
    path_type: T.PathType,
    recursive: bool = False,
    prefix: T.Prefix = None,
    suffix: T.Suffix = None,
    sort_by: T.SortBy = None,
    filter: T.Filter = None,
) -> T.FinderResult:
    """
    params:
        path_type: 0: file, 1: dir. see also `[class] PathType`.
        suffix:
            1. each item must be string start with '.' ('.jpg', '.txt', etc.)
            2. case insensitive.
            3. param type is str or tuple[str], cannot be list[str].
        filter:
            None: no filter.
            True: use default filter. it is equivalent to pass `default_filter`.
            Iterable[str]: will construct a Filter object.
            Filter: use the given Filter object.
            we usually use `None` or `True` for convenience.
    """
    dirpath = normpath(dirpath, force_abspath=True)
    if filter:
        if filter is True:
            filter = default_filter
        elif isinstance(filter, Filter):
            pass
        else:
            filter = Filter(filter)
        if path_type == PathType.FILE:
            filter = filter.filter_file
        else:
            filter = filter.filter_dir
    
    def main() -> T.FinderResult:
        for root, dirs, files in os.walk(dirpath, followlinks=True):
            root = normpath(root)
            
            if path_type == PathType.FILE:
                names = files
            else:
                names = dirs
            
            for n in names:
                p = f'{root}/{n}'
                if filter and filter(p, n, is_root=(root == dirpath)):
                    continue
                if prefix and not n.startswith(prefix):
                    continue
                if suffix and not n.endswith(suffix):
                    continue
                
                yield Path(
                    dir=root,
                    path=p,
                    relpath=p[len(dirpath) + 1:],
                    name=n,
                    type='dir' if path_type == PathType.DIR else 'file',  # noqa
                )
            
            if not recursive:
                break
    
    if sort_by is None:
        yield from main()
    elif sort_by == 'name':
        yield from sorted(main(), key=lambda x: x.name)
    elif sort_by == 'path':
        yield from sorted(main(), key=lambda x: x.path)
    elif sort_by == 'time':
        yield from sorted(main(), key=lambda x: os.path.getmtime(x.path),
                          reverse=True)  # fmt:skip
    else:
        raise ValueError(sort_by)


class Filter:
    def __init__(self, exclusions: t.Iterable[str]) -> None:
        """
        exclusions:
            use '^...' to create a regular expression.
        """
        regexes = set()
        statics = set()
        for rule in exclusions:
            if rule.startswith('^'):
                regexes.add(re.compile(rule[1:]))
            else:
                statics.add(rule)
        self._regexes = regexes
        # self._statics = tuple(statics)
        self._statics = statics
        self._blocked = set()
        self._allowed = set()
        
    def filter_file(self, filepath: str, filename: str, is_root: bool) -> bool:
        if filename in self._statics:
            return True
        for regex in self._regexes:
            if regex.match(filename):
                return True
        if is_root:
            return False
        else:
            dirpath = filepath[: -(len(filename) + 1)]
            dirname = dirpath.rsplit('/', 1)[-1]
            return self.filter_dir(dirpath, dirname)
    
    def filter_dir(self, dirpath: str, dirname: str, **_) -> bool:
        if dirpath in self._blocked:
            return True
        if dirpath in self._allowed:
            return False
        if dirname + '/' in self._statics:
            self._blocked.add(dirpath)
            return True
        for regex in self._regexes:
            if regex.match(dirname + '/'):
                self._blocked.add(dirpath)
                return True
        self._allowed.add(dirpath)
        return False


default_filter = Filter((
    '.idea/', '.git/', '.vscode/', '__pycache__/',
    '.DS_Store', '.gitkeep',
    '^~.+', '^.+~'
))


# -----------------------------------------------------------------------------


def find_files(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    **kwargs,
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.FILE,
        recursive=False,
        suffix=suffix,
        **kwargs,
    )


def find_file_paths(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    **kwargs,
) -> t.List[str]:
    return [
        x.path
        for x in _find_paths(
            dirpath,
            path_type=PathType.FILE,
            recursive=False,
            suffix=suffix,
            **kwargs,
        )
    ]


def find_file_names(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    **kwargs,
) -> t.List[str]:
    return [
        x.name
        for x in _find_paths(
            dirpath,
            path_type=PathType.FILE,
            recursive=False,
            suffix=suffix,
            **kwargs,
        )
    ]


def findall_files(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    **kwargs,
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.FILE,
        recursive=True,
        suffix=suffix,
        **kwargs,
    )


def findall_file_paths(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    **kwargs,
) -> t.List[str]:
    return [
        x.path
        for x in _find_paths(
            dirpath,
            path_type=PathType.FILE,
            recursive=True,
            suffix=suffix,
            **kwargs,
        )
    ]


def findall_file_names(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    **kwargs,
) -> t.List[str]:
    return [
        x.name
        for x in _find_paths(
            dirpath,
            path_type=PathType.FILE,
            recursive=True,
            suffix=suffix,
            **kwargs,
        )
    ]


# -----------------------------------------------------------------------------


def find_dirs(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    **kwargs,
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.DIR,
        recursive=False,
        prefix=prefix,
        **kwargs,
    )


def find_dir_paths(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    **kwargs,
) -> t.List[str]:
    return [
        x.path
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=False,
            prefix=prefix,
            **kwargs,
        )
    ]


def find_dir_names(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    **kwargs,
) -> t.List[str]:
    return [
        x.name
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=False,
            prefix=prefix,
            **kwargs,
        )
    ]


def findall_dirs(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    **kwargs,
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.DIR,
        recursive=True,
        prefix=prefix,
        **kwargs,
    )


def findall_dir_paths(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    **kwargs,
) -> t.List[str]:
    return [
        x.path
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=True,
            prefix=prefix,
            **kwargs,
        )
    ]


def findall_dir_names(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    **kwargs,
) -> t.List[str]:
    return [
        x.name
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=True,
            prefix=prefix,
            **kwargs,
        )
    ]

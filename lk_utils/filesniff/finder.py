"""
design guide: docs/filename-extension-form-in-design-thinking.zh.md
"""
import os
import re
import typing as t
from dataclasses import dataclass

from .main import normpath

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
    
    AnyFilter = t.Union[None, bool, t.Iterable[str], 'Filter']
    DirPath = str
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
    filter: T.AnyFilter = True,
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
            filter0 = default_filter
        elif isinstance(filter, Filter):
            filter0 = filter
        else:
            filter0 = Filter(filter)
        filter1 = (
            filter0.filter_file if path_type == PathType.FILE else
            filter0.filter_dir
        )
    else:
        filter0 = None
        filter1 = None
    # del filter
    
    def main() -> T.FinderResult:
        for root, dirs, files in os.walk(dirpath, followlinks=True):
            root = normpath(root)
            
            if root != dirpath and (
                filter0 and filter0.filter_dir(root, root.rsplit('/', 1)[-1])
            ):
                continue
            
            names = files if path_type == PathType.FILE else dirs
            for n in names:
                p = f'{root}/{n}'
                # noinspection PyArgumentList
                if filter1 and filter1(p, n):
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
        yield from sorted(
            main(), key=lambda x: os.path.getmtime(x.path), reverse=True
        )
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
        self._regexes = tuple(regexes)
        self._statics = frozenset(statics)
        self._blocked = set()
        self._allowed = set()
    
    # noinspection PyUnusedLocal
    def filter_file(self, path: str, name: str) -> bool:
        if name in self._statics:
            return True
        for regex in self._regexes:
            if regex.match(name):
                return True
        return False
    
    def filter_dir(self, path: str, name: str) -> bool:
        if path in self._blocked:
            return True
        if path.rsplit('/', 1)[0] in self._blocked:
            self._blocked.add(path)
            return True
        if path in self._allowed:
            return False
        if name + '/' in self._statics:
            self._blocked.add(path)
            return True
        for regex in self._regexes:
            if regex.match(name):
                self._blocked.add(path)
                return True
        self._allowed.add(path)
        return False


default_filter = Filter((
    '.git/', '.idea/', '.vscode/', '__pycache__/',
    '.DS_Store', '.gitkeep',
    '^~.+', '^.+~$'
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

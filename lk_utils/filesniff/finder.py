"""
design guide: docs/filename-extension-form-in-design-thinking.zh.md
"""
import os
from dataclasses import dataclass

from .main import normpath
from .. import common_typing as t

__all__ = [
    'Path',
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
    FinderResult = t.Iterator[_Path]
    PathFilter = t.Callable[[str, str], bool]
    #   callable[[abspath, name], bool]
    #       the abspath could either be a file or a dir.
    #       the name could either be a file or a dir.
    PathType = int
    
    Prefix = t.Union[str, t.Tuple[str, ...]]
    Suffix = t.Union[str, t.Tuple[str, ...]]
    #   DELETE: suffix supported formats:
    #       'png'
    #       '.png'
    #       '*.png'
    #       'png jpg'
    #       '.png .jpg'
    #       '*.png *.jpg'
    #       ('png', 'jpg', ...)
    #       ('.png', '.jpg', ...)
    #       ('*.png', '*.jpg', ...)
    #   (new) suffix supported formats:
    #       '.png'
    #       ('.png', '.jpg')
    
    SortBy = t.Literal['name', 'path', 'time']


def _find_paths(
    dirpath: T.DirPath,
    path_type: T.PathType,
    recursive: bool = False,
    prefix: T.Prefix = None,
    suffix: T.Suffix = None,
    filter: T.PathFilter = None,
    sort_by: T.SortBy = None,
) -> T.FinderResult:
    """
    args:
        path_type: 0: file, 1: dir. see also `[class] PathType`.
        suffix:
            1. each item must be string start with '.' ('.jpg', '.txt', etc.)
            2. case insensitive.
            3. param type is str or tuple[str], cannot be list[str].
        filter:
            None: no filter (everything pass through)
            callable:
                return: True means matched, False means dropped.
    """
    dirpath = normpath(dirpath, force_abspath=True)
    
    def main() -> T.FinderResult:
        for root, dirs, files in os.walk(dirpath):
            root = normpath(root)
            
            if path_type == PathType.FILE:
                names = files
            else:
                names = dirs
            
            for n in names:
                p = f'{root}/{n}'
                if filter and filter(p, n) is False:
                    continue
                if prefix and not n.startswith(prefix):
                    continue
                if suffix and not n.endswith(suffix):
                    continue
                
                yield Path(
                    dir=root,
                    path=p,
                    relpath=p[len(dirpath) + 1 :],
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


class _DefaultFilter:
    def __init__(self):
        self._whitelist = set()  # DELETE
        self._blacklist = set()
    
    def reset(self) -> None:
        self._whitelist.clear()
        self._blacklist.clear()
    
    """
    filter returns:
        True means accepted, False means rejected. (this is different with \
        python's built-in `filter` function)
    """
    
    def filter_file(self, filepath: str, filename: str) -> bool:
        if filepath.endswith('~'):  # e.g. '/path/to/file.py~'
            return False
        dirpath = filepath[: -(len(filename) + 1)]
        dirname = dirpath.rsplit('/', 1)[-1]
        if self.filter_dir(dirpath, dirname) is False:
            return False
        if filename.startswith(('.', '~')):
            return False
        return True
    
    def filter_dir(self, dirpath: str, dirname: str) -> bool:
        if dirpath in self._blacklist:
            return False
        if dirname.startswith(('.', '~', '__')):
            self._blacklist.add(dirpath)
            return False
        return True


_default_filter = _DefaultFilter()


# -----------------------------------------------------------------------------


def find_files(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    filter: T.PathFilter = _default_filter.filter_file,
    **kwargs,
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.FILE,
        recursive=False,
        suffix=suffix,
        filter=filter,
        **kwargs,
    )


def find_file_paths(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    filter: T.PathFilter = _default_filter.filter_file,
    **kwargs,
) -> t.List[str]:
    return [
        x.path
        for x in _find_paths(
            dirpath,
            path_type=PathType.FILE,
            recursive=False,
            suffix=suffix,
            filter=filter,
            **kwargs,
        )
    ]


def find_file_names(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    filter: T.PathFilter = _default_filter.filter_file,
    **kwargs,
) -> t.List[str]:
    return [
        x.name
        for x in _find_paths(
            dirpath,
            path_type=PathType.FILE,
            recursive=False,
            suffix=suffix,
            filter=filter,
            **kwargs,
        )
    ]


def findall_files(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    filter: T.PathFilter = _default_filter.filter_file,
    **kwargs,
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.FILE,
        recursive=True,
        suffix=suffix,
        filter=filter,
        **kwargs,
    )


def findall_file_paths(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    filter: T.PathFilter = _default_filter.filter_file,
    **kwargs,
) -> t.List[str]:
    return [
        x.path
        for x in _find_paths(
            dirpath,
            path_type=PathType.FILE,
            recursive=True,
            suffix=suffix,
            filter=filter,
            **kwargs,
        )
    ]


def findall_file_names(
    dirpath: T.DirPath,
    suffix: T.Suffix = None,
    filter: T.PathFilter = _default_filter.filter_file,
    **kwargs,
) -> t.List[str]:
    return [
        x.name
        for x in _find_paths(
            dirpath,
            path_type=PathType.FILE,
            recursive=True,
            suffix=suffix,
            filter=filter,
            **kwargs,
        )
    ]


# -----------------------------------------------------------------------------


def find_dirs(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    filter: T.PathFilter = _default_filter.filter_dir,
    **kwargs,
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.DIR,
        recursive=False,
        prefix=prefix,
        filter=filter,
        **kwargs,
    )


def find_dir_paths(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    filter: T.PathFilter = _default_filter.filter_dir,
    **kwargs,
) -> t.List[str]:
    return [
        x.path
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=False,
            prefix=prefix,
            filter=filter,
            **kwargs,
        )
    ]


def find_dir_names(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    filter: T.PathFilter = _default_filter.filter_dir,
    **kwargs,
) -> t.List[str]:
    return [
        x.name
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=False,
            prefix=prefix,
            filter=filter,
            **kwargs,
        )
    ]


def findall_dirs(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    filter: T.PathFilter = _default_filter.filter_dir,
    **kwargs,
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.DIR,
        recursive=True,
        prefix=prefix,
        filter=filter,
        **kwargs,
    )


def findall_dir_paths(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    filter: T.PathFilter = _default_filter.filter_dir,
    **kwargs,
) -> t.List[str]:
    return [
        x.path
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=True,
            prefix=prefix,
            filter=filter,
            **kwargs,
        )
    ]


def findall_dir_names(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    filter: T.PathFilter = _default_filter.filter_dir,
    **kwargs,
) -> t.List[str]:
    return [
        x.name
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=True,
            prefix=prefix,
            filter=filter,
            **kwargs,
        )
    ]

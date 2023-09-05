"""
design guide: docs/filename-extension-form-in-design-thinking.zh.md
"""
import os
import re
import typing as t
from dataclasses import dataclass

from .main import normpath

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


class PathType:
    FILE = 0
    DIR = 1


class T:
    _Path = Path
    
    DirPath = str
    Name = DirName = FileName = str
    
    FinderResult = t.Iterator[_Path]
    PathFilter = t.Callable[[DirPath, t.Union[DirName, FileName]], bool]
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


def _find_paths(
    dirpath: T.DirPath,
    path_type: T.PathType,
    recursive: bool = False,
    prefix: T.Prefix = None,
    suffix: T.Suffix = None,
    filter: T.PathFilter = None,
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
        
        if not recursive: break


# -----------------------------------------------------------------------------


# DELETE
def _norm_suffix(suffix: T.Suffix) -> t.Tuple[str, ...]:
    """
    normalize suffix.
    
    examples:
        'png' -> ('.png',)
        '.png' -> ('.png',)
        '*.png' -> ('.png',)
        'png jpg' -> ('.png', '.jpg')
        '.png .jpg' -> ('.png', '.jpg')
        '*.png *.jpg' -> ('.png', '.jpg')
        ('png', 'jpg') -> ('.png', '.jpg')
        ('.png', '.jpg') -> ('.png', '.jpg')
        ('*.png', '*.jpg') -> ('.png', '.jpg')
    """
    if isinstance(suffix, str):
        if ' ' in suffix:
            return tuple(
                '.' + x.lstrip('*.').lower() for x in re.split(r' +', suffix)
            )
        else:
            return ('.' + suffix.lstrip('*.').lower(),)
    elif isinstance(suffix, tuple):
        return tuple('.' + x.lstrip('*.').lower() for x in suffix)
    else:
        raise Exception('invalid type', type(suffix), suffix)


def find_files(
    dirpath: T.DirPath, suffix: T.Suffix = None, **kwargs
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.FILE,
        recursive=False,
        suffix=suffix,
        **kwargs,
    )


def find_file_paths(
    dirpath: T.DirPath, suffix: T.Suffix = None, **kwargs
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
    dirpath: T.DirPath, suffix: T.Suffix = None, **kwargs
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
    dirpath: T.DirPath, suffix: T.Suffix = None, **kwargs
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.FILE,
        recursive=True,
        suffix=suffix,
        **kwargs,
    )


def findall_file_paths(
    dirpath: T.DirPath, suffix: T.Suffix = None, **kwargs
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
    dirpath: T.DirPath, suffix: T.Suffix = None, **kwargs
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
    use_default_filter: bool = True,
    **kwargs,
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.DIR,
        recursive=False,
        prefix=prefix,
        filter=_default_dirs_filter if use_default_filter else None,
        **kwargs,
    )


def find_dir_paths(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    use_default_filter: bool = True,
    **kwargs,
) -> t.List[str]:
    return [
        x.path
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=False,
            prefix=prefix,
            filter=_default_dirs_filter if use_default_filter else None,
            **kwargs,
        )
    ]


def find_dir_names(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    use_default_filter: bool = True,
    **kwargs,
) -> t.List[str]:
    return [
        x.name
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=False,
            prefix=prefix,
            filter=_default_dirs_filter if use_default_filter else None,
            **kwargs,
        )
    ]


def findall_dirs(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    use_default_filter: bool = True,
    **kwargs,
) -> T.FinderResult:
    return _find_paths(
        dirpath,
        path_type=PathType.DIR,
        recursive=True,
        prefix=prefix,
        filter=_default_dirs_filter if use_default_filter else None,
        **kwargs,
    )


def findall_dir_paths(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    use_default_filter: bool = True,
    **kwargs,
) -> t.List[str]:
    return [
        x.path
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=True,
            prefix=prefix,
            filter=_default_dirs_filter if use_default_filter else None,
            **kwargs,
        )
    ]


def findall_dir_names(
    dirpath: T.DirPath,
    prefix: T.Prefix = None,
    use_default_filter: bool = True,
    **kwargs,
) -> t.List[str]:
    return [
        x.name
        for x in _find_paths(
            dirpath,
            path_type=PathType.DIR,
            recursive=True,
            prefix=prefix,
            filter=_default_dirs_filter if use_default_filter else None,
            **kwargs,
        )
    ]


# -----------------------------------------------------------------------------


class _ProtectedDirsFilter:
    def __init__(self):
        self._whitelist = set()
        self._blacklist = set()
    
    def reset(self) -> None:
        self._whitelist.clear()
        self._blacklist.clear()
    
    def __call__(self, path: T.DirPath, name: T.Name) -> bool:
        """
        return: True means accepted, False means rejected. (this is different \
            with python's built-in `filter` function)
        """
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


_default_dirs_filter = _ProtectedDirsFilter()

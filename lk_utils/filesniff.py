import os
from inspect import currentframe
from os import path as ospath


class T:
    import typing as _t
    
    File = str
    Dir = str
    
    Path = str  # file path or dir path
    NormPath = str  # normalized path, use only '/', and rstrip '/' in tail
    
    PathType = _t.Literal['file', 'dir']
    PathFormat = _t.Literal[
        'filepath', 'dirpath', 'path', 'filename', 'dirname', 'name', 'zip',
        'dict', 'list', 'dlist'
    ]
    
    FileName = str
    FilePath = NormPath
    
    _FileDict = _t.Dict[FilePath, FileName]
    _FileZip = _t.Iterable[_t.Tuple[FilePath, FileName]]
    _FileDualList = _t.Tuple[_t.List[FilePath], _t.List[FileName]]
    
    FileZip = _FileZip
    
    FinderReturn = _t.Union[
        _t.List[FilePath], _t.List[FileName],
        _FileDict, _FileZip, _FileDualList
    ]
    
    Suffix = _t.Union[str, tuple]


def normpath(path: T.Path) -> T.NormPath:
    """
    
    Examples:
        from            to
        -------------------
        ./              .
        ./a/b/          a/b
        ./a/b/c/../     a/b
    """
    return ospath.normpath(path).replace('\\', '/')


# ------------------------------------------------------------------------------

def get_dirname(path: T.Path) -> str:
    """ Return the directory name of path.
    
    Examples:
        path = 'a/b/c/d.txt' -> 'c'
        path = 'a/b/c' -> 'c'
    """
    if ospath.isfile(path):
        return ospath.basename(ospath.dirname(path))
    else:
        return ospath.basename(path)


def get_filename(path: T.Path, suffix=True, strict=False) -> T.NormPath:
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
    name = ospath.basename(path)
    if suffix:
        return name
    else:
        return ospath.splitext(name)[0]


def __get_launch_path() -> T.NormPath:
    """ Get launcher's filepath.
    
    Example:
        sys.argv: ['D:/myprj/src/main.py', ...] -> 'D:/myprj/src/main.py'
    """
    from sys import argv
    path = ospath.abspath(argv[0])
    if ospath.isfile(path):
        return normpath(path)
    else:
        raise Exception


def __get_launch_dir() -> T.NormPath:
    return ospath.dirname(__get_launch_path())


try:
    LAUNCH_DIR = __get_launch_dir()  # launcher's dirpath
except:
    LAUNCH_DIR = normpath(os.getcwd())


# ------------------------------------------------------------------------------
# Path Finders (File Finders)

def _find_paths(dir_: T.Path, path_type: T.PathType, fmt: T.PathFormat,
                suffix: T.Suffix = '', recursive=False,
                custom_filter=None) -> T.FinderReturn:
    """ Basic find.
    
    Args:
        dir_: target path to find in.
        path_type: 'file'|'dir'.
        fmt:
        suffix: assign a filter to which file types we want to fetch.
            NOTICE:
                1. Each suffix name must start with a dot ('.jpg', '.txt', etc.)
                2. Case sensitive
                3. Param type is str or tuple, cannot be list
        recursive: whether to find descendant folders.
        custom_filter:
            自定义一个过滤函数. 您需确保该函数只有一个参数, 类型为
            `_TFileZip`. 其返回结果必须同样为 `_TFileZip`.
            Usages see `find_dirs`, `findall_dirs`.
    
    Returns:
        fmt: 'filepath'|'dirpath'|'path'    ->  return [filepath, ...]
        fmt: 'filename'|'dirname'|'name'    ->  return [filename, ...]
        fmt: 'zip'          ->  return zip([filepath, ...], [filename, ...])
        fmt: 'dict'         ->  return {filepath: filename, ...}
        fmt: 'dlist'|'list' ->  return ([filepath, ...], [filename, ...])
    """
    dir_ = normpath(dir_)
    
    # recursive
    if recursive is False:
        names = os.listdir(dir_)
        paths = (f'{dir_}/{f}' for f in names)
        out = zip(paths, names)
        if path_type == 'file':
            out = filter(lambda x: ospath.isfile(x[0]), out)
        else:
            out = filter(lambda x: ospath.isdir(x[0]), out)
    else:
        names = []
        paths = []
        for root, dirnames, filenames in os.walk(dir_):
            root = normpath(root)
            if path_type == 'file':
                names.extend(filenames)
                paths.extend((f'{root}/{f}' for f in filenames))
            else:
                names.extend(dirnames)
                paths.extend((f'{root}/{d}' for d in dirnames))
        out = zip(paths, names)
    
    _not_empty = bool(names)
    #   True: not empty; False: empty (no paths found)
    
    if _not_empty:
        # suffix
        if suffix:
            out = filter(lambda x: x[1].endswith(suffix), out)
        
        # custom_filter
        if custom_filter:
            out = custom_filter(out)
    
    # fmt
    if fmt in ('filepath', 'dirpath', 'path'):
        return [fp for (fp, fn) in out]
    elif fmt in ('filename', 'dirname', 'name'):
        return [fn for (fp, fn) in out]
    elif fmt == 'zip':
        return out
    elif fmt == 'dict':
        return dict(out)
    elif fmt in ('dlist', 'list'):
        return zip(*out) if _not_empty else ([], [])
    else:
        raise ValueError('Unknown format', fmt)


def find_files(dir_: T.Path, *, fmt: T.PathFormat = 'filepath',
               suffix: T.Suffix = ''):
    return _find_paths(dir_, 'file', fmt, suffix, False)


def find_filenames(dir_: T.Path, *, suffix: T.Suffix = ''):
    return _find_paths(dir_, 'file', 'filename', suffix, False)


def findall_files(dir_: T.Path, *, fmt: T.PathFormat = 'filepath',
                  suffix: T.Suffix = ''):
    return _find_paths(dir_, 'file', fmt, suffix, True)


def find_dirs(dir_: T.Path, *, fmt: T.PathFormat = 'dirpath',
              suffix: T.Suffix = '', exclude_protected_folders=True):
    return _find_paths(
        dir_, 'dir', fmt, suffix, False,
        custom_filter=__exclude_protected_folders
        if exclude_protected_folders else None
    )


def findall_dirs(dir_: T.Path, *, fmt: T.PathFormat = 'dirpath',
                 suffix: T.Suffix = '', exclude_protected_folders=True):
    """
    Refer: https://www.cnblogs.com/bigtreei/p/9316369.html
    """
    return _find_paths(
        dir_, 'dir', fmt, suffix, True,
        custom_filter=__exclude_protected_folders
        if exclude_protected_folders else None
    )


def __exclude_protected_folders(path_zip: T.FileZip) -> T.FileZip:
    """
    see `func:_find_paths:params:custom_filter:docstring`.
    """
    discard_paths = set()
    out = []
    
    for filepath, filename in path_zip:
        if filepath.startswith(tuple(discard_paths)):
            discard_paths.add(filepath + '/')
        elif filename.startswith(('.', '__')):
            discard_paths.add(filepath + '/')
        else:
            out.append((filepath, filename))
    
    del discard_paths
    return out


# alias
find_subdirs = find_dirs
findall_subdirs = findall_dirs


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


def currdir() -> T.NormPath:
    caller_frame = currentframe().f_back
    return _get_dir_info_from_caller(caller_frame)


def relpath(path: T.Path, ret_abspath=True) -> T.NormPath:
    """ Consider relative path always based on caller's.
    
    References: https://blog.csdn.net/Likianta/article/details/89299937
    """
    caller_frame = currentframe().f_back
    caller_dir = _get_dir_info_from_caller(caller_frame)
    
    if path in ('', '.', './'):
        out = caller_dir
    else:
        out = ospath.abspath(ospath.join(caller_dir, path))
    
    if ret_abspath:
        return normpath(out)
    else:
        return normpath(ospath.relpath(out, os.getcwd()))


def _get_dir_info_from_caller(frame) -> T.NormPath:
    file = frame.f_globals.get('__file__') \
           or frame.f_code.co_filename
    if file.startswith('<') and file.endswith('>'):
        print(':v4', 'Unable to get dir info from caller frame! Fallback to '
                     'use current working directory.')
        return normpath(os.getcwd())
    else:
        return normpath(ospath.dirname(file))

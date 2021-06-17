import os
import sys
from os import path as ospath

from .typehint.filesniff import *


def normpath(path: TPath, ex=False) -> TNormPath:
    if ex:  # ex: 'enhance mode'. e.g. 'a/b/c/..' -> 'a/b'
        return ospath.abspath(path).replace('\\', '/').rstrip('/')
    else:
        return path.replace('\\', '/').rstrip('/')


# ------------------------------------------------------------------------------

def get_dirname(path: TPath) -> str:
    """ Return the directory name of path.
    
    Examples:
        path = 'a/b/c/d.txt' -> 'c'
        path = 'a/b/c' -> 'c'
    """
    nodes = path.split('/')
    if isfile(path):
        return nodes[-2]
    else:
        return nodes[-1]


def get_filename(path: TPath, suffix=True, strict=False) -> TNormPath:
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
    name = ospath.split(normpath(path))[-1]
    if suffix:
        return name
    else:
        return ospath.splitext(name)[0]


def __get_launch_path() -> TNormPath:
    """ Get launcher's filepath.
    
    Example:
        sys.argv: ['D:/myprj/src/main.py', ...] -> 'D:/myprj/src/main.py'
    """
    path = ospath.abspath(sys.argv[0])
    if ospath.isfile(path):
        return normpath(path)
    else:
        raise Exception(sys.argv)


def __get_launch_dir() -> TNormPath:
    return ospath.dirname(__get_launch_path())


try:
    MAINDIR = __get_launch_dir()  # launcher's dirpath
except:
    MAINDIR = normpath(os.getcwd())


# ------------------------------------------------------------------------------
# Path Finders (File Finders)

def _find_paths(dir_: TPath, path_type: TPathType, fmt: TPathFormat,
                suffix: TSuffix = '', recursive=False,
                custom_filter=None) -> TFinderReturn:
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
        custom_filter: if you want a more powerful filter than `suffix`
            param, set it here. The `custom_filter` works after `suffix` filter.
            Usages see `find_subdirs()`, `findall_subdirs()`.
    
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
            out = filter(custom_filter, out)
    
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
        return zip(*out) if _not_empty else (None, None)
    else:
        raise ValueError('Unknown format', fmt)


def find_files(dir_: TPath, *, fmt: TPathFormat = 'filepath',
               suffix: TSuffix = ''):
    return _find_paths(dir_, 'file', fmt, suffix, False)


def find_filenames(dir_: TPath, *, suffix: TSuffix = ''):
    return _find_paths(dir_, 'file', 'filename', suffix, False)


def findall_files(dir_: TPath, *, fmt: TPathFormat = 'filepath',
                  suffix: TSuffix = ''):
    return _find_paths(dir_, 'file', fmt, suffix, True)


def find_dirs(dir_: TPath, *, fmt: TPathFormat = 'dirpath',
              suffix: TSuffix = '', exclude_protected_folder=True):
    return _find_paths(
        dir_, 'dir', fmt, suffix, False,
        lambda x: __exclude_protected_folders(x, normpath(dir_))
        if exclude_protected_folder else None
    )


def findall_dirs(dir_: TPath, *, fmt: TPathFormat = 'dirpath',
                 suffix: TSuffix = '', exclude_protected_folder=True):
    """
    Refer: https://www.cnblogs.com/bigtreei/p/9316369.html
    """
    return _find_paths(
        dir_, 'dir', fmt, suffix, True,
        lambda x: __exclude_protected_folders(x, normpath(dir_))
        if exclude_protected_folder else None
    )


def __exclude_protected_folders(path_and_name, root=''):
    filepath, filename = path_and_name  # type: str
    if filename.startswith(('.', '__')):
        return False
    if any(part.startswith(('.', '__'))
           for part in filepath.replace(root, '', 1).split('/')):
        return False
    return True


# alias
find_subdirs = find_dirs
findall_subdirs = findall_dirs


# ------------------------------------------------------------------------------

def isfile(filepath: TPath) -> bool:
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


def isdir(dirpath: TPath) -> bool:
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


def relpath(path: TPath, caller_file='') -> TNormPath:
    """ Consider relative path always based on caller's.
    
    References: https://blog.csdn.net/Likianta/article/details/89299937
    
    Args:
        path: This param name makes a trick that when we call the function in
            Pycharm, Pycharm will consider the first argument as a file-like
            param (bacause of the param name), thus Pycharm gives us path hint
            when we type into strings.
        caller_file: Literal[__file__, '']. Recommended passing `__file__` as
            argument. It will be faster than passing an empty string.
    """
    if caller_file == '':
        # noinspection PyProtectedMember, PyUnresolvedReferences
        frame = sys._getframe(1)
        caller_file = frame.f_code.co_filename
    caller_dir = ospath.dirname(caller_file)
    return normpath(f'{caller_dir}/{path}', ex=True)


# ------------------------------------------------------------------------------
# Other

def dialog(dir_: TPath, suffix,
           prompt='请选择您所需文件的对应序号') -> TNormPath:
    """ File select dialog (Chinese). """
    print(f'当前目录为: {dir_}')
    
    # fp: filepaths, fn: filenames
    fp, fn = find_files(dir_, fmt='list', suffix=suffix)
    
    if not fn:
        raise FileNotFoundError(f'当前目录没有找到目标类型 ({suffix}) 的文件')
    
    elif len(fn) == 1:
        print(f'当前目录找到了一个目标类型的文件: {fn[0]}')
        return fp[0]
    
    else:
        x = ['{} | {}'.format(i, j) for i, j in enumerate(fn)]
        print('当前目录找到了多个目标类型的文件:'
              '\n\t{}'.format('\n\t'.join(x)))
        
        if not prompt.endswith(': '):
            prompt += ': '
        index = input(prompt)
        return fp[int(index)]


def mkdirs(path: TPath, exist_ok=True):  # DELETE
    os.makedirs(path, exist_ok=exist_ok)
    # # dirpath = (nodes := path.split('/'))[0]
    # # for node in nodes[1:]:
    # #     dirpath += '/' + node
    # #     if not ospath.exists(dirpath):
    # #         os.mkdir(dirpath)

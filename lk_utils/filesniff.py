"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : filesniff.py
@Created : 2018-00-00
@Updated : 2021-02-17
@Version : 1.9.3
@Desc    : Obtain files more easily.
    
Notes:
    1. 本模块优先接受使用正斜杠
    2. 本模块优先返回文件 (夹) 的绝对路径
"""
import os
import sys

from os import path as ospath

from ._typing import FilesniffHint as Hint


# ------------------------------------------------------------------------------
# Prettifiers

def prettify_dir(dirpath: str) -> str:
    if '\\' in dirpath:
        dirpath = dirpath.replace('\\', '/').rstrip('/')
        if dirpath == '.' or dirpath == '..': 
            dirpath += '/'
        return dirpath
    else:
        return dirpath


def prettify_file(filepath: str) -> str:
    if '\\' in filepath: 
        return filepath.replace('\\', '/')
    else:
        return filepath


prettify_path = prettify_file


# ------------------------------------------------------------------------------
# Path Getters

def get_dirname(path: str) -> str:
    """ Return the directory name from path.
    
    Args:
        path: filepath or dirpath
    
    Notes:
        该函数与 ospath.dirname 的处理方式不同.

    Examples:
        path = 'a/b/c/d.txt' -> return 'c'
        path = 'a/b/c' -> return 'c'
    """
    segs = prettify_path(path).split('/')
    if is_file_like(path):
        return segs[-2]
    else:
        return segs[-1]
    

def get_filename(path: str, suffix=True, strict=True) -> str:
    """ Return the file name from path.
    
    Examples:
        args: suffix = True, strict = False
            path = 'a/b/c/d.txt' -> return 'd.txt'
            path = 'a/b/c' -> strict is False -> return 'c' (假定它是无后缀的文件)
                           -> strict is True -> raise Error  
    """
    if strict and is_dir_like(path):
        raise ValueError('Path must be a file path, not directory!')
    name = ospath.split(path)[1]
    if suffix:
        return name
    else:
        return ospath.splitext(name)[0]


def __get_launch_path() -> str:
    """ Get launcher's filepath.
    
    Note: this method only works in Pycharm.
    
    Returns:
        Example:
            sys.argv: ['D:/myprj/src/main.py', ...] -> 'D:/myprj/src/main.py'
    """
    path = ospath.abspath(sys.argv[0])
    return prettify_file(path)


def __get_launch_dir() -> str:
    """ Get launcher's dirpath.
    
    Note: this method only works in Pycharm.
    
    Returns:
        Example:
            launcher: 'D:/myprj/src/main.py' -> 'D:/myprj/src'
    """
    dirpath = ospath.split(__get_launch_path())[0]
    return prettify_dir(dirpath)


def __get_prj_dir(working_dir=''):
    """ Get project dirpath.
    
    Note: This method only works in Pycharm.
    
    When script launched in Pycharm, the `sys.path[1]` is project's dirpath.
    If script launched in cmd or exe (pyinstaller), `_get_launch_dir()` is
    project's dirpath.
    """
    if working_dir:
        dirpath = prettify_dir(ospath.abspath(working_dir))
        # assert prj dirpath is launcher's parent path or launcher's itself.
        assert __get_launch_dir().startswith(dirpath), \
            'Something wrong with `working_dir` (if you passed it)'
    else:
        dirpath = __get_launch_dir()
    return dirpath


CURRDIR = __get_launch_dir()  # launcher's dirpath
PRJDIR = __get_prj_dir()  # project's dirpath
#   assert CURRDIR == PRJDIR or CURRDIR.startswith(PRJDIR)


# ------------------------------------------------------------------------------
# Listing Paths

def _find_paths(rootdir: str, path_type: str, suffix: Hint.Suffix, fmt: str,
                recursive=False, custom_filter=None) -> Hint.FinderReturn:
    """ Basic find.
    
    Args:
        rootdir: directory entrance
        path_type: 'file'|'dir'.
        suffix: str|tuple. assign a filter to which file types we want to fetch.
            注意:
                1. each suffix name must start with a dot ('.jpg', '.txt', etc.)
                2. case sensitive
                3. type cannot be list
                4. 如果不需要限定后缀, 则传入空字符串或 None
        fmt: 定义要返回的数据格式. 可选值见 `docstring:Returns` 中的说明
        recursive: whether to find descendant folders.
        custom_filter: function. 传入您自定义的过滤器. 
            示例: 参考 `find_dirs`, `findall_dirs`.
    
    Returns:
        取决于 args:fmt 的值:
            | args:fmt                          | return                       |
            | --------------------------------- | ---------------------------- |
            | 'filepath' or 'dirpath' or 'path' | [filepath, ...]              |
            | 'filename' or 'dirname' or 'name' | [filename, ...]              |
            | 'zip'                    | zip([filepath, ...], [filename, ...]) |
            | 'dict'                   | {filepath: filename, ...}             |
            | 'dlist' or 'list'        | ([filepath, ...], [filename, ...])    |
    """
    rootdir = prettify_dir(rootdir)
    
    # 1. args:recursive
    if recursive is False:
        names = os.listdir(rootdir)
        paths = (f'{rootdir}/{f}' for f in names)
        out = zip(paths, names)
        if path_type == 'file':
            out = filter(lambda x: ospath.isfile(x[0]), out)
        else:
            out = filter(lambda x: ospath.isdir(x[0]), out)
    else:
        names = []
        paths = []
        for root, dirnames, filenames in os.walk(rootdir):
            root = prettify_dir(root)
            if path_type == 'file':
                names.extend(filenames)
                paths.extend((f'{root}/{f}' for f in filenames))
            else:
                names.extend(dirnames)
                paths.extend((f'{root}/{d}' for d in dirnames))
        out = zip(paths, names)
    
    if len(names) > 0:
        # 2. args:suffix
        if suffix:
            out = filter(lambda x: x[1].endswith(suffix), out)
        
        # 3. args:custom_filter
        if custom_filter is not None:
            out = filter(custom_filter, out)
    
    # 4. args:fmt
    if fmt in ('filepath', 'dirpath', 'path'):
        return [fp for (fp, fn) in out]
    elif fmt in ('filename', 'dirname', 'name'):
        return [fn for (fp, fn) in out]
    elif fmt == 'zip':
        return out
    elif fmt == 'dict':
        return dict(out)
    elif fmt in ('double_list', 'dlist', 'list'):
        return zip(*out) if len(names) > 0 else ([], [])
    else:
        raise ValueError('Unknown return format', fmt)


def find_files(idir, suffix='', fmt='filepath'):
    return _find_paths(idir, path_type='file', suffix=suffix, 
                       fmt=fmt, recursive=False)


def find_filenames(idir, suffix=''):
    return _find_paths(idir, path_type='file', suffix=suffix,
                       fmt='filename', recursive=False)


def findall_files(idir, suffix='', fmt='filepath'):
    return _find_paths(idir, path_type='file', suffix=suffix,
                       fmt=fmt, recursive=True)


def find_dirs(idir, suffix='', fmt='dirpath',
              exclude_protected_folders=True):
    """
    Args:
        idir
        suffix
        fmt
        exclude_protected_folders: exclude folders which startswith "." or "__".
            Example:
                ".git", "__pycache__", "~temp", "$system", etc.
    """
    
    def _filter(x):
        return not bool(x[1].startswith(('.', '__', '$', '~')))
        #   x[1] indicates to 'filename'
    
    return _find_paths(
        idir, path_type='dir', suffix=suffix, fmt=fmt, recursive=False,
        custom_filter=_filter if exclude_protected_folders else None
    )


def findall_dirs(idir, fmt='dirpath', suffix='',
                 exclude_protected_folders=True):
    """
    References: https://www.cnblogs.com/bigtreei/p/9316369.html
    """
    
    def _filter(x):
        return not bool(x[1].startswith(('.', '__', '$', '~')))
        #   x[1] indicates to 'filename'
    
    return _find_paths(
        idir, path_type='dir', suffix=suffix, fmt=fmt, recursive=True,
        custom_filter=_filter if exclude_protected_folders else None
    )


# ------------------------------------------------------------------------------
# Path Checking

def is_file_like(path: str) -> bool:
    """ If `filepath` looks like a filepath, will return True; otherwise return 
        False.
    
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
    if path == '':
        return False
    if path.endswith('/'):
        return False
    if ospath.isfile(path):
        return True
    if '.' in path.rsplit('/', 1)[-1]:
        return True
    else:
        return False


def is_dir_like(path: str) -> bool:
    """ If `dirpath` looks like a dirpath, will return True; otherwise return
        False.
    
    Judgement based:
        - Is it a dot/dot-slash/slash? -> True
        - Does it really exist on system? -> True
        - Does it end with '/'? -> False
    """
    if path == '':
        return False
    if path in ('.', './', '/'):
        return True
    if ospath.isdir(path):
        return True
    else:
        return False


# ------------------------------------------------------------------------------
# Path Getters 2

def _calc_path(base: str, offset: str) -> str:
    """ Calculate path by relative offset.
    
    Examples:
        base = 'D:/myprj', offset = 'model/sample.txt'
         -> return f'{base}/{offset}' -> i.e. 'D:/myprj/model/sample.txt'
         
    Args:
        base: absolute path
        offset: relative path (offset) to `base`
    """
    if offset.startswith('./'):
        return f'{base}/{offset[2:]}'
    elif not offset.startswith('../'):
        return f'{base}/{offset}'
    else:
        segs1, segs2 = base.split('/'), offset.split('/')
        move_cnt = offset.count('..')
        return '/'.join(segs1[:-move_cnt] + segs2[move_cnt:])


def path_on_prj(offset: str) -> str:
    """ Calculate path based on PRJDIR as pivot.
    
    Example:
        PRJDIR = 'D:/myprj', path = 'src/main.py' -> 'D:/myprj/src/main.py'
    """
    return _calc_path(PRJDIR, offset)


def relpath(file: str, caller='') -> str:
    """ Consider relative path always based on caller's.
    
    Args:
        file: the target path. 
            注意这个参数的名字不要变更. 这是因为 Pycharm 会把 'file' 识别为一个 "文
            件相关的参数", 并提供给我们智能提示; 使用其他参数名不会有此特性.
        caller: __file__|''. Recommended passing `__file__` as argument. It
            will be faster than passing an empty string.
    
    References: https://blog.csdn.net/Likianta/article/details/89299937
    """
    # 1. target_path
    target_path = file
    # 2. caller_dir
    if caller == '':
        # noinspection PyProtectedMember, PyUnresolvedReferences
        frame = sys._getframe(1)
        caller = frame.f_code.co_filename
    caller_dir = ospath.abspath(f'{caller}/../')
    # 3. get relative path of target_path started from caller_dir
    return prettify_path(ospath.relpath(target_path, caller_dir))


# ------------------------------------------------------------------------------
# Other

def dialog(idir: str, suffix, prompt='请选择您所需文件的对应序号') -> str:
    """ File select dialog (Chinese). """
    print(f'当前目录为: {idir}')
    
    # fp: 'filepaths', fn: 'filenames'
    fp, fn = find_files(idir, suffix=suffix, fmt='dlist')
    
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


def force_create_dirpath(path: str):
    path = prettify_path(path)
    dirpath = (nodes := path.split('/'))[0]
    for node in nodes[1:]:
        dirpath += '/' + node
        if not ospath.exists(dirpath):
            os.mkdir(dirpath)

import os
import shutil
import typing as t
import urllib.request
from collections import namedtuple
from datetime import datetime
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile
from zipfile import ZipInfo

from . import main
from .finder import findall_dirs
from .finder import findall_files
from .main import IS_WINDOWS  # noqa
from .main import abspath
from .main import basename
from .main import dirname
from .main import exist
from .main import real_exist
from .main import xpath
from ..subproc import run_cmd_args
from ..textwrap import dedent

__all__ = [
    'clone_tree',
    'copy_file',
    'copy_tree',
    'download',
    'make_dir',
    'make_dirs',
    'make_file',
    'make_link',
    'make_links',
    'make_shortcut',
    'move',
    'move_file',
    'move_tree',
    'remove',
    'remove_file',
    'remove_tree',
    'unzip',
    'unzip_file',
    'zip',
    'zip_dir',
]

_ProgressItem = namedtuple('ProgressItem', 'total index percent text')

class T:
    AnyProgress = t.Optional[t.Union[t.Callable[[_ProgressItem], None], bool]]
    OverwriteScheme = t.Optional[bool]


def clone_tree(src: str, dst: str, overwrite: T.OverwriteScheme = None) -> None:
    if exist(dst):
        if any(os.listdir(dst)):
            if _overwrite(dst, overwrite):
                os.mkdir(dst)
            else:
                return
    else:
        os.mkdir(dst)
    for d in findall_dirs(src):
        dp_o = f'{dst}/{d.relpath}'
        if not exist(dp_o):
            os.mkdir(dp_o)


def copy_file(
    src: str,
    dst: str,
    overwrite: T.OverwriteScheme = None,
    reserve_metadata: bool = False,
) -> None:
    if exist(dst) and not _overwrite(dst, overwrite):
        return
    if reserve_metadata:
        shutil.copy2(src, dst)
    else:
        shutil.copyfile(src, dst)


def copy_tree(
    src: str,
    dst: str,
    overwrite: T.OverwriteScheme = None,
    symlinks: bool = False,
    reserve_metadata: bool = True,
) -> None:
    if exist(dst) and not _overwrite(dst, overwrite):
        return
    shutil.copytree(
        _safe_long_path(src),
        _safe_long_path(dst),
        copy_function=shutil.copy2 if reserve_metadata else shutil.copy,
        symlinks=symlinks
    )


def download(
    url: str,
    path: str, 
    extract: bool = False,
    keep_file: bool = False,
    progress: T.AnyProgress = None,
    overwrite: T.OverwriteScheme = None,
) -> None:
    """
    params:
        keep_file: whether to keep zip file after extracting.
    """
    if exist(path) and not _overwrite(path, overwrite):
        return
    
    url = url.replace(' ', '%20')
    
    if progress is True:
        def _report(count, block_size, total_size):
            assert total_size > 0, (url, path)
            _show_progress_in_console(total_size, block_size * count)
    elif progress:
        def _report(count, block_size, total_size):
            assert total_size > 0, (url, path)
            progress(
                _ProgressItem(
                    total_size,
                    block_size * count,
                    block_size * count / total_size,
                    ''
                )
            )
    else:
        _report = None

    if extract:
        assert url.endswith(('.zip', '.7z'))
        #   if assertion error, a workaround is setting `extract=False` then
        #   using `unzip_file()` function afterwards.
        ext = url.rsplit('.', 1)[-1]
        temp_file = '{}.tmp.{}'.format(path, ext)
        urllib.request.urlretrieve(url, temp_file, _report)
        unzip_file(temp_file, path)
        if not keep_file:
            remove_file(temp_file)
    else:
        urllib.request.urlretrieve(url, path, _report)


def make_dir(dst: str) -> None:
    if not exist(dst):
        os.mkdir(dst)


def make_dirs(dst: str) -> None:
    os.makedirs(dst, exist_ok=True)


def make_file(dst: str) -> None:
    open(dst, 'w').close()


def make_link(src: str, dst: str, overwrite: T.OverwriteScheme = None) -> str:
    """
    ref: https://blog.walterlv.com/post/ntfs-link-comparisons.html
    """
    src, dst = abspath(src), abspath(dst)
    
    assert real_exist(src), src
    if exist(dst):
        if overwrite is True:  # noqa
            if real_exist(dst) and os.path.samefile(src, dst):
                return dst
            else:
                remove(dst)
        elif overwrite is False:
            raise FileExistsError(dst)
        elif overwrite is None:
            return dst
    
    if IS_WINDOWS:
        if main.system_privileged is True:
            os.symlink(src, dst, target_is_directory=os.path.isdir(src))
        elif main.system_privileged is False:
            _make_link_fallback(src, dst)
        else:  # None type. only first-time calling reaches this case.
            try:
                os.symlink(src, dst, target_is_directory=os.path.isdir(src))
            except OSError as e:
                # print(':v8p', e)
                if 'WinError 1314' in str(e):
                    # https://docs.python.org/3/library/os.html#os.symlink
                    print(':pv6', 'fallback symlink with no privileges')
                    main.system_privileged = False
                    _make_link_fallback(src, dst)
                    return dst
                raise e
            else:
                main.system_privileged = True
    
    return dst


def _make_link_fallback(src: str, dst: str) -> None:
    """
    this function doesn't require administrative privileges.
    note: `src` and `dst` must be absolute paths.
    related:
        https://docs.python.org/3/library/os.html#os.symlink
        https://discuss.python.org/t/add-os-junction-pathlib-path-junction-to
        /50394
    """
    src = src.replace('/', '\\')
    dst = dst.replace('/', '\\')
    if os.path.isdir(src):  # directory junction for dirs
        run_cmd_args(('mklink', '/J', dst, src), shell=True)
    else:  # hard link for files
        run_cmd_args(('mklink', '/H', dst, src), shell=True)


def make_links(
    src: str,
    dst: str,
    names: t.List[str] = None,
    overwrite: T.OverwriteScheme = None
) -> t.List[str]:
    out = []
    for n in names or os.listdir(src):
        out.append(make_link(f'{src}/{n}', f'{dst}/{n}', overwrite))
    return out


def make_shortcut(
    src: str,
    dst: str = None,
    overwrite: T.OverwriteScheme = None
) -> None:
    """
    use batch script to create shortcut, no pywin32 required.
    
    params:
        dst:
            if not given, will create a shortcut in the same folder as `src`, -
            with the same base name.
            trick: use "<desktop>" to create a shortcut on the desktop.
    
    refs:
        https://superuser.com/questions/455364/how-to-create-a-shortcut
        -using-a-batch-script
        https://www.blog.pythonlibrary.org/2010/01/23/using-python-to-create
        -shortcuts/
    """
    if exist(dst) and not _overwrite(dst, overwrite):
        return
    if not IS_WINDOWS:
        raise NotImplementedError
    
    assert exist(src) and not src.endswith('.lnk')
    if not dst:
        dst = os.path.splitext(os.path.basename(src))[0] + '.lnk'
    else:
        assert dst.endswith('.lnk')
        if '<desktop>' in dst:
            dst = dst.replace('<desktop>', os.path.expanduser('~/Desktop'))
    
    vbs = xpath('./_temp_shortcut_generator.vbs')
    with open(vbs, 'w') as f:
        f.write(dedent(
            '''
            Set objWS = WScript.CreateObject("WScript.Shell")
            lnkFile = "{file_o}"
            Set objLink = objWS.CreateShortcut(lnkFile)
            objLink.TargetPath = "{file_i}"
            objLink.Save
            '''
        ).format(
            file_i=src.replace('/', '\\'),
            file_o=dst.replace('/', '\\'),
        ))
    run_cmd_args('cscript', '/nologo', vbs)
    os.remove(vbs)


# def merge_tree(src: str, dst: str, overwrite: bool = False) -> None:
#     if overwrite:  # TODO
#         raise NotImplementedError
#     src_dirs = frozenset(x.relpath for x in findall_dirs(src))
#     src_files = frozenset(x.relpath for x in findall_files(src))
#     dst_dirs = frozenset(x.relpath for x in findall_dirs(dst))
#     dst_files = frozenset(x.relpath for x in findall_files(dst))
#     # TODO


def move(src: str, dst: str, overwrite: T.OverwriteScheme = None) -> None:
    if exist(dst) and not _overwrite(dst, overwrite):
        return
    shutil.move(src, dst)


move_file = move
move_tree = move


def remove(dst: str) -> None:
    if os.path.isfile(dst):
        os.remove(dst)
    elif main.islink(dst):
        os.unlink(dst)
    elif os.path.isdir(dst):
        shutil.rmtree(dst)
    else:
        raise Exception('inexistent or invalid path type', dst)


def remove_file(dst: str) -> None:
    if os.path.isfile(dst):
        os.remove(dst)
    elif main.islink(dst):
        os.unlink(dst)
    else:
        raise Exception('inexistent or invalid path type', dst)


def remove_tree(dst: str) -> None:
    if main.islink(dst):
        os.unlink(dst)
    elif os.path.isdir(dst):
        shutil.rmtree(dst)
    else:
        raise Exception('inexistent or invalid path type', dst)


rename = move


def zip_dir(
    src: str,
    dst: str = None,
    overwrite: T.OverwriteScheme = None,
    progress: T.AnyProgress = None,
    compression_level: int = 7,
    keep_empty_folders: bool = True,
) -> str:
    """
    ref: https://likianta.blog.csdn.net/article/details/126710855
    """
    if dst is None:
        dst = src + '.zip'
    else:
        assert dst.endswith(('.zip', '.7z', '.tar.zst'))
    if exist(dst) and not _overwrite(dst, overwrite):
        return dst
    
    if progress is True:
        report = _show_progress_in_console
    elif progress:
        raise NotImplementedError
    else:
        report = None
    
    if dst.endswith('.zip'):
        top_name = basename(src)
        todo_dirs = tuple(findall_dirs(src))
        todo_files = tuple(findall_files(src))
        total = len(todo_dirs) + len(todo_files)
        
        with ZipFile(
            dst, 'w', compression=ZIP_DEFLATED, compresslevel=compression_level
        ) as handle:
            handle.write(src, arcname=top_name)
            i = 0
            for d in todo_dirs:
                i += 1
                if report: report(total, i, d.name)
                handle.write(
                    d.path, arcname='{}/{}'.format(top_name, d.relpath)
                )
            for f in todo_files:
                i += 1
                if report: report(total, i, f.name)
                handle.write(
                    f.path, arcname='{}/{}'.format(top_name, f.relpath)
                )
                
    elif dst.endswith('.7z'):
        import py7zr  # `pip install lk-utils[zip]` or `pip install py7zr`
        
        top_name = basename(src)
        todo_dirs = tuple(findall_dirs(src))
        todo_files = tuple(findall_files(src))
        total = len(todo_dirs) + len(todo_files)
        
        with py7zr.SevenZipFile(dst, 'w') as handle:
            handle.write(src, arcname=top_name)
            i = 0
            for d in todo_dirs:
                i += 1
                if report: report(total, i, d.name)
                handle.write(
                    d.path, arcname='{}/{}'.format(top_name, d.relpath)
                )
            for f in todo_files:
                i += 1
                if report: report(total, i, f.name)
                handle.write(
                    os.path.realpath(f.path),
                    arcname='{}/{}'.format(top_name, f.relpath)
                )
                
    elif dst.endswith('.tar.zst'):
        # https://chatgpt.com/share/69dde78d-8348-8321-b90d-0efc090f6b4f
        import tarfile
        # from compression import zstd  # TODO
        import zstandard as zstd  # pip install zstandard
        
        top_name = basename(src)
        todo_files = tuple(findall_files(src))
        if keep_empty_folders:
            all_dirs = frozenset((x.relpath for x in findall_dirs(src)))
            dirs_not_empty = frozenset((
                x.relpath.rsplit('/', 1)[0]
                for x in todo_files if '/' in x.relpath
            ))
            todo_dirs = sorted(all_dirs - dirs_not_empty)
        else:
            todo_dirs = ()
        total = len(todo_dirs) + len(todo_files)
        empty = xpath('.empty')
        
        with open(dst, 'wb') as file_out:
            with zstd.ZstdCompressor().stream_writer(file_out) as compressor:
                with tarfile.open(fileobj=compressor, mode='w|') as tar:
                    tar.add(src, arcname=basename(src))
                    i = 0
                    for f in todo_files:
                        i += 1
                        if report:
                            report(total, i, f.name)
                        if os.path.islink(f.path):
                            full_path = os.path.realpath(f.path)
                        else:
                            full_path = f.path
                        tar.add(
                            full_path,
                            arcname='{}/{}'.format(top_name, f.relpath)
                        )
                    if keep_empty_folders:
                        for d in todo_dirs:
                            i += 1
                            if report:
                                report(
                                    total, i, d.rsplit('/', 1)[-1] + '/.empty'
                                )
                            tar.add(
                                empty,
                                arcname='{}/{}'.format(top_name, d + '/.empty')
                            )
        
    else:
        raise Exception('no handler to compress this file type', dst)
    
    if report: print('', ':s2')
    
    return dst


def unzip_file(
    src: str,
    dst: str = None,
    overwrite: T.OverwriteScheme = None,
    progress: T.AnyProgress = None,
    # compression_level: int = 7,
    overwrite_top_name: bool = True,
    reserve_file_mtime: bool = True,
) -> str:
    assert src.endswith(('.zip', '.7z'))
    if dst is None:
        dst = src.rsplit('.', 1)[0]
    # print(src, dst, overwrite, exist(path_o), ':lvp')
    if exist(dst) and not _overwrite(dst, overwrite):
        return dst
    
    if progress is True:
        _report = _show_progress_in_console
    elif progress:
        def _report(total, index, name):
            progress(_ProgressItem(total, index, index / total, name))
    else:
        _report = None
    
    if dst.endswith('.7z'):
        import py7zr
        handle = py7zr.SevenZipFile(dst, 'r')
    else:
        handle = ZipFile(src, 'r', compression=ZIP_DEFLATED)
    
    def is_single_top(zfile: ZipFile) -> str:
        top_names = set()
        for name in zfile.namelist():
            # print(name, ':vi')
            if name.endswith('/'):
                if '/' not in name[:-1]:
                    top_names.add(name[:-1])
            else:
                if '/' not in name:
                    return ''
        if len(top_names) == 1:
            return top_names.pop()
        else:
            return ''
    
    top_name_i = is_single_top(handle)
    top_name_o = dirname(dst)
    # print(top_name_i, top_name_o, overwrite_top_name, ':v')
    trim_src_prefix = False
    if top_name_i:
        if top_name_i == top_name_o or overwrite_top_name:
            trim_src_prefix = True
    
    todo_dirs: t.Set[str] = set()
    todo_files: t.Set[t.Tuple[str, ZipInfo, int]] = set()
    for name in handle.namelist():
        relpath = name[len(top_name_i) + 1:] if trim_src_prefix else name
        if relpath:
            if relpath.endswith('/'):
                todo_dirs.add(relpath[:-1])
            else:
                info = handle.NameToInfo[name]  # noqa
                time = int(datetime(*info.date_time).timestamp())
                todo_files.add((relpath, info, time))
                if '/' in relpath:
                    todo_dirs.add(relpath.rsplit('/', 1)[0])
    total = len(todo_dirs) + len(todo_files)
    
    # -- make dirs
    os.mkdir(dst)
    i = 0
    for relpath in sorted(todo_dirs):
        if _report:
            i += 1
            _report(total, i, relpath)
        os.makedirs(dst + '/' + relpath, exist_ok=True)

    # -- dump files
    for relpath, info, time in sorted(todo_files):
        if _report:
            i += 1
            _report(total, i, relpath)  # noqa
        with (
            handle.open(info) as i,  # noqa
            open(dst + '/' + relpath, 'wb') as o
        ):
            shutil.copyfileobj(i, o)  # noqa
        if reserve_file_mtime:
            os.utime(dst + '/' + relpath, (time, time))
    
    handle.close()
    return dst


zip = zip_dir
unzip = unzip_file


def _overwrite(path: str, scheme: T.OverwriteScheme) -> bool:
    """
    params:
        scheme:
            True: overwrite
            False: no overwrite, and raise an FileexistError
            None: no overwrite, no error (skip)
    returns: bool
        True menas "can do overwrite".
    """
    if scheme is None:
        return False
    elif scheme is True:  # noqa
        remove(path)
        return True
    else:  # raise error
        raise FileExistsError(path)


def _safe_long_path(path: str) -> str:
    """
    avoid path limit error in windows.
    ref: docs/devnote/issues-summary-202401.zh.md
    """
    if IS_WINDOWS:
        return '\\\\?\\' + os.path.abspath(path)
    return path


def _show_progress_in_console(
    total: t.Union[float, int],
    current: t.Union[float, int],
    desc: str = ''
) -> None:
    prog = current / total
    print(':s1r', '\\[{}/{}] [red]{}[/][bright_black]{}[/] {}'.format(
        current,
        total,
        '-' * round(prog * 60),
        '-' * (60 - round(prog * 60)),
        desc and '{} ({:.2%})'.format(desc, prog) or '{:.2%}'.format(prog)
    ), end='\r')

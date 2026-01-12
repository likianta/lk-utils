import os
import shutil
import typing as t
import urllib.request
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile

from .finder import findall_dirs
from .finder import findall_files
from .main import IS_WINDOWS  # noqa
from .main import abspath
from .main import basename
from .main import dirname
from .main import exist
from .main import parent
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


class T:
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
    progress: t.Callable[[float], None] = None,
    overwrite: T.OverwriteScheme = None,
) -> None:
    """
    params:
        keep_file: whether to keep zip file after extracting.
    """
    if exist(path) and not _overwrite(path, overwrite):
        return
    
    if progress:
        def _report(count, block_size, total_size):
            assert total_size > 0, (url, path)
            progress(count * block_size / total_size)
    else:
        _report = None

    if extract:
        ext = (
            url.rsplit('.', 1)[-1] if url.endswith(
                ('.zip', '.gz', '.7z', '.zst')
            ) else 'zip'
        )
        assert ext == 'zip', (  # TODO
            'currently only support ".zip" extension.', url, path
        )
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


_symlink_granted = True


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
        global _symlink_granted
        if _symlink_granted:
            try:
                os.symlink(src, dst, target_is_directory=os.path.isdir(src))
            except OSError as e:
                # print(':v8p', e)
                if 'WinError 1314' in str(e):
                    # https://docs.python.org/3/library/os.html#os.symlink
                    # if os.getenv('FALLBACK_SYMLINK_IF_NO_PRIVILEGE') == '1':
                    print(':pv6', 'fallback symlink with no privileges')
                    _symlink_granted = False
                    _make_link_fallback(src, dst)
                    return dst
                raise e
        else:
            _make_link_fallback(src, dst)
            return dst
    else:
        os.symlink(src, dst)
    
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
    elif os.path.islink(dst):
        os.unlink(dst)
    elif os.path.isdir(dst):
        shutil.rmtree(dst)
    else:
        raise Exception('inexistent or invalid path type', dst)


def remove_file(dst: str) -> None:
    if os.path.isfile(dst):
        os.remove(dst)
    elif os.path.islink(dst):
        os.unlink(dst)
    else:
        raise Exception('inexistent or invalid path type', dst)


def remove_tree(dst: str) -> None:
    if os.path.islink(dst):
        os.unlink(dst)
    elif os.path.isdir(dst):
        shutil.rmtree(dst)
    else:
        raise Exception('inexistent or invalid path type', dst)


def zip_dir(
    src: str,
    dst: str = None,
    overwrite: T.OverwriteScheme = None,
    compression_level: int = 7,
) -> str:
    """
    ref: https://likianta.blog.csdn.net/article/details/126710855
    """
    if dst is None:
        dst = src + '.zip'
    else:
        assert dst.endswith('.zip')
    if exist(dst) and not _overwrite(dst, overwrite):
        return dst
    top_name = basename(src)
    with ZipFile(
        dst, 'w', compression=ZIP_DEFLATED, compresslevel=compression_level
    ) as z:
        z.write(src, arcname=top_name)
        for d in tuple(findall_dirs(src)):
            z.write(d.path, arcname='{}/{}'.format(top_name, d.relpath))
        for f in tuple(findall_files(src)):
            z.write(f.path, arcname='{}/{}'.format(top_name, f.relpath))
    return dst


def unzip_file(
    src: str,
    dst: str = None,
    overwrite: T.OverwriteScheme = None,
    compression_level: int = 7,
    overwrite_top_name: bool = True,
) -> str:
    assert src.endswith('.zip')
    if dst is None:
        dst = src[:-4]
    # print(src, dst, overwrite, exist(path_o), ':lvp')
    if exist(dst) and not _overwrite(dst, overwrite):
        return dst
    
    def is_single_top(zfile: ZipFile) -> str:
        top_names = set()
        for name in zfile.namelist():
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
    
    with ZipFile(
        src, 'r', compression=ZIP_DEFLATED, compresslevel=compression_level
    ) as z:
        if top_name := is_single_top(z):
            if top_name == dirname(dst):
                z.extractall(_safe_long_path(parent(dst)))
            elif overwrite_top_name:
                for name in z.namelist():
                    z.extract(name, name.replace(top_name, dst, 1))
            else:
                make_dir(dst)
                z.extractall(_safe_long_path(dst))
        else:
            z.extractall(_safe_long_path(dst))
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

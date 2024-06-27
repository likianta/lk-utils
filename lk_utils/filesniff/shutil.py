import os
import shutil
from os.path import exists
from textwrap import dedent

from .finder import findall_dirs
from .main import IS_WINDOWS  # noqa
from .main import xpath
from .. import common_typing as t
from ..subproc import run_cmd_args

__all__ = [
    'clone_tree',
    'copy_file',
    'copy_tree',
    'make_dir',
    'make_dirs',
    'make_file',
    'make_link',
    'make_links',
    'make_shortcut',
    'move',
    'remove',
    'remove_file',
    'remove_tree',
]


def clone_tree(src: str, dst: str, overwrite: bool = None) -> None:
    if exists(dst):
        if _overwrite(dst, overwrite) is False: return
    if not exists(dst):
        os.mkdir(dst)
    for d in findall_dirs(src):
        dp_o = f'{dst}/{d.relpath}'
        if not exists(dp_o):
            os.mkdir(dp_o)


def copy_file(src: str, dst: str, overwrite: bool = None) -> None:
    if exists(dst):
        if _overwrite(dst, overwrite) is False: return
    shutil.copyfile(src, dst)


def copy_tree(
    src: str, dst: str, overwrite: bool = None, symlinks: bool = False
) -> None:
    if exists(dst):
        if _overwrite(dst, overwrite) is False: return
    shutil.copytree(src, dst, symlinks=symlinks)


def make_dir(dst: str) -> None:
    if not exists(dst):
        os.mkdir(dst)


def make_dirs(dst: str) -> None:
    os.makedirs(dst, exist_ok=True)


def make_file(dst: str) -> None:
    open(dst, 'w').close()


def make_link(src: str, dst: str, overwrite: bool = None) -> str:
    """
    args:
        overwrite:
            True: if exists, overwrite
            False: if exists, raise an error
            None: if exists, skip it
    
    ref: https://blog.walterlv.com/post/ntfs-link-comparisons.html
    """
    from .main import normpath
    
    src = normpath(src, force_abspath=True)
    dst = normpath(dst, force_abspath=True)
    
    assert exists(src), src
    if exists(dst):
        if _overwrite(dst, overwrite) is False:
            return dst
    
    if IS_WINDOWS:
        os.symlink(src, dst, target_is_directory=os.path.isdir(src))
    else:
        os.symlink(src, dst)
    
    return dst


def make_links(
    src: str, dst: str, names: t.List[str] = None, overwrite: bool = None
) -> t.List[str]:
    out = []
    for n in names or os.listdir(src):
        out.append(make_link(f'{src}/{n}', f'{dst}/{n}', overwrite))
    return out


def make_shortcut(src: str, dst: str = None, overwrite: bool = None) -> None:
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
    if exists(dst):
        if _overwrite(dst, overwrite) is False: return
    if not IS_WINDOWS:
        raise NotImplementedError
    
    assert os.path.exists(src) and not src.endswith('.lnk')
    if not dst:
        dst = os.path.splitext(os.path.basename(src))[0] + '.lnk'
    else:
        assert dst.endswith('.lnk')
        if '<desktop>' in dst:
            dst = dst.replace('<desktop>', os.path.expanduser('~/Desktop'))
    
    vbs = xpath('./_temp_shortcut_generator.vbs')
    with open(vbs, 'w') as f:
        f.write(dedent('''
            Set objWS = WScript.CreateObject("WScript.Shell")
            lnkFile = "{file_o}"
            Set objLink = objWS.CreateShortcut(lnkFile)
            objLink.TargetPath = "{file_i}"
            objLink.Save
        ''').format(
            file_i=src.replace('/', '\\'),
            file_o=dst.replace('/', '\\'),
        ))
    run_cmd_args('cscript', '/nologo', vbs)
    os.remove(vbs)


def move(src: str, dst: str, overwrite: bool = None) -> None:
    if exists(dst):
        if _overwrite(dst, overwrite) is False: return
    shutil.move(src, dst)


def remove(dst: str) -> None:
    if exists(dst):
        if os.path.isfile(dst):
            os.remove(dst)
        elif os.path.islink(dst):
            os.unlink(dst)
        else:
            shutil.rmtree(dst)


def remove_file(dst: str) -> None:
    if exists(dst):
        os.remove(dst)


def remove_tree(dst: str) -> None:
    if exists(dst):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        elif os.path.islink(dst):
            os.unlink(dst)
        else:
            raise Exception('Unknown file type', dst)


def _overwrite(path: str, scheme: t.Union[None, bool]) -> bool:
    """
    args:
        scheme:
            True: overwrite
            False: no overwrite, and raise an FileExistsError
            None: no overwrite, no error (skip)
    returns: bool
        the return value reflects what "overwrite" results in, literally.
        i.e. True means "we DID overwrite", False means "we DID NOT overwrite".
        the caller should take care of the return value and do the leftovers. \
        usually, if caller receives True, it can continue its work; if False, \
        should return at once.
    """
    if scheme is None:
        return False
    elif scheme is True:
        remove(path)
        return True
    else:  # raise error
        raise FileExistsError(path)

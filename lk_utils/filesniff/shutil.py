import os
import shutil
from functools import partial
from os.path import exists

from .finder import findall_dirs
from .main import _IS_WINDOWS  # noqa
from .. import common_typing as t

__all__ = [
    'clone_tree',
    'copy_file',
    'copy_tree',
    'make_dir',
    'make_dirs',
    'make_file',
    'make_link',
    'make_links',
    'move',
    'overwrite',
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
    
    if _IS_WINDOWS:
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


def move(src: str, dst: str, overwrite: bool = None) -> None:
    if exists(dst):
        if _overwrite(dst, overwrite) is False: return
    shutil.move(src, dst)


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
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.islink(path):
            os.unlink(path)
        else:
            shutil.rmtree(path)
        return True
    else:  # raise error
        raise FileExistsError(path)


overwrite = partial(_overwrite, scheme=True)

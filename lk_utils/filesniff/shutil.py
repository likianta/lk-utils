import os
import shutil
import typing as t
from os.path import exists

from .finder import findall_dirs
from .main import _IS_WINDOWS  # noqa

__all__ = [
    'clone_tree',
    'copy_file',
    'copy_tree',
    'make_dir',
    'make_dirs',
    'make_link',
    'make_links',
    'move',
    'remove_file',
    'remove_tree',
]


def clone_tree(src: str, dst: str, overwrite: bool = None) -> None:
    if exists(dst):
        if _overwrite(dst, overwrite):
            return
    if not os.path.exists(dst):
        os.mkdir(dst)
    for d in findall_dirs(src):
        dp_o = f'{dst}/{d.relpath}'
        if not os.path.exists(dp_o):
            os.mkdir(dp_o)


def copy_file(src: str, dst: str, overwrite: bool = None) -> None:
    if exists(dst):
        if _overwrite(dst, overwrite):
            return
    shutil.copyfile(src, dst)


def copy_tree(src: str, dst: str, overwrite: bool = None,
              symlinks=False) -> None:
    if exists(dst):
        if _overwrite(dst, overwrite):
            return
    shutil.copytree(src, dst, symlinks=symlinks)


def make_dir(dst: str) -> None:
    if not exists(dst):
        os.mkdir(dst)


def make_dirs(dst: str) -> None:
    os.makedirs(dst, exist_ok=True)


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
    
    assert os.path.exists(src), src
    if exists(dst):
        if _overwrite(dst, overwrite):
            return dst
    
    if _IS_WINDOWS:
        os.symlink(src, dst, target_is_directory=os.path.isdir(src))
    else:
        os.symlink(src, dst)
    
    return dst


def make_links(src: str, dst: str,
               names: t.List[str] = None,
               overwrite: bool = None) -> t.List[str]:
    out = []
    for n in (names or os.listdir(src)):
        out.append(make_link(f'{src}/{n}', f'{dst}/{n}', overwrite))
    return out


def move(src: str, dst: str, overwrite: bool = None) -> None:
    if exists(dst):
        if _overwrite(dst, overwrite):
            return
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


def _overwrite(path: str, scheme: t.Optional[bool]) -> bool:
    """
    args:
        scheme:
            True: overwrite
            False: not overwrite, and raise an FileExistsError
            None: not overwrite, no error (skip)
    returns:
        True: tells caller all have been finished
        False: continue
    """
    if scheme is None:  # skip
        return True
    elif scheme is True:  # overwrite
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.islink(path):
            os.unlink(path)
        else:
            shutil.rmtree(path)
        return False
    else:  # raise error
        raise FileExistsError(path)

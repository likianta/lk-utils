from __future__ import annotations

import os
import shutil

from .finder import findall_dirs
from .main import _IS_WINDOWS


class T:
    Path = DirPath = str


def move(src: str, dst: str) -> None:
    shutil.move(src, dst)


def copy_tree(src: str, dst: str) -> None:
    shutil.copytree(src, dst)


def remove_tree(dst: str) -> None:
    shutil.rmtree(dst)


def clone_tree(src: str, dst: str) -> None:
    if not os.path.exists(dst):
        os.mkdir(dst)
    for d in findall_dirs(src):
        dp_o = f'{dst}/{d.relpath}'
        if not os.path.exists(dp_o):
            os.mkdir(dp_o)


def make_link(src: str, dst: str, overwrite: bool = None) -> str:
    """
    args:
        overwrite:
            True: if exists, overwrite
            False: if exists, raise an error
            None: if exists, skip it
    
    ref: https://blog.walterlv.com/post/ntfs-link-comparisons.html
    """
    assert os.path.exists(src), src
    
    # overwrite scheme
    if os.path.exists(dst):
        if overwrite is None:
            return dst
        elif overwrite is True:
            if os.path.islink(dst):
                os.unlink(dst)
            elif os.path.isfile(dst):
                os.remove(dst)
            else:
                shutil.rmtree(dst)
        else:  # False
            raise FileExistsError(dst)
    
    if _IS_WINDOWS:
        os.symlink(src, dst, target_is_directory=os.path.isdir(src))
    else:
        os.symlink(src, dst)
    
    return dst


def make_links(src, dst, names=None, overwrite: bool = None) -> list[str]:
    out = []
    for n in (names or os.listdir(src)):
        out.append(make_link(f'{src}/{n}', f'{dst}/{n}', overwrite))
    return out


# alias
copytree = copy_tree
rmtree = remove_tree
clonetree = clone_tree
mklink = make_link
mklinks = make_links

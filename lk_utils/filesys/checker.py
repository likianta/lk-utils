import os
import os.path as osp
import stat

from . import env


def empty(path: str) -> bool:
    if osp.isdir(path):
        return is_empty_dir(path)
    elif osp.isfile(path):
        return is_empty_file(path)
    elif osp.islink(path):
        return empty(osp.realpath(path))
    else:
        raise Exception(path)


def exist(path: str) -> bool:
    if osp.exists(path):
        return True
    elif osp.islink(path):
        # for broken symlink, although `osp.exists` gives False, we still -
        # return True.
        # https://stackoverflow.com/questions/75444181
        return True
    elif env.system_privileged is not True:
        if _is_junction(path):  # a broken junction link
            return True
    return False


def is_empty_dir(path: str) -> bool:
    for _ in os.listdir(path):
        return False
    return True


def is_empty_file(path: str) -> bool:
    """
    https://www.imooc.com/wenda/detail/350036?block_id=tuijian_yw
    """
    if osp.exists(path):
        if osp.getsize(path):
            return False
        return True
    return True


def is_parent(possible_parent: str, child: str) -> bool:
    return child.startswith(possible_parent + '/')


def isdir(path: str) -> bool:
    if path.strip('./') == '':
        return True
    if osp.isdir(path):
        return True
    if osp.isfile(path):
        return False
    if osp.islink(path):
        path = osp.realpath(path)
        return isdir(path)
    # raise Exception('unknown path type', path)
    return False


def isfile(path: str) -> bool:
    if path.strip('./') == '':
        return False
    if osp.isfile(path):
        return True
    if osp.isdir(path):
        return False
    if osp.islink(path):
        path = osp.realpath(path)
        return isfile(path)
    # raise Exception('unknown path type', path)
    return False


def islink(path: str) -> bool:
    if osp.islink(path):
        return True
    if env.system_privileged is not True:
        if _is_junction(path):  # a broken junction link
            return True
    return False


def issame(a: str, b: str) -> bool:
    if real_exist(a) and real_exist(b):
        return osp.samefile(a, b)
    print(':pv6', 'the comparison may not be valid!', a, b)
    return osp.realpath(a) == osp.realpath(b)


def real_exist(path: str) -> bool:
    return osp.exists(path)


def _is_junction(path: str) -> bool:
    # note: `os.path.isjunction` is added in python 3.12.
    if env.IS_PYTHON_312_OR_HIGHER:
        return osp.isjunction(path)
    else:
        try:
            st = os.lstat(path)
        except OSError:
            return False
        is_reparse = st.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
        is_mount_tag = (
            getattr(st, 'st_reparse_tag', 0) == stat.IO_REPARSE_TAG_MOUNT_POINT
        )
        return bool(is_reparse and is_mount_tag)

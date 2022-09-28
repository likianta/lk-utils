import os

from .main import normpath


class T:
    Path = str


def __get_launch_path() -> T.Path:
    """ Get launcher's filepath.

    Example:
        sys.argv: ['D:/myprj/src/main.py', ...] -> 'D:/myprj/src/main.py'
    """
    from sys import argv
    path = os.path.abspath(argv[0])
    if os.path.isfile(path):
        return normpath(path)
    else:
        raise Exception


def __get_launch_dir() -> T.Path:
    return os.path.dirname(__get_launch_path())


try:
    LAUNCH_ROOT = __get_launch_dir()  # launcher's dirpath
except:
    LAUNCH_ROOT = normpath(os.getcwd())

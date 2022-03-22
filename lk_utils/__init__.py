try:
    import lk_logger
    lk_logger.setup(silent=True)
except Exception:
    pass

from . import char_converter
from . import chinese_name_processor
from . import easy_launcher
from . import filesniff
from . import name_formatter
from . import read_and_write
from . import subproc
from . import time_utils
from . import tree_and_trie
from .filesniff import currdir
from .filesniff import find_dirs
from .filesniff import find_files
from .filesniff import findall_dirs
from .filesniff import findall_files
from .filesniff import relpath
from .read_and_write import dumps
from .read_and_write import loads
from .read_and_write import ropen
from .read_and_write import wopen
from .subproc import new_thread
from .subproc import run_cmd_args
from .subproc import run_cmd_shell
from .subproc import run_cmd_shell as send_cmd
from .subproc import run_new_thread
from .time_utils import timestamp

__version__ = '2.2.0'

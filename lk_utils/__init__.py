if 1:
    import lk_logger
    lk_logger.setup(quiet=True, show_funcname=False, show_varnames=True)

from . import binding
from . import common_typing as t
from . import common_typing as typing
from . import filesniff
from . import filesniff as fs
from . import read_and_write
from . import read_and_write as rw
from . import subproc
from . import textwrap
from . import time_utils  # TODO: rename to "time"?
from .binding import Signal
from .binding import bind_with
from .binding import call_once
from .filesniff import cd_current_dir
from .filesniff import find_dir_names
from .filesniff import find_dir_paths
from .filesniff import find_dirs
from .filesniff import find_file_names
from .filesniff import find_file_paths
from .filesniff import find_files
from .filesniff import findall_dir_names
from .filesniff import findall_dir_paths
from .filesniff import findall_dirs
from .filesniff import findall_file_names
from .filesniff import findall_file_paths
from .filesniff import findall_files
from .filesniff import get_current_dir
from .filesniff import make_link as mklink
from .filesniff import make_links as mklinks
from .filesniff import normpath
from .filesniff import xpath
from .filesniff import xpath as relpath  # backward compatible
# from .importer import get_module
# from .importer import get_package
# from .importer import load_module
# from .importer import load_package
from .read_and_write import dumps
from .read_and_write import loads
from .read_and_write import ropen
from .read_and_write import wopen
from .subproc import new_thread
from .subproc import run_cmd_args
from .subproc import run_cmd_line
from .subproc import run_new_thread
from .time_utils import timestamp
from .time_utils import wait

__version__ = '2.9.4'

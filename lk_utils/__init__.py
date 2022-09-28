try:
    import lk_logger
    lk_logger.setup(quiet=True)
except Exception:
    pass

from . import filesniff
from . import filesniff as fs
from . import read_and_write
from . import read_and_write as rw
from . import subproc
from . import time_utils
from .filesniff import currdir
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
from .filesniff import mklink
from .filesniff import mklinks
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

__version__ = '2.4.0'

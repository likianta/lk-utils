if 1:
    import lk_logger
    lk_logger.setup(quiet=True, show_funcname=False, show_varnames=False)

if 2:
    import sys
    if sys.version_info[:2] < (3, 11):
        # print('fix typing module compatibility', ':vs')
        from . import common_typing
        sys.modules['typing'] = common_typing

from . import binding
from . import filesniff as fs
from . import importer
from . import io
from . import io as rw  # alias
from . import pycompatible
from . import subproc
from . import textwrap
from . import time_utils  # TODO: rename to "time"?
from .binding import Reactive
from .binding import Signal
from .binding import bind_with
from .binding import call_once
from .filesniff import cd_current_dir
from .filesniff import find_dirs
from .filesniff import find_files
from .filesniff import findall_dirs
from .filesniff import findall_files
# from .filesniff import get_current_dir
from .filesniff import make_link as mklink
from .filesniff import make_links as mklinks
from .filesniff import normpath
from .filesniff import xpath
from .filesniff import xpath as p
from .filesniff import xpath as relpath  # backward compatible
from .io import dump
from .io import dumps  # backward compatible
from .io import load
from .io import loads  # backward compatible
from .subproc import coro_mgr as coro
from .subproc import new_thread
from .subproc import run_cmd_args
from .subproc import run_cmd_line
from .subproc import run_new_thread
from .time_utils import timer
from .time_utils import timestamp
from .time_utils import wait

__version__ = '3.0.0'

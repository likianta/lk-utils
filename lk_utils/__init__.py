# fmt: off
if 1:
    # import sys
    # if sys.version_info[:2] < (3, 11):
    #     from . import common_typing
    #     sys.modules['typing'] = common_typing
    import neoprint as np
    np.setup()
# fmt: on

from . import binding
from . import filesys as fs
from . import importer
from . import regex
from . import subproc
from . import textwrap
from . import time
from .binding import Reactive
from .binding import Signal
from .binding import bind_with
from .binding import call_once
from .chunk import chunkwise
from .filesys import cd_current_dir
from .filesys import find_dirs
from .filesys import find_files
from .filesys import findall_dirs
from .filesys import findall_files
from .filesys import here
from .filesys import normpath
from .filesys import xpath
from .filesys import xpath as p
from .filesys import xpath as relpath  # backward compatible
from .io import dump
from .io import load
from .ipython import start_ipython
from .subproc import Activity
from .subproc import bg
from .subproc import coro_mgr as coro
from .subproc import new_thread
from .subproc import run_cmd_args
from .subproc import run_cmd_line
from .subproc import run_new_thread
from .textwrap import wrap as dedent
from .time import now
from .time import pretty_time
from .time import timestamp
from .time import wait

__version__ = '3.6.0'

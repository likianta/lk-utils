# fmt: off
if 1:
    import neoprint as np
    np.setup()
if 2:
    # import sys
    # if sys.version_info[:2] < (3, 11):
    #     from . import common_typing
    #     sys.modules['typing'] = common_typing
    import typing as tp
    if not hasattr(tp, 'Self'):
        setattr(tp, 'Self', tp.Any)
# fmt: on

from . import binding
from . import filesys as fs
from . import importer
from . import subproc
from . import text_util
from . import time
from .binding import Reactive
from .binding import Signal
from .binding import bind_with
from .binding import call_once
from .chunk import chunkwise
from .filesys import cd_current_dir
from .filesys import dump
from .filesys import find_dirs
from .filesys import find_files
from .filesys import findall_dirs
from .filesys import findall_files
from .filesys import here
from .filesys import load
from .filesys import normpath
from .filesys import there
from .filesys import xpath
from .ipython import setup_breakpoint
from .ipython import start_ipython
from .ipython import start_ipython as enter_ipython
from .subproc import Activity
from .subproc import bg
from .subproc import coro_mgr as coro
from .subproc import new_thread
from .subproc import run_cmd_args
from .subproc import run_cmd_line
from .subproc import run_new_thread
from .text_util import dedent
from .text_util import manipulate as manipulate_text
from .text_util import regex
from .text_util import regex as re
from .text_util import slice as slice_text
from .text_util import textwrap
from .text_util import textwrap as tw
from .time import now
from .time import pretty_time
from .time import timestamp
from .time import wait
from .uuid import uuid

__version__ = '3.8.1'

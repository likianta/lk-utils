if 1:
    import lk_logger
    lk_logger.setup(quiet=True)

if 2:
    # check python version, if lower than 3.11, import typing_extensions
    import sys
    if sys.version_info < (3, 11):
        import typing
        from typing_extensions import Self
        setattr(typing, 'Self', Self)
    #   currently `typing.Self` in only used in `.subproc.threading \
    #   .ThreadBroker.then : [annotation] return`. we are considering whether \
    #   to remove this dependency becuase of its rare necessarity.

from . import filesniff
from . import filesniff as fs
from . import read_and_write
from . import read_and_write as rw
from . import subproc
from . import textwrap
from . import time_utils
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
from .read_and_write import dumps
from .read_and_write import loads
from .read_and_write import ropen
from .read_and_write import wopen
from .subproc import new_thread
from .subproc import run_cmd_args
from .subproc import run_cmd_line
from .subproc import run_new_thread

__version__ = '2.7.3'

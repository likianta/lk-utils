import os
import sys
from .filesys import abspath
from .filesys import basename
from .filesys import isdir
from .filesys import parent
from .filesys import real_exist
from .subproc import run_cmd_args

def run(target_path: str) -> None:
    print(sys.argv, ':lv')
    sys.path.append(abspath(os.getcwd()))
    if isdir(target_path):
        assert real_exist(f'{target_path}/__main__.py')
        cmd = (sys.executable, '-m', basename(target_path))
    else:
        cmd = (sys.executable, target_path)
    run_cmd_args(
        cmd,
        verbose=True,
        force_term_color=True,
        cwd=parent(target_path),
        ignore_return=True,
    )

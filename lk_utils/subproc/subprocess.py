import os
import re
import shlex
import subprocess as sp

import sys
from rich.text import Text

from lk_logger import bprint
from .threading import run_new_thread
from .. import common_typing as t
from ..textwrap import indent
from ..textwrap import join
from ..textwrap import reindent

__all__ = [
    # 'SubprocessError',
    'compose',
    'compose_cmd',
    'compose_command',
    'run',
    'run_cmd_args',
    'run_command_args',
    'run_cmd_line',
    'run_command_line',
]

# class SubprocessError(Exception):
#     pass

_ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
_SUBPROC_SCHEME = os.getenv('LK_SUBPROCESS_SCHEME', 'default')


def compose_command(*args: t.Any, filter: bool = True) -> t.List[str]:
    """
    examples:
        ('pip', 'install', '', 'lk-utils') -> ['pip', 'install', 'lk-utils']
        ('pip', 'install', 'lk-utils', ('-i', mirror)) ->
            if mirror is empty, returns ['pip', 'install', 'lk-utils']
            else returns ['pip', 'install', 'lk-utils', '-i', mirror]
    """
    
    def flatten(seq: t.Sequence) -> t.Iterator:
        for s in seq:
            if isinstance(s, (tuple, list)):
                yield from flatten(s)
            else:
                yield s
    
    def stringify(x: t.Optional[t.AnyStr]) -> str:
        return '' if x is None else str(x).strip()
    
    out = []
    for a in args:
        if isinstance(a, (tuple, list)):
            a = tuple(stringify(x) for x in flatten(a))
            if all(a) or not filter:
                out.extend(a)
        else:
            a = stringify(a)
            if a or not filter:
                out.append(a)
    return out


def run_command_args(
    *args: t.Any,
    verbose: bool = False,
    shell: bool = False,
    cwd: str = None,
    blocking: bool = True,
    ignore_error: bool = False,
    ignore_return: bool = False,
    filter: bool = True,
    subprocess_scheme: str = _SUBPROC_SCHEME,
    _refmt_args: bool = True,
) -> t.Union[str, sp.Popen, None]:
    """
    https://stackoverflow.com/questions/58302588/how-to-both-capture-shell -
    -command-output-and-show-it-in-terminal-at-realtime
    
    params:
        subprocess_scheme:
            'default':
                the most stable implementation. but lacks of:
                    - the progress bar which uses `print(..., end='\r') will
                        result into multiple lines.
                    - text lost color effect when using `rich` library.
            'progress_enhanced':
                an experimental scheme to resolve progress bar issue.
            'rich_colored_text':
                an experimental scheme to resolve text color lost issue. it may
                affect returned result.
            'rich_and_progress':
                apply both 'progress_enhanced' and 'rich_colored_text'.
            'pty':
                use pseudo-terminal to run the command. the cons are it changes
                your terminal title and may flicker the window.
        _refmt_args: set to False is faster. this is for internal use.
    
    returns:
        if ignore_return:
            return None
        else:
            if blocking:
                return <string>
            else:
                return <Popen object>
    
    memo:
        `sp.run` is blocking, `sp.Popen` is non-blocking.
    
    fix text color lost when using rich library:
        https://github.com/Textualize/rich/issues/2622
        https://rich.readthedocs.io/en/stable/console.html#terminal-detection
    """
    if _refmt_args:
        args = compose_command(*args, filter=filter)
    # else:
    #     assert all(isinstance(x, str) for x in args)
    if verbose:
        print('[magenta dim]{}[/]'.format(' '.join(args)), ':psr')
    
    def communicate0(ignore_return: bool = False) -> t.Tuple[str, str]:
        """
        returns:
            if `ignore_return` is True, returns ('', '');
            else returns (stdout, stderr).
        """
        stdout = ''
        for line in process.stdout:
            if verbose:
                bprint(line, end='')
            if not ignore_return:
                stdout += line
        stderr = ''
        for line in process.stderr:
            if verbose:
                bprint(line, end='')
            if not ignore_return:
                stderr += line
        return stdout, stderr
    
    def communicate1(
        remove_ansi_code: bool = True,
        #   https://stackoverflow.com/questions/14693701
        #   https://stackoverflow.com/questions/4324790
        #   https://stackoverflow.com/questions/17480656
        ignore_return: bool = False
    ) -> t.Tuple[str, str]:
        
        def readlines(source: t.IO) -> t.Iterator[str]:
            """
            yields: (line, ...)
            """
            b: bytes
            temp = b''
            while True:
                if b := source.read(1):
                    print(b, ':vi')
                    temp += b
                    if b == b'\n' or b == b'\r':
                        yield temp.decode()
                        temp = b''
                else:
                    break
            assert not temp
        
        stdout = ''
        for line in readlines(process.stdout):
            if verbose:
                bprint(line, end='')
            if not ignore_return:
                if remove_ansi_code:
                    stdout += _ANSI_ESCAPE.sub('', line)
                else:
                    stdout += line
        
        stderr = ''
        for line, end in readlines(process.stderr):
            if verbose:
                bprint(line, end='')
            if not ignore_return:
                if remove_ansi_code:
                    stderr += _ANSI_ESCAPE.sub('', line)
                else:
                    stderr += line
        
        return stdout, stderr
    
    def show_error(stdout: str, stderr: str) -> None:
        if verbose:  # we have printed the stdout, so do nothing.
            pass
        else:  # better to dump the stdout message to console.
            if stdout:
                print(':s1r', '[red dim]original output from subprocess:[/]')
                print(':s1r1', Text.from_ansi(indent(stdout), style='red dim'))
            print(':dv4s', 'subprocess error')
        print(
            reindent(
                '''
                error happened with exit code {}.
                the origin run command is:
                    {}
                each element is:
                    {}
                subprocess stderr: {}
                ''',
                lstrip=False,
            ).format(
                retcode,
                ' '.join(args),
                join(
                    (
                        '{:<2}  {}'.format(i, x)
                        for i, x in enumerate(args, 1)
                    ),
                    8,
                ),
                '\n' + indent(stderr) if stderr else '(no data)'
            ),
            ':v4'
        )
    
    if subprocess_scheme == 'default':
        with sp.Popen(
            args,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            cwd=cwd,
            shell=shell,
            text=True,
        ) as process:
            if blocking:
                stdout, stderr = communicate0(ignore_return)
                if retcode := process.wait():
                    if ignore_error:
                        return stderr
                    else:
                        show_error(stdout, stderr)
                        sys.exit(retcode)
                else:
                    assert not stderr
                    return stdout
            else:
                if verbose:
                    run_new_thread(communicate0, args=(True,))
                if ignore_return:
                    return None
                else:
                    return process
    elif subprocess_scheme in (
        'progress_enhanced',
        'rich_colored_text',
        'rich_and_progress',
    ):
        with sp.Popen(
            args,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            cwd=cwd,
            shell=shell,
            text=False,
        ) as process:
            if blocking:
                stdout, stderr = communicate1(ignore_return=ignore_return)
                if retcode := process.wait():
                    if ignore_error:
                        return stderr
                    else:
                        show_error(stdout, stderr)
                        sys.exit(retcode)
                else:
                    assert not stderr
                    return stdout
            else:
                if verbose:
                    run_new_thread(communicate1, args=(False, True,))
                if ignore_return:
                    return None
                else:
                    return process
    elif subprocess_scheme == 'pty':  # TODO
        # if sys.platform == 'win32':
        #     # pip install pywinpty
        #     # https://github.com/andfoy/pywinpty
        #     import winpty as pty
        # else:
        #     import pty
        # p = pty.PtyProcess.spawn(
        #     args, cwd=cwd, dimensions=(40, 100)
        # )
        # while p.isalive():
        #     line = p.readline()
        #     bprint(line)
        raise NotImplementedError
    else:
        raise Exception(subprocess_scheme)


def run_command_line(
    cmd: str,
    *,
    verbose: bool = False,
    shell: bool = False,
    cwd: str = None,
    blocking: bool = True,
    ignore_error: bool = False,
    ignore_return: bool = False,
    filter: bool = False,  # notice this differs
) -> t.Union[str, sp.Popen, None]:
    return run_command_args(
        *shlex.split(cmd),
        verbose=verbose,
        shell=shell,
        cwd=cwd,
        blocking=blocking,
        ignore_error=ignore_error,
        ignore_return=ignore_return,
        filter=filter,
        _refmt_args=False,
    )


# alias
compose = compose_cmd = compose_command
run = run_cmd_args = run_command_args
run_cmd_line = run_command_line

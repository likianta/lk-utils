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
    # subprocess_scheme: str = 'default',
    # subprocess_scheme: str = os.getenv('LK_SUBPROCESS_SCHEME', 'default'),
    _refmt_args: bool = True,
) -> t.Union[str, sp.Popen, None]:
    """
    https://stackoverflow.com/questions/58302588/how-to-both-capture-shell -
    -command-output-and-show-it-in-terminal-at-realtime
    
    params:
        ~~subprocess_scheme:~~
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
    
    def communicate(
        remove_ansi_code: bool = True,
        #   https://stackoverflow.com/questions/14693701
        #   https://stackoverflow.com/questions/4324790
        #   https://stackoverflow.com/questions/17480656
        ignore_return: bool = False
    ) -> t.Optional[str]:
        
        def readlines(source: t.IO) -> t.Iterator[str]:
            last: bytes = b''
            curr: bytes
            temp: bytes = b''
            while True:
                try:
                    if curr := source.read(1):
                        if curr == b'\n':
                            temp += curr
                            yield temp.decode()
                            temp = b''
                        elif last == b'\r':
                            yield temp.decode()
                            temp = curr
                        else:
                            temp += curr
                        last = curr
                    else:
                        break
                except Exception as e:
                    print(':e', e)
                    break
            if last == b'\r':
                # assert temp
                yield (temp + b'\n').decode()
            else:
                assert not temp, temp
        
        stdout = ''
        for line in readlines(process.stdout):
            if verbose:
                bprint(line, end='')
            if not ignore_return:
                if remove_ansi_code:
                    stdout += _ANSI_ESCAPE.sub('', line)
                else:
                    stdout += line
        # if ignore_return: assert stdout == ''
        return None if ignore_return else stdout.rstrip()  # strip '\r\n'
    
    def show_error(stdout: str) -> None:
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
            ),
            ':v4'
        )
    
    '''
    backup: the 'pty' scheme:
        if sys.platform == 'win32':
            # pip install pywinpty
            # https://github.com/andfoy/pywinpty
            import winpty as pty
        else:
            import pty
        p = pty.PtyProcess.spawn(
            args, cwd=cwd, dimensions=(40, 100)
        )
        while p.isalive():
            line = p.readline()
            bprint(line)
            ...
    '''
    
    # note: do not use `with sp.Popen(...) as process` statement, the child
    # process may exit before communicating, which raises 'ValueError: read of
    # closed file' or 'invalid arguments' error.
    process = sp.Popen(
        args,
        stdout=sp.PIPE,
        stderr=sp.STDOUT,
        cwd=cwd,
        shell=shell,
        # set `text` to False. since `text` will translate all types of newline
        # chars ('\n', '\r', '\r\n') to '\n', which is not convenient for
        # printing progress bar.
        text=False,
    )
    
    if blocking:
        result = communicate(ignore_return=ignore_return)
        if retcode := process.wait():
            if ignore_error:
                return result
            else:
                show_error(result)
                sys.exit(retcode)
        else:
            return result
    else:
        if verbose:
            run_new_thread(communicate, args=(False, True,))
        if ignore_return:
            return None
        else:
            return process


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

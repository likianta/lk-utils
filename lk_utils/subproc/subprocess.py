import shlex
import subprocess as sp

import sys
from lk_logger import bprint
from rich.text import Text

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
    _refmt_args: bool = True,
) -> t.Union[str, sp.Popen, None]:
    """
    https://stackoverflow.com/questions/58302588/how-to-both-capture-shell -
    -command-output-and-show-it-in-terminal-at-realtime
    
    params:
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
    """
    if _refmt_args:
        args = compose_command(*args, filter=filter)
    # else:
    #     assert all(isinstance(x, str) for x in args)
    if verbose:
        print('[magenta dim]{}[/]'.format(' '.join(args)), ':psr')
    
    if blocking:
        try:
            return sp.run(
                args,
                capture_output=verbose,
                check=not ignore_error,
                cwd=cwd,
                shell=shell,
                stderr=sp.PIPE,
                stdout=sp.PIPE,
                text=True,
            ).stdout
        except sp.CalledProcessError as e:
            if ignore_error:
                return e.stderr
            else:
                if e.stdout:
                    print(
                        ':s1r',
                        '[red dim]original output from subprocess:[/]'
                    )
                    print(
                        ':s1r1',
                        Text.from_ansi(indent(e.stdout), style='red dim')
                    )
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
                        e.returncode,
                        ' '.join(args),
                        join(
                            (
                                '{:<2}  {}'.format(i, x)
                                for i, x in enumerate(args, 1)
                            ),
                            8,
                        ),
                        '\n' + indent(e.stderr) if e.stderr else '(no data)'
                    ),
                    ':v4'
                )
                sys.exit(e.returncode)
                
                # raise SubprocessError(reindent(
                #     '''
                #     error happened with exit code {}.
                #     the origin run command is:
                #         {}
                #     each element is:
                #         {}
                #     subprocess response: {}
                #     '''.format(
                #         e.returncode,
                #         ' '.join(args),
                #         join(
                #             (
                #                 '{:<2}  {}'.format(i, x)
                #                 for i, x in enumerate(args, 1)
                #             ),
                #             24,
                #         ),
                #         '\n' + indent(e.stderr or e.stdout, '    ')
                #         if (e.stderr or e.stdout) else '(no data)'
                #     ),
                #     lstrip=False,
                # ))
    
    proc = sp.Popen(
        args, stdout=sp.PIPE, stderr=sp.PIPE, text=True, shell=shell, cwd=cwd
    )
    
    def communicate() -> t.Iterator[t.Tuple[str, int]]:
        for line in proc.stdout:
            if verbose:
                bprint(line)
            yield line, 0
        for line in proc.stderr:
            if verbose:
                bprint(line)
            yield line, 1
    
    if verbose:
        run_new_thread(lambda: [_ for _ in communicate()])
    return None if ignore_return else proc


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

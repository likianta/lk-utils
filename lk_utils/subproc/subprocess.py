import shlex
import subprocess as sp

from lk_logger import bprint

from .threading import run_new_thread
from .. import common_typing as t

__all__ = [
    'compose',
    'compose_cmd',
    'compose_command',
    'run',
    'run_cmd_args',
    'run_command_args',
    'run_cmd_line',
    'run_command_line',
]


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
    
    proc = sp.Popen(
        args, stdout=sp.PIPE, stderr=sp.PIPE, text=True, shell=shell, cwd=cwd
    )
    
    def communicate() -> t.Iterator[t.Tuple[str, int]]:
        for line in proc.stdout:
            if verbose:
                bprint(line.rstrip())
                # print(
                #     '[dim]{}[/]'.format(line.rstrip().replace('[', '\\[')),
                #     ':p2s1r',
                # )
            yield line, 0
        for line in proc.stderr:
            if verbose:
                bprint(line.rstrip())
                # print(
                #     '[red dim]{}[/]'.format(line.rstrip().replace('[', '\\[')),
                #     ':p2s1r',
                # )
            yield line, 1
    
    if blocking:
        out, err = '', ''
        for line, code in communicate():
            if ignore_return:
                continue
            if code == 0:
                out += line
            else:
                err += line
        
        if (code := proc.wait()) != 0:
            if not ignore_error:
                if verbose:  # the error trace info was already printed
                    exit(code)
                else:
                    raise E.SubprocessError(proc.args, err, code)
        
        return None if ignore_return else (out or err).lstrip('\n').rstrip()
    else:
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


class E:
    class SubprocessError(Exception):
        def __init__(
            self, args: t.Iterable[str], response: str, return_code: int = None
        ):
            self._args = ' '.join(args)
            self._resp = response
            self._code = str(return_code or 'null')
        
        def __str__(self):
            from textwrap import dedent
            from textwrap import indent
            
            return (
                dedent('''
                error happened with exit code {code}:
                    args:
                        {args}
                    response:
                        {response}
            ''')
                .format(
                    code=self._code,
                    args=self._args,
                    response=indent(self._resp, ' ' * 8).lstrip(),
                )
                .strip()
            )


# alias
compose = compose_cmd = compose_command
run = run_cmd_args = run_command_args
run_cmd_line = run_command_line

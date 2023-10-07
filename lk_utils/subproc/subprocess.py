import shlex
import subprocess as sp
import typing as t

__all__ = [
    'compose',
    'compose_cmd',
    'compose_command',
    'run',
    'run_cmd_args',
    'run_command_args',
    'run_cmd_shell',
    'run_command_shell',
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
    
    out = []
    for a in args:
        if isinstance(a, (tuple, list)):
            a = tuple(str(x).strip() for x in flatten(a))
            if all(a):
                out.extend(a)
        else:
            a = str(a).strip()
            if a or not filter:
                out.append(a)
    return out


def run_command_args(
    *args: t.Any,
    verbose: bool = False,
    shell: bool = False,
    blocking: bool = True,
    ignore_error: bool = False,
    ignore_return: bool = False,
    filter: bool = True,
    _refmt_args: bool = True,
) -> t.Union[None, str, sp.Popen]:
    """
    https://stackoverflow.com/questions/58302588/how-to-both-capture-shell -
    -command-output-and-show-it-in-terminal-at-realtime
    
    params:
        _refmt_args: set to False is faster. this is for internal use.
        
    returns:
        if non blocking: returns sp.Popen.
        if ignore_return: returns None.
        else: returns string.
    """
    if _refmt_args:
        args = compose_command(*args, filter=filter)
    # else:
    #     assert all(isinstance(x, str) for x in args)
    
    if ignore_return and blocking:
        # note: `sp.run` is blocking, `sp.Popen` is non-blocking.
        sp.run(args, check=not ignore_error, shell=shell)
        return None
    
    proc = sp.Popen(
        args, stdout=sp.PIPE, stderr=sp.PIPE, text=True, shell=shell
    )
    
    if not blocking:
        assert not verbose, 'cannot use `verbose=True` in non-blocking mode!'
    
    if blocking:
        out, err = '', ''
        for line in proc.stdout:
            if verbose:
                print(
                    '[dim]{}[/]'.format(
                        line.rstrip().replace('[', '\\['),
                    ),
                    ':psr',
                )
            out += line
        for line in proc.stderr:
            if verbose:
                print(
                    '[red dim]{}[/]'.format(
                        line.rstrip().replace('[', '\\['),
                    ),
                    ':psr',
                )
            err += line
        
        if (code := proc.wait()) != 0:
            if not ignore_error:
                if verbose:  # the output already printed
                    exit(code)
                else:
                    raise E.SubprocessError(proc.args, err, code)
        
        return (out or err).lstrip('\n').rstrip()
    else:
        return proc


def run_command_shell(
    cmd: str,
    verbose: bool = False,
    shell: bool = False,
    ignore_error: bool = False,
    ignore_return: bool = False,
    filter: bool = False,
) -> t.Union[None, str, sp.Popen]:
    return run_command_args(
        *shlex.split(cmd),
        verbose=verbose,
        shell=shell,
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
run_cmd_shell = run_command_shell

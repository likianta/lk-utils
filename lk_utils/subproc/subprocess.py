import shlex
import typing as t
from subprocess import PIPE
from subprocess import Popen
from subprocess import run as sub_run

__all__ = [
    'compose', 'compose_cmd', 'compose_command',
    'run', 'run_cmd_args', 'run_command_args',
    'run_cmd_shell', 'run_command_shell',
]


def compose_command(*args: t.Any, filter_=True) -> t.List[str]:
    """
    examples:
        ('pip', 'install', '', 'lk-utils') -> ['pip', 'install', 'lk-utils']
        ('pip', 'install', 'lk-utils', ('-i', mirror)) ->
            if mirror is empty, returns ['pip', 'install', 'lk-utils']
            else returns ['pip', 'install', 'lk-utils', '-i', mirror]
    """
    out = []
    for a in args:
        if isinstance(a, (tuple, list)):
            a = tuple(str(x).strip() for x in a)
            if all(a):
                out.extend(a)
        else:
            a = str(a).strip()
            if a or not filter_:
                out.append(a)
    return out


def run_command_args(
        *args: t.Any, verbose=False,
        ignore_error=False, filter_=True,
        _refmt_args=True
) -> str:
    """
    https://stackoverflow.com/questions/58302588/how-to-both-capture-shell
    -command-output-and-show-it-in-terminal-at-realtime
    
    args:
        _refmt_args: set to False is faster. this is for internal use only.
    """
    if _refmt_args:
        args = compose_command(*args, filter_=filter_)
    # else:
    #     assert all(isinstance(x, str) for x in args)
    
    if not verbose:
        sub_run(args, check=not ignore_error)
        return ''
    
    proc = Popen(args, stdout=PIPE, stderr=PIPE, text=True)
    
    out, err = '', ''
    for line in proc.stdout:
        print(':psr', '[dim]{}[/]'.format(
            line.rstrip().replace('[', '\\[')))
        out += line
    for line in proc.stderr:
        print(':psr', '[red dim]{}[/]'.format(
            line.rstrip().replace('[', '\\[')))
        err += line
    
    if (code := proc.wait()) != 0:
        if not ignore_error:
            if verbose:  # the output already printed
                exit(code)
            else:
                raise E.SubprocessError(proc.args, err, code)
    
    return out or err


def run_command_shell(
        cmd: str, verbose=False,
        ignore_error=False, filter_=False
) -> str:
    return run_command_args(
        *shlex.split(cmd), verbose=verbose,
        ignore_error=ignore_error, filter_=filter_,
        _refmt_args=False
    )


class E:
    class SubprocessError(Exception):
        def __init__(
                self,
                args: t.Iterable[str],
                response: str,
                return_code: int = None
        ):
            self._args = ' '.join(args)
            self._resp = response
            self._code = str(return_code or 'null')
        
        def __str__(self):
            from textwrap import dedent, indent
            return dedent('''
                error happened with exit code {code}:
                    args:
                        {args}
                    response:
                        {response}
            ''').format(
                code=self._code,
                args=self._args,
                response=indent(self._resp, ' ' * 8).lstrip()
            ).strip()


# alias
compose = compose_cmd = compose_command
run = run_cmd_args = run_command_args
run_cmd_shell = run_command_shell

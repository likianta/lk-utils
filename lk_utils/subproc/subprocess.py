import typing as t
from subprocess import PIPE
from subprocess import Popen

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
        ignore_error=False, filter_=False
) -> str:
    if filter_:
        args = tuple(filter(None, map(str, args)))
    else:
        args = tuple(map(str, args))
    proc = Popen(args, stdout=PIPE, stderr=PIPE, text=True)
    
    if verbose:
        # https://stackoverflow.com/questions/58302588/how-to-both-capture-shell
        # -command-output-and-show-it-in-terminal-at-realtime
        out, err = '', ''
        for line in proc.stdout:
            print(':psr', '[dim]{}[/]'.format(
                line.rstrip().replace('[', '\\[')))
            out += line
        for line in proc.stderr:
            print(':psr', '[red dim]{}[/]'.format(
                line.rstrip().replace('[', '\\[')))
            err += line
    else:
        out, err = proc.communicate()
    
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
    import shlex
    return run_command_args(
        *shlex.split(cmd), verbose=verbose,
        ignore_error=ignore_error, filter_=filter_
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
            self._response = response
            self._return_code = str(return_code or 'null')
        
        def __str__(self):
            from textwrap import dedent, indent
            return dedent('''
                error happened with exit code {code}:
                    args:
                        {args}
                    response:
                        {response}
            ''').format(
                code=self._return_code,
                args=self._args,
                response=indent(self._response, ' ' * 8).lstrip()
            ).strip()


# alias
compose = compose_cmd = compose_command
run = run_cmd_args = run_command_args
run_cmd_shell = run_command_shell

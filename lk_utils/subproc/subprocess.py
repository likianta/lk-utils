import atexit
import os
import re
import shlex
import subprocess as sp
import typing as t

import psutil
from rich.text import Text
from time import sleep

from lk_logger import bprint
from .threading import Thread
from .threading import new_thread
from .threading import run_new_thread
from .. import textwrap

_ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class Popen(sp.Popen):
    communication_thread: t.Optional[Thread]
    _introspection: bool
    
    def __init__(self, *args, keep_alive: bool = False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.communication_thread = None
        self._introspection = False
        atexit.register(self.kill)
        if keep_alive:
            self._watch_self_status()
    
    @property
    def is_running(self) -> bool:
        # return self.poll() is None
        return psutil.pid_exists(self.pid) and self.poll() is None
    
    def kill(self) -> None:
        """
        kill self and child processes.
        """
        if not self.is_running: return
        pid = self.pid
        parent = psutil.Process(pid)
        print(':r', '[red dim]kill process: {} ({})[/]'.format(
            pid, parent.name()
        ))
        self._introspection = False
        for child in parent.children(recursive=True):
            print(':r', '[red dim]|- kill child process: {} ({})[/]'.format(
                child.pid, child.name()
            ))
            # noinspection PyUnresolvedReferences
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
        # noinspection PyUnresolvedReferences
        try:
            parent.kill()
        except psutil.NoSuchProcess:
            pass
        if self.communication_thread:
            print('[red dim]cut off subprocess printing.[/]', ':r')
            self.communication_thread.kill()
    
    @new_thread()
    def _watch_self_status(self) -> None:
        self._introspection = True
        while self._introspection:
            if self.is_running:
                sleep(1)
            else:
                print(':v8', 'process has exited unexpectly.')
                self._introspection = False
                return


def compose_cmd(*args: t.Any, filter: bool = True) -> t.List[str]:
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


def run_cmd_args(
    *args: t.Any,
    verbose: bool = False,
    shell: bool = False,
    cwd: str = None,
    env: t.Dict[str, str] = None,
    blocking: bool = True,
    ignore_error: bool = False,
    ignore_return: bool = False,
    force_term_color: bool = False,
    filter: bool = True,
    # subprocess_scheme: str = 'default',
    # subprocess_scheme: str = os.getenv('LK_SUBPROCESS_SCHEME', 'default'),
    _refmt_args: bool = True,
) -> t.Union[str, Popen, None]:
    """
    https://stackoverflow.com/questions/58302588/how-to-both-capture-shell -
    -command-output-and-show-it-in-terminal-at-realtime
    
    params:
        force_term_color:
            by default (force_term_color=False), the prints from subprocess
            don't render ansi color code.
            if you need to keep the color effect, set it true.
            warning:
                - this is an experimental feature.
                - requires dependency lk-logger >= 5.6.2.
                - it may result grumble code in some old terminals on windows.
            related:
                fix text color lost when using rich library:
                    https://github.com/Textualize/rich/issues/2622
                    https://rich.readthedocs.io/en/stable/console.html#terminal
                    -detection
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
        args = compose_cmd(*args, filter=filter)
    # else:
    #     assert all(isinstance(x, str) for x in args)
    if verbose:
        print('[magenta dim]{}[/]'.format(' '.join(args)), ':psr')
    
    def communicate(
        remove_ansi_code: t.Optional[bool] = None,
        #   https://stackoverflow.com/questions/14693701
        #   https://stackoverflow.com/questions/4324790
        #   https://stackoverflow.com/questions/17480656
    ) -> t.Iterator[str]:
        """
        yield: line, without '\n' at the end.
        """
        
        def readlines(source: t.IO) -> t.Iterator[str]:
            last: bytes = b''
            curr: bytes
            temp: bytes = b''
            while True:
                try:
                    if curr := source.read(1):
                        if curr == b'\n':
                            temp += curr
                            yield temp.decode(errors='ignore')
                            temp = b''
                        elif last == b'\r':
                            yield temp.decode(errors='ignore')
                            temp = curr
                        else:
                            temp += curr
                        last = curr
                    else:
                        break
                except Exception as e:
                    print(':e', e)
                    break
            if temp:
                yield (temp + b'\n').decode(errors='ignore')
        
        for line in readlines(process.stdout):
            if verbose:
                bprint(line, end='', flush=True)
            if remove_ansi_code:
                yield _ANSI_ESCAPE.sub('', line)
            else:
                yield line.rstrip()
    
    def format_error(stdout: str) -> str:
        if verbose:  # we have printed the stdout, so do nothing.
            pass
        else:  # better to dump the stdout message to console.
            if stdout:
                print(':s1r', '[red dim]original output from subprocess:[/]')
                print(':s1r1', Text.from_ansi(
                    textwrap.wrap(stdout, 4), style='red dim'
                ))
            # print(':dv8', 'subprocess error')
        return textwrap.wrap(
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
            textwrap.join(
                (
                    '{:<2}  {}'.format(i, x)
                    for i, x in enumerate(args, 1)
                ),
                8,
            ),
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
    
    if env is None:
        if force_term_color:
            env = os.environ.copy()
            env['LK_LOGGER_FORCE_COLOR'] = '1'
        else:
            env = os.environ
    else:
        if force_term_color:
            env['LK_LOGGER_FORCE_COLOR'] = '1'
    # note: do not use `with sp.Popen(...) as process` statement, the child
    # process may exit before communicating, which raises 'ValueError: read of
    # closed file' or 'invalid arguments' error.
    process = Popen(
        args,
        stdout=sp.PIPE,
        stderr=sp.STDOUT,
        cwd=cwd,
        shell=shell,
        # set `text` to False. since `text` will translate all types of newline
        # chars ('\n', '\r', '\r\n') to '\n', which is not convenient for
        # printing progress bar.
        text=False,
        env=env,
    )
    
    if blocking:
        comm = communicate(remove_ansi_code=force_term_color)
        if ignore_return:
            for _ in comm:
                pass
            stdout = None
        else:
            stdout = '\n'.join(comm)
        if retcode := process.wait():
            if ignore_error:
                return stdout
            else:
                # show_error(stdout)
                # sys.exit(retcode)
                raise Exception(format_error(stdout))
        else:
            return stdout
    else:
        if verbose:
            process.communication_thread = run_new_thread(
                communicate, args=(False,), interruptible=True
            )
        return process


def run_cmd_line(cmd: str, **kwargs) -> t.Union[str, Popen, None]:
    return run_cmd_args(
        *shlex.split(cmd), **kwargs, filter=False, _refmt_args=False
    )

import builtins
import os
import sys
import typing as tp
from inspect import currentframe
from traceback import walk_tb
from types import FrameType
from types import TracebackType

import neoprint as np

from .filesys import normpath
from .filesys import relpath


def start_ipython(
    context: tp.Optional[tp.Dict[str, tp.Any]] = None,
    message: str = '',
    *,
    verbose: tp.Optional[bool] = None,
    verbosity: int = 1,
) -> None:
    """
    params:
        message: text in markdown format.
        verbose: `verbose=True` is equal to `verbosity=1`.
    """

    if getattr(builtins, '__IPYTHON__', False):
        # we are already in ipython environment.
        np.show(':pv5', 'you are already in ipython environment')
        return

    try:
        import IPython  # noqa
    except (ImportError, ModuleNotFoundError):
        np.show('ipython is not installed!', ':pv8')
        raise
    else:
        from IPython.core.getipython import get_ipython
        from IPython.terminal.ipapp import TerminalIPythonApp
        from rich import get_console
        from rich.traceback import install

    verbosity = 1 if verbose is True else 0 if verbose is False else verbosity
    if verbosity and (message or context):
        if message:
            np.markdown(message)
        elif context:
            np.show(
                ':lv2p',
                'registered global variables:',
                sorted(context.keys()) if verbosity == 1 else context,
            )

    sys_argv_backup = sys.argv.copy()
    sys.argv = ['']  # avoid ipython to parse `sys.argv`.

    app = TerminalIPythonApp.instance(
        user_ns={'__userns__': context, **(context or {})}
    )
    if verbosity and message:
        app.display_banner = False
    app.initialize()

    # setup except hook for ipython
    setattr(builtins, 'get_ipython', get_ipython)
    install(console=get_console())

    app.start()  # type: ignore

    # afterwards
    sys.argv = sys_argv_backup


# ------------------------------------------------------------------------------


def setup_breakpoint() -> None:
    sys.excepthook = _break_into_ipython


def _break_into_ipython(type, value, traceback) -> None:
    # ref: `neoprint.config._Config._custom_excepthook`
    if type is KeyboardInterrupt:
        sys.exit()
    else:
        np.show(':dv6', 'breaking into ipython environment')

        ctx_changer = _ContextChanger(traceback)
        frame = traceback.tb_frame
        assert frame

        def _whatsup() -> None:
            raise value

        start_ipython(
            frame.f_globals
            | frame.f_locals
            | {
                '__error__': value,
                'check_out_frame': ctx_changer.check_out_frame,
                'preview_tb': ctx_changer.preview,
                'whatsup': _whatsup,
            },
            """
            {banner}

            You are getting into this place because an error occurred in your 
            program.
            
            - To check all context variables, type `__userns__`.
            - To check the error message, type `__error__`.
            - To check the error details, type `raise __error__` or `whatsup()`.
            - To exit the IPython session, type `exit` or `quit`.
            
            {banner}
            """.format(banner='█ ░ ' * (min((np.console.width, 80)) // 4)),
        )


class _ContextChanger:
    def __init__(self, traceback: TracebackType) -> None:
        # self._tb = traceback
        self._frames = []  # [(file, lineno, function_name, frame), ...]
        for frame, lineno in walk_tb(traceback):
            self._frames.append(
                (
                    normpath(frame.f_code.co_filename),
                    lineno,
                    frame.f_code.co_name,
                    frame,
                )
            )

    def preview(self, _format: bool = False) -> tp.Optional[str]:
        table_rows = [('index', 'source', 'function')]
        for i, (s, l, n, _) in enumerate(self._frames):  # noqa
            table_rows.append((str(i), relpath(s) + ':' + str(l), n))
        if _format:
            return np.format(table_rows, ':r2')
        else:
            np.show(table_rows, ':r2')

    def check_out_frame(
        self, search: tp.Union[str, int] = '', interactive: bool = True
    ) -> None:
        caller_frame: FrameType
        target_frame: FrameType

        if isinstance(search, int):
            target_frame = self._frames[search][3]
        elif search != '':
            partial_path: str
            lineno: int = 0
            func_name: str = ''
            if search.count(':') == 0:
                partial_path = search
            elif search.count(':') == 1:
                a, b = search.split(':')
                partial_path = a
                lineno = int(b)
            else:  # 2
                a, b, c = search.split(':')
                partial_path = a
                lineno = int(b)
                func_name = c
            assert any(
                (partial_path, lineno, func_name)
            ) and partial_path.endswith('.py')

            for s, l, n, f in self._frames:  # noqa
                if (
                    s.endswith(partial_path)
                    and (not lineno or lineno == l)
                    and (not func_name or func_name == n)
                ):
                    target_frame = f
                    break
            else:
                raise Exception(
                    'cannot find target frame',
                    self.preview(_format=True),
                    search,
                )
        elif interactive:
            self.preview()
            while True:
                index = input('select frame index: ')
                if index == 'x':  # exit method
                    return
                if index.isdigit():
                    target_frame = self._frames[int(index)][3]
                    break
        else:
            raise Exception

        assert target_frame
        caller_frame = currentframe().f_back  # type: ignore
        caller_frame.f_globals.update(target_frame.f_globals)
        caller_frame.f_locals.update(target_frame.f_locals)


if os.getenv('LKUTILS_BREAKPOINT') == '1':
    setup_breakpoint()

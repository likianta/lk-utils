import builtins
import os
import sys
import typing as t
from inspect import currentframe
from traceback import walk_tb
from types import FrameType

import neoprint as np


def start_ipython(
    context: t.Optional[t.Dict[str, t.Any]] = None,
    message: str = '',
    *,
    verbose: t.Optional[bool] = None,
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
                tuple(context.keys()) if verbosity == 1 else context,
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


def _break_into_ipython(type, value, traceback) -> None:
    # ref: `neoprint.config._Config._custom_excepthook`
    if type is KeyboardInterrupt:
        sys.exit()
    else:
        np.show(':dv6', 'breaking into ipython environment')
        frame = traceback.tb_frame
        assert frame

        def _whatsup() -> None:
            raise value

        def _check_out_context(
            partial_script_path: str, function_name: str = ''
        ) -> None:
            assert partial_script_path.endswith('.py')
            caller_frame: FrameType = currentframe().f_back  # type: ignore
            stack_view = []
            for frame, lineno in walk_tb(traceback):
                stack_view.append(
                    (frame.f_code.co_filename, lineno, frame.f_code.co_name)
                )
                if frame.f_code.co_filename.replace('\\', '/').endswith(
                    partial_script_path
                ):
                    if (
                        not function_name
                        or frame.f_code.co_name == function_name
                    ):
                        np.show(
                            ':p',
                            'find frame in ~/{}:{}'.format(
                                partial_script_path, lineno
                            ),
                        )
                        caller_frame.f_globals.update(frame.f_globals)
                        caller_frame.f_locals.update(frame.f_locals)
                        return
            raise Exception(
                'cannot find target frame', np.format(stack_view, ':l')
            )

        start_ipython(
            frame.f_globals
            | frame.f_locals
            | {
                '__error__': value,
                'whatsup': _whatsup,
                'check_out_context': _check_out_context,
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


if os.getenv('LKUTILS_BREAKPOINT') == '1':
    sys.excepthook = _break_into_ipython


def setup_breakpoint() -> None:
    sys.excepthook = _break_into_ipython

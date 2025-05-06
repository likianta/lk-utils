import builtins
import typing as t


def start_ipython(
    user_ns: t.Dict[str, t.Any] = None,
    verbosity: t.Union[bool, int] = 1
) -> None:
    if getattr(builtins, '__IPYTHON__', False):
        # we are already in ipython environment.
        print(':pv5', 'you are already in ipython environment')
        return
    
    try:
        import IPython  # noqa
    except (ImportError, ModuleNotFoundError) as e:
        print('ipython is not installed!', ':pv8')
        raise e
    else:
        import sys
        from IPython.core.getipython import get_ipython  # noqa
        from IPython.terminal.ipapp import TerminalIPythonApp  # noqa
        from lk_logger import bprint
        from lk_logger import deflector
        from lk_logger.console import console
        from rich.traceback import install
    
    if user_ns and verbosity:
        print(
            ':lv2ps',
            'registered global variables:',
            tuple(user_ns.keys()) if verbosity == 1 else user_ns
        )
    
    sys_argv_backup = sys.argv.copy()
    sys.argv = ['']  # avoid ipython to parse `sys.argv`.
    deflector.add(IPython, bprint, scope=True)
    
    app = TerminalIPythonApp.instance(
        user_ns={
            '__USERNS__': user_ns,
            **(user_ns or {})
        }
    )
    app.initialize()
    
    # setup except hook for ipython
    setattr(builtins, 'get_ipython', get_ipython)
    install(console=console)
    
    app.start()
    
    # afterwards
    sys.argv = sys_argv_backup

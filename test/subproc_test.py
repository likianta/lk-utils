import sys
import typing as t
from inspect import currentframe
from textwrap import indent

from argsense import cli

import lk_logger
from lk_utils import subproc
from lk_utils import subproc as sp

pyexe = sys.executable


@cli.cmd()
def composing_command():
    print(subproc.compose_cmd('a'))  # -> ['a']
    print(subproc.compose_cmd('a', 'b'))  # -> ['a', 'b']
    print(subproc.compose_cmd('a', '', 'b'))  # -> ['a', 'b']
    print(subproc.compose_cmd('a', (), 'b'))  # -> ['a', 'b']
    print(subproc.compose_cmd('a', 'b', ('c',)))  # -> ['a', 'b', 'c']
    print(subproc.compose_cmd('a', 'b', ('c', 'd')))  # -> ['a', 'b', 'c', 'd']
    print(subproc.compose_cmd('a', 'b', ('c', '')))  # -> ['a', 'b']


@cli.cmd()
def run_cmd() -> None:
    print(':d', 'normal case')
    rsp = subproc.run_cmd_args(pyexe, 'test/subproc_test.py', 'normal-case')
    print(rsp)
    
    print(':d', 'error case')
    rsp = subproc.run_cmd_args(pyexe, 'test/subproc_test.py', 'error-case')
    print(rsp)
    
    # print(':d', 'enable verbose')
    
    # print(subproc.run_cmd_line(f'{pyexe} -V'))
    # print(subproc.run_cmd_args(pyexe, '-V'))
    # print(subproc.run_cmd_args(pyexe, '-m', 'pip', '-V'))
    # print(':d', 'enable verbose')
    # subproc.run_cmd_line(f'{pyexe} -V', verbose=True)
    # subproc.run_cmd_args(pyexe, '-V', verbose=True)
    # subproc.run_cmd_args(pyexe, '-m', 'pip', '-V', verbose=True)


@cli.cmd()
def raise_cmd_error():
    try:
        print(subproc.run_cmd_args('depsland', '-V'))
    except Exception as e:
        print(type(e), e)


@cli.cmd()
def new_thread_singleton():
    from time import sleep
    from random import choice
    
    @subproc.new_thread(singleton=True)
    def foo(head: str):
        for i in range(10):
            print(head, i)
            sleep(choice((0.1, 0.2, 0.3)))
    
    foo('alpha')
    foo(' beta')
    foo('gamma')
    
    sleep(5)
    print('done')


# -----------------------------------------------------------------------------

@cli.cmd()
def normal_case(_user: bool = True) -> None:
    if _user:
        _rerun_in_subproc()
    else:
        print('hello world')

    
@cli.cmd()
def error_case(_user: bool = True) -> None:
    if _user:
        _rerun_in_subproc()
    else:
        print('going to raise an error...', ':v4s')
        raise Exception('this is an error')


def _rerun_in_subproc() -> None:
    lk_logger.update(
        show_source=False,
        show_funcname=False,
        show_varnames=False
    )
    
    last_frame = currentframe().f_back
    last_func = last_frame.f_code.co_name.replace('_', '-')
    print('run command', last_func, ':vsi')
    rsp = sp.run_cmd_args(
        pyexe, 'test/subproc_test.py', last_func, '--not-user'
    )

    if rsp:
        print('the response is:', ':vsi')
        print(indent(rsp, '    '))
    else:
        print('nothing returned', ':vsi')
        

if __name__ == '__main__':
    # pox test/subproc_test.py normal-case
    # pox test/subproc_test.py error-case
    cli.run()

from lk_logger import lk

from lk_utils import subproc


def show_python_version():
    lk.loga(subproc.run_cmd_shell('python -V'))
    lk.loga(subproc.run_cmd_args('python', '-V'))
    
    
def show_pip_version():
    lk.loga(subproc.run_cmd_args('python', '-m', 'pip', '-V'))


def raise_an_error():
    lk.loga(subproc.run_cmd_args('depsland', '-V'))


if __name__ == '__main__':
    show_python_version()
    show_pip_version()
    raise_an_error()

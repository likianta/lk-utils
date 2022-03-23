from lk_utils import subproc


def test_popen_cmd():
    print(subproc.run_cmd_shell('python -V'))
    print(subproc.run_cmd_args('python', '-V'))
    print(subproc.run_cmd_args('python', '-m', 'pip', '-V'))


def test_raise_cmd_error():
    try:
        print(subproc.run_cmd_args('depsland', '-V'))
    except Exception as e:
        print(type(e), e)

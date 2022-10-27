from lk_utils import subproc


def test_composing_command():
    print(subproc.compose_cmd('a'))  # -> ['a']
    print(subproc.compose_cmd('a', 'b'))  # -> ['a', 'b']
    print(subproc.compose_cmd('a', '', 'b'))  # -> ['a', 'b']
    print(subproc.compose_cmd('a', (), 'b'))  # -> ['a', 'b']
    print(subproc.compose_cmd('a', 'b', ('c',)))  # -> ['a', 'b', 'c']
    print(subproc.compose_cmd('a', 'b', ('c', 'd')))  # -> ['a', 'b', 'c', 'd']
    print(subproc.compose_cmd('a', 'b', ('c', '')))  # -> ['a', 'b']


def test_popen_cmd():
    print(subproc.run_cmd_shell('python -V'))
    print(subproc.run_cmd_args('python', '-V'))
    print(subproc.run_cmd_args('python', '-m', 'pip', '-V'))


def test_raise_cmd_error():
    try:
        print(subproc.run_cmd_args('depsland', '-V'))
    except Exception as e:
        print(type(e), e)


if __name__ == '__main__':
    test_composing_command()

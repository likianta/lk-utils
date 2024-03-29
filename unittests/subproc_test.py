from argsense import cli
from lk_utils import subproc


@cli.cmd()
def test_composing_command():
    print(subproc.compose_cmd('a'))  # -> ['a']
    print(subproc.compose_cmd('a', 'b'))  # -> ['a', 'b']
    print(subproc.compose_cmd('a', '', 'b'))  # -> ['a', 'b']
    print(subproc.compose_cmd('a', (), 'b'))  # -> ['a', 'b']
    print(subproc.compose_cmd('a', 'b', ('c',)))  # -> ['a', 'b', 'c']
    print(subproc.compose_cmd('a', 'b', ('c', 'd')))  # -> ['a', 'b', 'c', 'd']
    print(subproc.compose_cmd('a', 'b', ('c', '')))  # -> ['a', 'b']


@cli.cmd()
def test_popen_cmd():
    print(subproc.run_cmd_shell('python3 -V'))
    print(subproc.run_cmd_args('python3', '-V'))
    print(subproc.run_cmd_args('python3', '-m', 'pip', '-V'))
    print(':d', 'add verbose')
    subproc.run_cmd_shell('python3 -V', verbose=True)
    subproc.run_cmd_args('python3', '-V', verbose=True)
    subproc.run_cmd_args('python3', '-m', 'pip', '-V', verbose=True)


@cli.cmd()
def test_raise_cmd_error():
    try:
        print(subproc.run_cmd_args('depsland', '-V'))
    except Exception as e:
        print(type(e), e)


@cli.cmd()
def test_new_thread_singleton():
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


if __name__ == '__main__':
    cli.run()

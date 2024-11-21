import sys
from argsense import cli
from lk_utils import run_cmd_args
from time import sleep


@cli.cmd()
def main() -> None:
    run_cmd_args(
        sys.executable, __file__, 'foo',
        verbose=True,
        force_term_color=True,
    )


@cli.cmd()
def foo() -> None:
    print(':dt')
    run_cmd_args(
        sys.executable, __file__, 'bar',
        verbose=True,
        force_term_color=True,
    )


@cli.cmd()
def bar() -> None:
    for i in range(10):
        print('bar', i, ':t')
        sleep(0.2)


if __name__ == '__main__':
    # pox test/popen_no_stuck_printing.py main
    cli.run()

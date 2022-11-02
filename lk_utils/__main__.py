from argsense import cli

from . import fs


@cli.cmd()
def mklink(src, dst, overwrite: bool = None):
    src = fs.normpath(src)
    dst = fs.normpath(dst)
    dst = _dst_or_dst_under(src, dst)
    fs.make_link(src, dst, overwrite)
    print('[green]soft-link done:[/] '
          '[red]{}[/] -> [cyan]{}[/]'.format(src, dst), ':r')


@cli.cmd()
def move(src, dst, overwrite: bool = None):
    src = fs.normpath(src)
    dst = fs.normpath(dst)
    dst = _dst_or_dst_under(src, dst)
    fs.move(src, dst, overwrite)
    print('[green]move done:[/] '
          '[red]{}[/] -> [cyan]{}[/]'.format(src, dst), ':r')


def _dst_or_dst_under(src: str, dst: str) -> str:
    from os.path import basename, exists
    if exists(dst) and basename(dst) != (x := basename(src)):
        dst += '/' + x
    return dst


if __name__ == '__main__':
    cli.run()

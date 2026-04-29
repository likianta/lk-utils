import typing as tp
from argsense import cli
from os.path import basename
from os.path import exists
from . import fs


@cli
def mklink(src, dst, overwrite: tp.Optional[bool] = None) -> None:
    src = fs.normpath(src)
    dst = fs.normpath(dst)
    dst = _dst_or_dst_under(src, dst)
    fs.make_link(src, dst, overwrite)
    print(
        '[green]soft-link done:[/] [red]{}[/] -> [cyan]{}[/]'.format(src, dst),
        ':r',
    )


@cli
def move(src, dst, overwrite: tp.Optional[bool] = None) -> None:
    src = fs.normpath(src)
    dst = fs.normpath(dst)
    dst = _dst_or_dst_under(src, dst)
    fs.move(src, dst, overwrite)
    print(
        '[green]move done:[/] [red]{}[/] -> [cyan]{}[/]'.format(src, dst), ':r'
    )


@cli
def zip(src: str, dst: str = '', compression_level: str = 'normal') -> None:
    out = fs.zip(
        src,
        dst,
        overwrite=True,
        compression_level=compression_level,
    )
    print('done: {} ({})'.format(out, fs.filesize(out, str)), ':t')


@cli
def unzip(src: str, dst: str = '', **kwargs) -> None:
    out = fs.unzip(src, dst, overwrite=True, **kwargs)
    print('done: {}'.format(out), ':t')


def _dst_or_dst_under(src: str, dst: str) -> str:
    if exists(dst) and basename(dst) != (x := basename(src)):
        dst += '/' + x
    return dst


if __name__ == '__main__':
    cli.run()

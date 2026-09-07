import os
import os.path
import typing as tp

from argsense import cli
from neoprint import print

from . import filesys as fs
from .text_util import regex as re
from .time import now


@cli
def download(
    url: str, dst: str = '', progress: bool = False, auto_extract: bool = False
) -> None:
    """
    Args:
        progress (-p):
        auto_extract (-e):
    """

    def get_file_path() -> str:
        if dst:
            if fs.isdir(dst):
                return fs.normpath(
                    '{}/{}'.format(dst, _get_file_name_from_url())
                )
            else:
                return fs.normpath(dst)
        else:
            return fs.normpath(
                '{}/Downloads/{}'.format(
                    os.environ['HOME'], _get_file_name_from_url()
                )
            )

    def _get_file_name_from_url() -> str:
        if m := re.match(r'\w+:///?(.+)', url):
            a = tp.cast(str, m.group(1))
        else:
            a = url
        b = a.rstrip('/')
        if '/' in b:
            c = b.rsplit('/', 1)[1]
        else:
            raise Exception(url)
        if '.' in c:
            d, e = c.rsplit('.', 1)
            if re.fullmatch(r'[a-zA-Z0-9]+', e):
                ext = e.lower()
            else:
                ext = ''
        else:
            d = c
            ext = ''
        if any(
            x in d
            for x in (
                '<',
                '>',
                '|',
                '?',
                '*',
                ':',
                '~',
                '=',
                '$',
                '#',
                '!',
                '{',
                '}',
            )
        ):
            file_stem_name = 'file-{}'.format(now('ymd-hns'))
        else:
            file_stem_name = d
        return '{}.{}'.format(file_stem_name, ext).rstrip('.')

    file = get_file_path()

    if auto_extract:
        if file.endswith(('.zip', '.7z')):
            extract = True
        else:
            extract = False
    else:
        extract = False

    fs.download(
        url,
        file,
        overwrite=True,
        progress=progress,
        extract=extract,
        keep_file=True,
    )
    print(':nt', 'file is downloaded', file)


@cli
def mklink(src: str, dst: str, overwrite: tp.Optional[bool] = None) -> None:
    src = fs.normpath(src)
    dst = fs.normpath(dst)
    dst = _dst_or_dst_under(src, dst)
    fs.make_link(src, dst, overwrite)
    print('soft-link done: {} -> {}'.format(src, dst), ':r2')


@cli
def move(src, dst, overwrite: tp.Optional[bool] = None) -> None:
    src = fs.normpath(src)
    dst = fs.normpath(dst)
    dst = _dst_or_dst_under(src, dst)
    fs.move(src, dst, overwrite)
    print('move done: {} -> {}'.format(src, dst), ':r2')


@cli
def zip(
    src: str,
    dst: str = '',
    compression_level: str = 'normal',
    progress: bool = False,
) -> None:
    """
    params:
        progress (-p): show progress bar
    """
    out = fs.zip(
        src,
        dst,
        overwrite=True,
        compression_level=compression_level,  # type: ignore
        progress=progress,
    )
    print('done: {} ({})'.format(out, fs.filesize(out, str)), ':t')


@cli
def unzip(src: str, dst: str = '', **kwargs) -> None:
    out = fs.unzip(src, dst, overwrite=True, **kwargs)
    print('done: {}'.format(out), ':t')


def _dst_or_dst_under(src: str, dst: str) -> str:
    if fs.exist(dst) and os.path.basename(dst) != (x := os.path.basename(src)):
        dst += '/' + x
    return dst


if __name__ == '__main__':
    cli.run()

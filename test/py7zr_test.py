from argsense import cli
from lk_utils import fs


@cli
def test_zip(
    src: str, dst: str = '', compression_level: str = 'normal'
) -> None:
    out = fs.zip(
        src,
        dst,
        overwrite=True,
        progress=_plain_print,
        compression_level=compression_level,
    )
    print('done', fs.filesize(out, str), ':t')


@cli
def test_unzip(src: str, dst: str = '', **kwargs) -> None:
    fs.unzip(src, dst, overwrite=True, progress=_plain_print, **kwargs)
    print(':t', 'done')


def _plain_print(prog: fs.ProgressItem) -> None:
    print(
        '[{}/{}] {} ({:.2%})'.format(
            prog.index, prog.total, prog.text, prog.percent
        )
    )


if __name__ == '__main__':
    cli.run()

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
        progress=True,
        compression_level=compression_level,
    )
    print('done', fs.filesize(out, str), ':t')


@cli
def test_unzip(src: str, dst: str = '') -> None:
    fs.unzip(src, dst, overwrite=True, progress=True)
    print(':t', 'done')


if __name__ == '__main__':
    cli.run()

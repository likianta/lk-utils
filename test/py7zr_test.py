from argsense import cli
from lk_utils import fs


@cli
def test_zip(src: str, dst: str = '') -> None:
    out = fs.zip(src, dst, overwrite=True, progress=True)
    print(fs.filesize(out, str), ':t')


@cli
def test_unzip(src: str, dst: str = '') -> None:
    fs.unzip(src, dst, overwrite=True, progress=True)
    print(':t', 'done')


if __name__ == '__main__':
    cli.run()

from argsense import cli


@cli.cmd()
def mklink(src, dst, overwrite: bool = None):
    import os
    from .filesniff import make_link
    
    if os.path.exists(dst) and \
            os.path.basename(dst) != (x := os.path.basename(src)):
        dst += '/' + os.path.basename(x)
    
    make_link(src, dst, overwrite)
    print('[green]soft-link done:[/] '
          '[red]{}[/] -> [cyan]{}[/]'.format(src, dst), ':r')


if __name__ == '__main__':
    cli.run()

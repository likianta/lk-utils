from argsense import cli


@cli.cmd()
def mklink(src, dst, overwrite: bool = None):
    import os
    from .filesniff import mklink
    
    if os.path.exists(dst) and \
            os.path.basename(dst) != (x := os.path.basename(src)):
        dst += '/' + os.path.basename(x)
    
    mklink(src, dst, overwrite)
    print('[green]soft-link done:[/] '
          '[red]{}[/] -> [cyan]{}[/]'.format(src, dst), ':r')


if __name__ == '__main__':
    cli.run()

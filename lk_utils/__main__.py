from argsense import cli


@cli.cmd()
def mklink(src, dst, exist_ok=True):
    import os
    from .subproc import mklink
    
    if os.path.exists(dst) and \
            os.path.basename(dst) != (x := os.path.basename(src)):
        dst += '/' + os.path.basename(x)
    
    mklink(src, dst, exist_ok)
    print('[green]soft-link done:[/] '
          '[red]{}[/] -> [cyan]{}[/]'.format(src, dst), ':r')


if __name__ == '__main__':
    cli.run()

import typing as t


class E:
    class Unreachable(Exception):
        # the code should not reach here.
        pass


class T:
    FileMode = t.Literal['a', 'r', 'rb', 'w', 'wb']
    FileType = t.Literal[
        'auto', 'binary', 'json', 'pickle', 'plain', 'toml', 'yaml'
    ]


def load(
    file: str,
    type: T.FileType = 'auto',
    **kwargs
) -> t.Union[str, bytes, dict, list, t.Any]:
    # TODO: add csv support
    if type == 'auto':
        type = _detect_file_type(file)
    with open(
        file,
        mode='rb' if type in ('binary', 'pickle') else 'r',
        encoding=kwargs.pop('encoding', 'utf-8'),
    ) as f:
        if type == 'plain':
            # out = f.read()
            # # strip BOM charset from the beginning of the file.
            # # https://blog.csdn.net/liu_xzhen/article/details/79563782
            # if out.startswith(u'\ufeff'):
            #     out = out.encode('utf-8')[3:].decode('utf-8')
            return f.read()
        if type == 'binary':
            return f.read()
        if type == 'json':
            from json import load as jload
            return jload(f, **kwargs)
        if type == 'yaml':  # pip install pyyaml
            from yaml import safe_load as yload
            return yload(f)
        if type == 'toml':  # pip install toml
            from toml import load as tload  # noqa
            return tload(f, **kwargs)
        if type == 'pickle':
            from pickle import load as pload
            return pload(f, **kwargs)  # noqa
    raise E.Unreachable


def dump(
    data: t.Any,
    file: str,
    type: T.FileType = 'auto',
    ensure_line_feed: bool = True,
    **kwargs
) -> None:
    # TODO: add csv support
    if type == 'auto':
        type = _detect_file_type(file)
    with open(
        file,
        mode='wb' if type in ('binary', 'pickle') else 'w',
    ) as f:
        if type == 'plain':
            if not isinstance(data, str):
                sep = kwargs.pop('sep', '\n')
                data = sep.join(map(str, data))
            if ensure_line_feed and not data.endswith('\n'):
                data += '\n'
            f.write(data)
        elif type == 'json':
            from json import dump as jdump
            kwargs = {
                'default'     : str,
                #   this is helpful to resolve things like `pathlib.PosixPath`.
                'ensure_ascii': False,
                #   https://www.cnblogs.com/zdz8207/p/python_learn_note_26.html
                'indent'      : 4,
                **kwargs,
            }
            jdump(data, f, **kwargs)
        elif type == 'yaml':
            from yaml import dump as ydump
            kwargs = {
                'allow_unicode': True,
                'sort_keys'    : False,
                **kwargs
            }
            ydump(data, f, **kwargs)
        elif type == 'pickle':
            from pickle import dump as pdump
            pdump(data, f, **kwargs)  # noqa
        elif type == 'toml':
            from toml import dump as tdump  # noqa
            tdump(data, f, **kwargs)
        elif type == 'binary':
            f.write(data)
        else:
            raise E.Unreachable


def _detect_file_type(filename: str) -> T.FileType:
    if filename.endswith(('.txt', '.htm', '.html', '.md', '.rst')):
        return 'plain'
    elif filename.endswith(('.json', '.json5')):
        return 'json'
    elif filename.endswith(('.yaml', '.yml')):  # pip install pyyaml
        return 'yaml'
    elif filename.endswith(('.toml', '.tml')):  # pip install toml
        return 'toml'
    elif filename.endswith(('.pkl',)):
        return 'pickle'
    else:  # fallback to 'plain'
        return 'plain'


# alias
rd = read = loads = load
wr = write = dumps = dump

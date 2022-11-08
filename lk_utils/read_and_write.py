import typing as t
from contextlib import contextmanager


class T:
    Content = t.Union[str, t.Iterable[str]]
    Data = t.Any
    File = str
    FileMode = t.Literal['a', 'r', 'rb', 'w', 'wb']
    FileHandle = t.Union[t.TextIO, t.BinaryIO]
    FileType = t.Literal['binary', 'json', 'pickle', 'plain', 'toml', 'yaml']


@contextmanager
def ropen(file: T.File,
          mode: T.FileMode = 'r',
          encoding='utf-8') -> T.FileHandle:
    if 'b' in mode:
        handle = open(file, mode=mode)
    else:
        handle = open(file, mode=mode, encoding=encoding)
    try:
        yield handle
    finally:
        handle.close()


@contextmanager
def wopen(file: T.File,
          mode: T.FileMode = 'w',
          encoding='utf-8') -> T.FileHandle:
    if 'b' in mode:
        handle = open(file, mode=mode)
    else:
        handle = open(file, mode=mode, encoding=encoding)
    try:
        yield handle
    finally:
        handle.close()


def read_file(file: T.File) -> str:
    with ropen(file) as f:
        content = f.read()
        # https://blog.csdn.net/liu_xzhen/article/details/79563782
        if content.startswith(u'\ufeff'):
            # Strip BOM charset at the start of content.
            content = content.encode('utf-8')[3:].decode('utf-8')
    return content


def read_lines(file: T.File, offset=0) -> t.List[str]:
    """
    References:
        https://blog.csdn.net/qq_40925239/article/details/81486637
    """
    with ropen(file) as f:
        out = [line.rstrip() for line in f]
    return out[offset:]


def write_file(content: T.Content, file: T.File,
               mode: T.FileMode = 'w', sep='\n'):
    """
    ref:
        python 在最后一行追加 https://www.cnblogs.com/zle1992/p/6138125.html
        python map https://blog.csdn.net/yongh701/article/details/50283689
    """
    if not isinstance(content, str):
        content = sep.join(map(str, content))
    if not content.endswith('\n'):  # add line feed
        content += '\n'
    with wopen(file, mode) as f:
        f.write(content)


# ------------------------------------------------------------------------------

def loads(file: T.File, ftype: T.FileType = None, **_) -> T.Data:
    if ftype is None:
        ftype = _detect_file_type(file)
    if ftype == 'plain':
        return read_file(file)
    elif ftype == 'binary':
        with ropen(file, 'rb') as f:
            return f.read()
    elif ftype == 'json':
        from json import load as jload
        with ropen(file) as f:
            return jload(f)
    elif ftype == 'yaml':  # pip install pyyaml
        from yaml import safe_load as yload  # noqa
        with ropen(file) as f:
            return yload(f)
    elif ftype == 'toml':  # pip install toml
        from toml import load as tload  # noqa
        with ropen(file) as f:
            return tload(f)
    elif ftype == 'pickle':
        from pickle import load as pload
        with ropen(file, 'rb') as f:
            return pload(f)
    else:
        # unregistered file types, like: .js, .css, .py, etc.
        return read_file(file)


def dumps(data: T.Data, file: T.File,
          ftype: T.FileType = None, **kwargs) -> None:
    if ftype is None:
        ftype = _detect_file_type(file)
    
    if ftype == 'plain':
        write_file(data, file, sep=kwargs.get('sep', '\n'))
    
    elif ftype == 'json':
        from json import dump as jdump
        with wopen(file) as f:
            jdump(data, f, ensure_ascii=False, default=str,
                  indent=kwargs.get('indent', 4))
            #   ensure_ascii=False
            #       https://www.cnblogs.com/zdz8207/p/python_learn_note_26.html
            #   default=str
            #       when something is not serializble, callback `__str__`.
            #       it is useful to resolve `pathlib.PosixPath`.
    
    elif ftype == 'yaml':  # pip install pyyaml
        from yaml import dump as ydump  # noqa
        with wopen(file) as f:
            ydump(data, f, **{'sort_keys': False, **kwargs})
    
    elif ftype == 'pickle':
        from pickle import dump as pdump
        with wopen(file, 'wb') as f:
            pdump(data, f, **kwargs)
    
    elif ftype == 'toml':  # pip install toml
        from toml import dump as tdump  # noqa
        with wopen(file) as f:
            tdump(data, f, **kwargs)
    
    elif ftype == 'binary':
        with wopen(file, 'wb') as f:
            f.write(data)
    
    else:
        raise Exception(ftype, file, type(data))


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
    else:
        return 'plain'
        # raise Exception(f'Unknown file type: {filename}')


# ------------------------------------------------------------------------------

@contextmanager
def read(file: T.File, **kwargs) -> t.Any:
    """ Open file as a read handle.
    
    Usage:
        with read('input.json') as r:
            print(len(r))
    """
    data = loads(file, **kwargs)
    yield data


@contextmanager
def write(file: T.File, data: t.Any = None, **kwargs):
    """ Create a write handle, file will be generated after the `with` block
        closed.
        
    Args:
        file: See `dumps`.
        data (list|dict|set|str): If the data type is incorrect, an Assertion
            Error will be raised.
        kwargs: See `dumps`.
        
    Usage:
        with write('output.json', []) as w:
            for i in range(10):
                w.append(i)
        print('See "result.json:1"')
    """
    assert isinstance(data, (list, dict, set))
    yield data
    dumps(data, file, **kwargs)

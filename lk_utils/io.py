import typing as t
from contextlib import contextmanager
from os.path import basename
from os.path import exists

import lk_logger


class E:
    class Unreachable(Exception):
        # the code should not reach here.
        pass


class T:
    ContextHolder = t.Iterator
    DataHolder = t.TypeVar('DataHolder', bound=t.Any)
    FileMode = t.Literal['a', 'r', 'rb', 'w', 'wb']
    FileType = t.Literal[
        'auto',
        'binary',
        'excel',
        'json',
        'pickle',
        'plain',
        'table',
        'toml',
        'yaml',
    ]


def load(
    file: str,
    type: T.FileType = 'auto',
    *,
    default: t.Any = None,
    **kwargs
) -> t.Any:  # t.Union[str, dict, list, t.List[list], t.Any]:
    """
    kwargs:
        for excels:
            sheet: int | str
                int: get sheet by index. 0 based.
                str: get sheet by name. case sensitive.
            progress: bool (=False)
                since pyexcel opening excel file is slow, this option shows a -
                progress bar in the console.
                TODO: this is a workaround option. we consider using `xlrd` to -
                    replace `pyexcel` to fix this issue.
    """
    if default is not None and not exists(file):
        dump(default, file)
        return default
    if type == 'auto':
        type = _detect_file_type(file)
    
    if type == 'excel':
        import pyexcel  # pip install lk-utils[exl]
        if kwargs.get('progress'):
            with lk_logger.spinner(
                'opening excel "{}"...'.format(basename(file))
            ):
                book_data = pyexcel.get_book_dict(file_name=file)
        else:
            book_data = pyexcel.get_book_dict(file_name=file)
        if (x := kwargs.get('sheet')) is not None:
            if isinstance(x, str):  # by sheet name
                try:
                    return book_data[x]
                except KeyError:
                    raise KeyError(tuple(book_data.keys()), x)
            elif isinstance(x, int):  # by sheet number
                for i, v in enumerate(book_data.values()):
                    if i == x:
                        return v
                else:
                    raise IndexError(tuple(book_data.keys()), x)
            else:
                raise TypeError(x)
        else:
            # return OrderedDict ({sheet_name: [row, ...], ...})
            return book_data
    assert type != 'excel'
    
    with open(
        file,
        mode='rb' if type in ('binary', 'pickle') else 'r',
        encoding=kwargs.pop(
            'encoding', None if type in ('binary', 'pickle') else 'utf-8'
        ),
    ) as f:
        if type == 'plain':
            # out = f.read()
            # # strip BOM charset from the beginning of the file.
            # # https://blog.csdn.net/liu_xzhen/article/details/79563782
            # if out.startswith(u'\ufeff'):
            #     out = out.encode('utf-8')[3:].decode('utf-8')
            return f.read()
        elif type == 'json':
            from json import load as jload
            return jload(f, **kwargs)
        elif type == 'yaml':  # pip install pyyaml
            from yaml import safe_load as yload
            return yload(f)
        elif type == 'table':
            import csv
            return list(csv.reader(f))
        elif type == 'pickle':
            from pickle import load as pload
            return pload(f, **kwargs)  # noqa
        elif type == 'binary':
            return f.read()
        elif type == 'toml':  # pip install toml
            from toml import load as tload  # noqa
            return tload(f, **kwargs)
        else:
            raise E.Unreachable


def dump(
    data: t.Any,
    file: str,
    type: T.FileType = 'auto',
    ensure_line_feed: bool = True,
    **kwargs
) -> None:
    if type == 'auto':
        type = _detect_file_type(file)
    with open(
        file,
        mode='wb' if type in ('binary', 'excel', 'pickle') else 'w',
        encoding=kwargs.pop(
            'encoding',
            None if type in ('binary', 'excel', 'pickle') else 'utf-8'
        ),
        newline='' if type == 'table' else None,
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
            # noinspection PyTypeChecker
            jdump(data, f, **kwargs)
        elif type == 'yaml':
            from yaml import dump as ydump
            kwargs = {
                'allow_unicode': True,
                'sort_keys'    : False,
                **kwargs
            }
            ydump(data, f, **kwargs)
        elif type == 'table':
            # data is a list of lists.
            import csv
            csv.writer(f).writerows(data)
        elif type == 'pickle':
            from pickle import dump as pdump
            pdump(data, f, **kwargs)  # noqa
        elif type == 'excel':
            pass  # TODO
        elif type == 'binary':
            f.write(data)
        elif type == 'toml':
            from toml import dump as tdump  # noqa
            tdump(data, f, **kwargs)
        else:
            raise E.Unreachable


def _detect_file_type(filename: str) -> T.FileType:
    if filename.endswith(('.txt', '.htm', '.html', '.md', '.rst')):
        return 'plain'
    elif filename.endswith(('.json', '.json5')):
        return 'json'
    elif filename.endswith(('.yaml', '.yml')):  # pip install pyyaml
        return 'yaml'
    elif filename.endswith(('.csv',)):
        return 'table'
    elif filename.endswith(('.toml', '.tml')):  # pip install toml
        return 'toml'
    elif filename.endswith(('.pkl',)):
        return 'pickle'
    elif filename.endswith(('.xlsx', '.xls')):
        return 'excel'
    else:  # fallback to 'plain'
        return 'plain'


# DELETE?
@contextmanager
def writing_to(
    file: str, data_holder: T.DataHolder = None, **kwargs
) -> T.ContextHolder[T.DataHolder]:
    if data_holder is None:
        data_holder = []
    yield data_holder
    dump(data_holder, file, **kwargs)

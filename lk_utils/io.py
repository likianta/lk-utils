import os
import typing as t


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
    """
    if default is not None and not os.path.exists(file):
        dump(default, file)
        return default
    if type == 'auto':
        type = _detect_file_type(file)
    
    if type == 'excel':
        def read_sheet(sheet) -> t.List[list]:
            return [
                [_prefer_int(value) for value in sheet.row_values(rowx)]
                for rowx in range(sheet.nrows)
            ]
        
        def _prefer_int(value: t.Any) -> t.Union[int, t.Any]:
            if isinstance(value, float) and value.is_integer():
                return int(value)
            return value
        
        import xlrd  # pip install "lk-utils[exl]"
        book = xlrd.open_workbook(file)
        if (x := kwargs.get('sheet')) is not None:
            if isinstance(x, str):  # by sheet name
                sheet = book.sheet_by_name(x)
            elif isinstance(x, int):  # by sheet number
                sheet = book.sheet_by_index(x)
            else:
                raise TypeError(x)
            return read_sheet(sheet)
        else:
            return {sheet.name: read_sheet(sheet) for sheet in book.sheets()}
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
            raise Exception('unreachable case')


def dump(
    data: t.Any,
    file: str,
    type: T.FileType = 'auto',
    ensure_line_feed: bool = True,
    **kwargs
) -> None:
    """
    file types:
        excel:
            data type:
                rows | {sheet_name: rows, ...}
                    rows: (row, ...)
                        row: (any value, ...)
            available kwargs:
                align: 'left' | 'center' | 'right'
                autofit: bool, default False.
                bold: bool
                border: int
                font_name: str
                font_size: int
                prompt: bool, default False.
                    if saving file crashed by other program occupying, will -
                    prompt user to close that program and try saving again.
                    we use `input` to wait user to do it.
                    be noticed this option is only available for '.xlsx' files -
                    and on windows.
                strings_to_numbers: bool
                strings_to_urls: bool
                text_wrap: bool
                valign: 'top' | 'vcenter' | 'bottom'
    """
    if type == 'auto':
        type = _detect_file_type(file)
    
    if type == 'excel':
        import xlsxwriter  # pip install "lk-utils[exl]"
        from xlsxwriter.exceptions import FileCreateError
        
        options = {'default_format_properties': {}}
        for k, v in {
            'strings_to_numbers': True,
            'strings_to_urls'   : False,
        }.items():
            options[k] = kwargs.get(k, v)
        for k, v in {
            'align'    : None,  # cell text horizontal alignment.
            'bold'     : None,  # font bold
            'border'   : None,  # cell border
            'font_name': 'Microsoft YaHei UI',
            'font_size': None,
            'text_wrap': None,
            'valign'   : None,  # cell text vertical alignment.
        }.items():
            if k in kwargs:
                options['default_format_properties'][k] = kwargs[k]
            elif v is not None:
                options['default_format_properties'][k] = v
        
        book = xlsxwriter.Workbook(filename=file, options=options)
        autofit = kwargs.get('autofit', False)
        
        if not isinstance(data, dict):
            data = {'sheet 1': data}
        for sheet_name, rows in data.items():
            sheet = book.add_worksheet(sheet_name)
            for rowx, row in enumerate(rows):
                for colx, value in enumerate(row):
                    sheet.write(rowx, colx, value)
            if autofit:
                sheet.autofit()
        
        try:
            book.close()
        except FileCreateError as e:
            if kwargs.get('prompt'):
                x = input(
                    'permission denied when saving excel: "{}"!\n'
                    'please close the opened file manually and press "Y" to '
                    'retry to save: '
                )
                if x.lower() == 'y':
                    book.close()
                    return
            raise e
        return
    assert type != 'excel'
    
    with open(
        file,
        mode='wb' if type in ('binary', 'pickle') else 'w',
        encoding=kwargs.pop(
            'encoding', None if type in ('binary', 'pickle') else 'utf-8'
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
            raise Exception('unreachable case')


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

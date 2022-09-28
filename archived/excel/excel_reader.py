import typing as t

import xlrd

from ..subproc import new_thread

"""
假设表格为:
    in.xlsx
          | A        | B   | C
        --|----------|-----|--------
        1 | name     | age | gender
        2 | li ming  | 18  | male
        3 | wang lin | 22  | male
        4 | zhao yan | 25  | female

使用方法:
    # 导入模块
    from excel_reader import ExcelReader
    
    # 创建一个 reader, 并选择第一个 sheet 读取 (默认).
    file = 'in.xlsx'
    reader = ExcelReader(file, sheetx=0)
    
    # 获得标题行数据
    header = reader.get_header()
    # -> ['name', 'age', 'gender']
    
    # 获得第二行数据, 以列表格式
    row = reader.row_values(1)
    # -> ['li ming', 18, 'male'] (注意这里的 18 是 int 类型的值)
    
    # 获得第二行数据, 以字典格式
    row = reader.row_dict(1)
    # -> {'name': 'li ming', 'age': 18, 'gender': 'male'}
    
    # 获得第一列数据, 通过指定序号
    col = reader.col_values(0)
    # -> ['li ming', 'wang lin', 'zhao yan']
    
    # 获得第一列数据, 通过指定标题头
    col = reader.col_values('name')
    # -> ['li ming', 'wang lin', 'zhao yan']
    
    # 获得第一列数据, 通过模糊搜索标题头
    col = reader.col_values(['name', '姓名', '名字'])
    # -> ['li ming', 'wang lin', 'zhao yan']
    
    # 定位标题头所在的位置, 通过指定标题头
    colx = reader.find_colx('gender')
    # -> 2 (当搜索不到时, 会返回 -1)
    
    # 定位标题头所在的位置, 通过模糊搜索标题头
    colx = reader.find_colx(['gender', '性别', '男女'])
    # -> 2 (当搜索不到时, 会返回 -1)
    
    # 获得总行数
    rowsnum = reader.get_num_of_rows()
    # -> 4
    
    # 获得总列数
    colsnum = reader.get_num_of_cols()
    # -> 3
    
    # 获得总 sheet 数
    sheetsnum = reader.get_num_of_sheets()
    # -> 1
    
    # 获得一个行数范围, 并指定从第二行开始
    for rowx in reader.get_range(1):
        pass
    # 此方法相当于: `for rowx in range(1, reader.get_num_of_rows())`
    
    # 切换到第二个 sheet
    reader.activate_sheet(1)
    # 注意: 如果要切换到的 sheet 不存在, 会报错.
    
"""


class T:
    Dict = t.Dict
    List = t.List
    Optional = t.Optional
    
    WorkBook = t.Optional[xlrd.Book]
    WorkSheet = t.Optional[xlrd.sheet.Sheet]
    
    Header = t.List[str]
    
    CellValue = t.Union[None, bool, float, int, str]
    RowValues = t.Sequence[CellValue]
    ColValues = t.Sequence[CellValue]
    SheetName = t.Optional[str]


class Header:
    strict: bool
    _header_a: T.RowValues
    _header_b: T.List[str]
    
    def __init__(self, header: T.RowValues, strict=True):
        """
        NOTE: 特别注意, 我们把 header_row 中的所有对象都转换成 str 类型了. 也就
            是如果参数 header 是 ['A', 2019, False], 则 self._header 是 ['A',
            '2019', 'False'].
            之所以这样做, 是有原因的, 见 self.find_colx() 注释.
        """
        self.strict = strict
        self._header_a = header
        self._header_b = [str(x).lower() for x in header]
        if len(set(self._header_b)) != len(self._header_b):
            print(':v3p', 'There are duplicate fields in your header, field '
                          'index locator may work incorrectly!')
    
    @property
    def header(self) -> T.RowValues:
        if self.strict:
            return self._header_a
        else:
            return self._header_b
    
    def find_colx(self, *query: str) -> t.Optional[int]:
        """
        Args:
            query: accept multiple query words
        """
        for i in query:
            if i in self._header_a:
                return self._header_a.index(i)
        for i in (str(x).lower() for x in query):
            if i in self._header_b:
                return self._header_b.index(i)
        return None


class ExcelReader:
    filepath: str
    _book: T.WorkBook
    _sheet: T.WorkSheet
    _header: T.Optional[Header]
    _background_thread = None
    
    def __init__(self, filepath: str, sheetx: t.Optional[int] = 0, **kwargs):
        """
        Args:
            filepath: '.xls' or '.xlsx' file.
            sheetx: int.
                which sheet to activate once after workbook connected.
                pass None to not initialize sheet at start.
                this value cannot exceed the total sheet number, or it will
                raise ValueError.
                You can laterly use `activate_sheet(int sheetx)` to change it.
            **kwargs:
                formatting_info: bool[default False].
                    whether to keep source table formats, e.g. note marks, bg
                    colors, fg colors.
                    be notice this only valid for '.xls' file type. see also
                    http://www.bubuko.com/infodetail-2547924.html
                strict: bool[default False]
                    example True:
                        a header would be ['A', 'b', 3, True, ...]
                    example False:
                        a header would be ['a', 'b', '3', 'true', ...]
                    see also `Header > __init__ > (param) strict`.
        """
        self.filepath = filepath
        self._background_thread = self._loading(
            filepath,
            formatting_info=False if filepath.endswith('.xlsx')
            else kwargs.get('formatting_info', False),
            sheetx=sheetx
        )
    
    @new_thread()
    def _loading(self, filepath: str, formatting_info=False,
                 sheetx: T.Optional[int] = 0):
        """
        Notes:
            if file is large, it consumes appreciable seconds of time. we'd
            better put it in a new thread.
        """
        self._book = xlrd.open_workbook(
            filepath, formatting_info=formatting_info
        )
        if sheetx is not None:
            self._sheet = self._book.sheet_by_index(sheetx)
        else:
            self._sheet = None
    
    @property
    def book(self) -> T.WorkBook:
        if self._background_thread.is_alive():
            self._background_thread.join()
        return self._book
    
    @property
    def sheet(self) -> T.Optional[T.WorkSheet]:
        if self._background_thread.is_alive():
            self._background_thread.join()
        return self._sheet
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()
        
    def _close(self):
        self._background_thread.join()
        self._book = None
        self._sheet = None
    
    def activate_sheet(self, sheetx: int):
        """ Activate a sheet by sheetx. """
        assert sheetx < self.get_num_of_sheets()
        self._sheet = self.book.sheet_by_index(sheetx)
        if self.get_num_of_rows() > 0:
            self._header = Header(self.row_values(0), strict=False)
        else:
            self._header = None
    
    # --------------------------------------------------------------------------
    
    def get_num_of_sheets(self) -> int:
        return self.book.nsheets
    
    def get_name_of_sheets(self) -> T.List[T.SheetName]:
        return self.book.sheet_names()
    
    def get_num_of_rows(self) -> int:
        return self.sheet.nrows
    
    def get_num_of_cols(self) -> int:
        return self.sheet.ncols
    
    # --------------------------------------------------------------------------
    
    @property
    def header(self) -> T.RowValues:
        return self._header or []
    
    def get_sheet(self, sheetx=None):
        """
        NOTE: this method doesn't change the self.sheet. otherwize you can use
            self.activate_sheet().
        """
        if sheetx is None:
            return self.sheet
        else:
            return self.book.sheet_by_index(sheetx)
    
    def get_filepath(self) -> str:
        return self.filepath
    
    # --------------------------------------------------------------------------
    
    # noinspection PyUnboundLocalVariable
    @staticmethod
    def _betterint(v: T.CellValue) -> T.CellValue:
        """
        在 excel 中, 所有数字皆以浮点储存. 但考虑到个人需求, 我需要将一些整数在
        python 中以 int 表示. 我将它上升为一个重要的决策. 尽管它可能带来一些负面
        影响 (例如在上下文环境均是浮点数时).
        """
        if isinstance(v, float) and v == (x := int(v)):
            return x
        else:
            return v
    
    def cell_value(self, x, y) -> T.CellValue:
        v = self.sheet.cell(x, y).value
        return self._betterint(v)
    
    def row_values(self, rowx: int) -> T.RowValues:
        return [
            self._betterint(x)
            for x in self.sheet.row_values(rowx)
        ]
    
    def row_dict(self, rowx: int) -> T.Dict[T.CellValue, T.RowValues]:
        return dict(zip(self.header, self.row_values(rowx)))
    
    def col_values(self, query, offset=0) -> T.Optional[T.ColValues]:
        if not isinstance(query, int):
            # str, list, tuple
            if isinstance(query, (str, bool, float)):
                query = (query,)
            if (colx := self._header.find_colx(*query)) == -1:
                return None
        else:
            colx = query
        
        return [
            self._betterint(x)
            for x in self.sheet.col_values(colx)[offset:]
        ]
    
    # --------------------------------------------------------------------------
    # Iterations
    
    def get_range(self, offset=0):
        return range(offset, self.sheet.nrows)
    
    def zip_cols(self, *cols, offset=1):
        if len(cols) == 1:
            return self.col_values(cols[0], offset)
        else:
            return zip(
                *(self.col_values(x, offset) for x in cols)
            )
    
    def enum_cols(self, *cols, offset=1):
        if len(cols) == 1:
            return enumerate(self.col_values(cols[0], offset), offset)
        else:
            return zip(range(offset, self.get_num_of_rows()),
                       *(self.col_values(x, offset) for x in cols))
    
    # noinspection PyArgumentList
    def walk_rows(self, offset=0, fmt='list'):
        """
        Args:
            offset
            fmt ('list'|'dict')
        """
        assert fmt in ('list', 'dict')
        handle = self.row_values if fmt == 'list' else self.row_dict
        return (handle(rowx) for rowx in range(offset, self.sheet.nrows))
    
    # noinspection PyArgumentList
    def enum_rows(self, offset=1, fmt='list'):
        """
        Args:
            offset
            fmt ('list'|'dict')
        """
        assert fmt in ('list', 'dict')
        handle = self.row_values if fmt == 'list' else self.row_dict
        return enumerate(
            (handle(rowx) for rowx in range(offset, self.sheet.nrows)), offset
        )

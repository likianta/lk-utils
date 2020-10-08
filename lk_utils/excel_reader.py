"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : excel_reader.py
@Created : 2019-00-00
@Updated : 2020-09-10
@Version : 1.2.17
@Desc    :
"""
from typing import *

import xlrd

_CellValue = Union[str, bool, int, float, None,]
_ColValues = _RowValues = Iterable

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


class ColIndexLocator:
    _header = None
    
    def __init__(self, header):
        """
        NOTE: 特别注意, 我们把 header_row 中的所有对象都转换成 str 类型了. 也就
            是如果参数 header 是 ['A', 2019, False], 则 self._header 是 ['A',
            '2019', 'False'].
            之所以这样做, 是有原因的, 见 self.find_colx() 注释.
        """
        self._header = tuple(str(x).lower() for x in header)
    
    def find_colx(self, *query: str, ignore_error=False) -> int:
        """
        NOTE: query 仅限 [str] 元素. 这样做的目的是避免 int 元素的二义性.
        """
        for i in (str(x).lower() for x in query):
            if i in self._header:
                return self._header.index(i)
            elif ignore_error:
                return -1
        raise ValueError('Query field not found in the header',
                         f'query: {query}', f'header: {self._header}')


class ExcelReader(ColIndexLocator):
    filepath = ''
    book = None
    sheet = None
    header = None
    
    # noinspection PyMissingConstructor
    def __init__(self, path: str, sheetx=0, formatting_info=False):
        """
        :param path: 传入要读取的文件的路径.
        :param sheetx: int. 选择要激活的 sheet. 默认读取第一个 sheet (sheetx=0),
            最大不超过该 excel 的 sheet 总数. 您也可以通过 self.activate_sheet
            (sheetx) 来切换要读取的 sheet.
        :param formatting_info: bool. 是否保留源表格样式. 例如单元格的批注, 背景
            色, 前景色等.
            注: 只有 ".xls" 支持保留源表格样式, 如果对".xlsx" 使用会直接报错.
            参考: http://www.bubuko.com/infodetail-2547924.html
        """
        self.filepath = path
        if '.xlsx' in path:
            # 当要打开的文件为 ".xlsx" 格式时, 强制 formatting_info 参数为 False.
            # 参考: http://www.bubuko.com/infodetail-2547924.html
            formatting_info = False
        # NOTE: ExcelReader 的实例化方法只能够一次性读取 Excel 到内存中. 如果您
        #   的表格非常大, 那么在此过程中会有明显卡顿.
        self.book = xlrd.open_workbook(path, formatting_info=formatting_info)
        self.activate_sheet(sheetx)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.book, self.sheet
    
    def activate_sheet(self, sheetx: int):
        """ Activate a sheet by sheetx. """
        assert sheetx < self.get_num_of_sheets()
        self.sheet = self.book.sheet_by_index(sheetx)
        if self.get_num_of_rows() > 0:
            self.header = self.row_values(0)
            self._header = tuple(str(x).lower() for x in self.header)
        else:
            self.header = None
            self._header = None
    
    # --------------------------------------------------------------------------
    
    def get_num_of_sheets(self) -> int:
        return self.book.nsheets
    
    def get_name_of_sheets(self) -> List[str]:
        return self.book.sheet_names()
    
    def get_num_of_rows(self) -> int:
        return self.sheet.nrows
    
    def get_num_of_cols(self) -> int:
        return self.sheet.ncols
    
    # --------------------------------------------------------------------------
    
    def get_header(self) -> list:
        return self.header
    
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
    def _betterint(v: Any) -> _CellValue:
        """
        在 excel 中, 所有数字皆以浮点储存. 但考虑到个人需求, 我需要将一些整数在
        python 中以 int 表示. 我将它上升为一个重要的决策. 尽管它可能带来一些负面
        影响 (例如在上下文环境均是浮点数时).
        """
        if isinstance(v, float) and v == (x := int(v)):
            return x
        else:
            return v
    
    def cell_value(self, x, y) -> _CellValue:
        v = self.sheet.cell(x, y).value
        return self._betterint(v)
    
    def row_values(self, rowx: int) -> _RowValues:
        return [
            self._betterint(x)
            for x in self.sheet.row_values(rowx)
        ]
    
    def row_dict(self, rowx: int) -> Dict[Union[str, int], _CellValue]:
        return dict(zip(self.header, self.row_values(rowx)))
    
    def col_values(self, query, offset=0) -> Union[_ColValues, None]:
        if not isinstance(query, int):
            # str, list, tuple
            if isinstance(query, (str, bool, float)):
                query = (query,)
            if (colx := self.find_colx(*query)) == -1:
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
        fmt: 'list'/'dict'
        """
        assert fmt in ('list', 'dict')
        handle = self.row_values if fmt == 'list' else self.row_dict
        return (handle(rowx) for rowx in range(offset, self.sheet.nrows))
    
    # noinspection PyArgumentList
    def enum_rows(self, offset=1, fmt='list'):
        """
        fmt: 'list'/'dict'
        """
        assert fmt in ('list', 'dict')
        handle = self.row_values if fmt == 'list' else self.row_dict
        return enumerate(
            (handle(rowx) for rowx in range(offset, self.sheet.nrows)), offset
        )

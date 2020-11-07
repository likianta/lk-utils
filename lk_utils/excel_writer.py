"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : excel_writer.py
@Created : 2018-00-00
@Updated : 2020-11-07
@Version : 2.4.1
@Desc    : ExcelWriter is a post-packing implementation based on XlsxWriter.
"""
from typing import *
from warnings import filterwarnings
from collections import defaultdict

# shield Python 3.8 SyntaxWarning from XlsxWriter.
filterwarnings('ignore', category=SyntaxWarning)


class TypeHint:
    from xlsxwriter.format import Format as ExlFormat
    from xlsxwriter.workbook import Workbook
    from xlsxwriter.worksheet import Worksheet
    
    WorkBook = Workbook
    WorkSheet = Worksheet
    SheetName = str
    SheetManager = Dict[str, Union[
        List[str], Dict[SheetName, Dict[str, int]]
    ]]
    """ -> {
        'sheets': [sheet_name, ...],
        'sheets_info': {
            sheet_name: {
                'rowx': int, ...
            }, ...
        }
    } """
    
    CellFormat = ExlFormat
    CellValue = Union[str, bool, int, float, None]
    
    ColValues = Iterable
    RowValues = Iterable
    
    ColsValues = List[ColValues]
    RowsValues = List[RowValues]


class ExcelWriter:
    """ ExcelWriter is an encapsulated implementation of xlsxwriter module,
        designed to provide more flexible and ease of use excel writing
        experience.
    
    Refer: https://www.jianshu.com/p/187e6b86e1d9
    Palette: `xlsxwriter.format.Format._get_color`
    """
    __h: str
    _is_constant_memory: bool
    _merge_format: TypeHint.CellFormat
    _sheet_manager: TypeHint.SheetManager
    book: TypeHint.WorkBook
    filepath: str
    rowx: int  # auto increasing row index, see self.writeln, self.writelnx.
    sheet: TypeHint.WorkSheet
    sheetx: int
    
    def __init__(self, filepath: str, sheet_name: Union[str, None] = '',
                 **options):
        """
        :param filepath: a filepath ends with '.xlsx' ('.xls' is not supported).
        :param sheet_name: Union[str, None].
            str: If string is empty, will create a sheet with default name --
                'sheet 1'.
            None: `None` is a special token, it tells ExcelWriter NOT to create
                sheet in `__init__` stage.
        :param options: workbook format.
        """
        self.__h = 'parent'  # just for adjusting lk_logger's hierarchy in
        #   `self.__exit__` and `self.save`.
        self._is_constant_memory = options.get('constant_memory', False)
        self.sheetx = 0
        self.rowx = -1
        self._sheet_manager = {
            'sheets': [],
            'sheets_info': defaultdict(dict),
        }
        
        if not filepath.endswith('.xlsx'):
            raise ValueError(
                'ExcelWriter only supports .xlsx file type.', filepath
            )
        else:
            self.filepath = filepath
        
        # create workbook
        import xlsxwriter
        self.book = xlsxwriter.Workbook(
            filename=filepath,
            options={  # the default options
                'strings_to_numbers'       : True,
                'strings_to_urls'          : False,
                'constant_memory'          : False,
                'default_format_properties': {
                    'font_name': '微软雅黑',  # default "Arial"
                    'font_size': 10,  # default 11
                    # 'bold': False,  # font bold
                    # 'border': 1,  # cell's border
                    # 'align': 'left',  # cell's horizontal alignment
                    # 'valign': 'vcenter',  # cell's vertical alignment
                    # 'text_wrap': False,  # auto line wrap (default False)
                },
                **options
            }
        )
        
        # create sheet (if `sheet_name` is not None)
        if sheet_name is not None:
            self.add_new_sheet(sheet_name)
        
        # the format for merge range
        self._merge_format = self.book.add_format({
            'align' : 'center',
            'valign': 'vcenter',
            # 'text_wrap': False,  # auto line wrap (default False)
        })  # REF: https://blog.csdn.net/lockey23/article/details/81004249

    def activate_sheet(self, sheetx: Union[int, str]):
        if isinstance(sheetx, int):
            sheet_name = self._sheet_manager['sheets'][sheetx]
        elif isinstance(sheetx, str):
            sheet_name = sheetx
        else:
            raise Exception
        # store last sheet's info
        self._sheet_manager['sheets_info'][self.sheet.name]['rowx'] = self.rowx
        # activate new sheet's info
        self.sheet = self.book.get_worksheet_by_name(sheet_name)
        self.rowx = self._sheet_manager['sheets_info'][sheet_name]['rowx']

    def add_new_sheet(self, sheet_name=''):
        # store last sheet's info
        self._sheet_manager['sheets_info'][self.sheet.name]['rowx'] = self.rowx
        
        self.sheetx += 1
        self.rowx = -1
        # create sheet name
        if not sheet_name:
            sheet_name = f'sheet {self.sheetx}'  # -> 'sheet 1', 'sheet 2', ...
        self.sheet = self.book.add_worksheet(sheet_name)
        
        # update new sheet's info
        self._sheet_manager['sheets'].append(sheet_name)
        self._sheet_manager['sheets_info'][sheet_name]['rowx'] = self.rowx

    def __enter__(self):
        """ Return self to use with `with` statement.
        Use case: `with ExcelWriter(filepath) as writer: pass`.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Save and close when leave `with` statement. """
        self.__h = 'grand_parent'  # prompt
        self.save()
        self.__h = 'parent'  # reset
    
    def save(self):
        from xlsxwriter.exceptions import FileCreateError
        try:
            self.book.close()
        except FileCreateError:
            if input('Permission denied on saving excel: \n'
                     '\t\t{}\n'
                     '\tPlease close the opened file manually and input "Y" to '
                     'retry to save.'.format(self.filepath)).lower() == 'y':
                self.book.close()
            else:
                raise FileCreateError
        from .lk_logger import lk
        lk.logt('[ExcelWriter][D1139]', f'Excel saved to "{self.filepath}"',
                h=self.__h)
    
    close = save
    
    # --------------------------------------------------------------------------
    
    def write(self, rowx: int, colx: int, data: TypeHint.CellValue, fmt=None):
        """ Write data to cell.
        
        :param rowx: int. Row number, starts from 0.
        :param colx: int. Col number, starts from 0.
        :param data: Union[str, int, float, bool, None]
        :param fmt: Union[None, Dict]
        """
        self.sheet.write(rowx, colx, data, fmt)
    
    def writeln(self, *row: TypeHint.RowValues, auto_index=False,
                purify_values=False, fmt=None):
        """ Write line of data to cells (with auto line breaks). """
        if purify_values:
            row = self.purify_values(row)
        self.rowx += 1
        if self.rowx == 0 or not auto_index:
            self.sheet.write_row(self.rowx, 0, row, fmt)
        else:
            self.sheet.write(self.rowx, 0, self.rowx, fmt)
            self.sheet.write_row(self.rowx, 1, row, fmt)
    
    def writelnx(self, *row: TypeHint.RowValues, fmt=None):
        self.writeln(*row, auto_index=True, fmt=fmt)
    
    def writerow(self, rowx: int, data: TypeHint.CellValue, offset=0,
                 purify_values=False, fmt=None):
        """ Write row of data to cells. """
        if purify_values:
            data = self.purify_values(data)
        self.sheet.write_row(rowx, offset, data, fmt)
    
    def writecol(self, colx: int, data: TypeHint.CellValue, offset=0,
                 purify_values=False, fmt=None):
        """ Write column of data to cells. """
        if purify_values:
            data = self.purify_values(data)
        self.sheet.write_column(offset, colx, data, fmt)
    
    @staticmethod
    def purify_values(row: TypeHint.RowValues):
        """
        Callers: self.writeln, self.writerow, self.writecol.
        """
        import re
        reg = re.compile(r'\s+')
        return tuple(
            re.sub(reg, ' ', v).strip()
            if isinstance(v, str) else v
            for v in row
        )
    
    # --------------------------------------------------------------------------
    
    def merging_visual(self, rows: TypeHint.RowValues, to_left='<', to_up='^',
                       offset=(0, 0), fmt=None):
        """ Merge cells in "visual" mode.
        Symbol: '<' means merged to the left cell, '^' merged to the upper cell.
        E.g.
            Input: [[ A,  B,  C,  <,  D ],
                    [ ^,  ^,  E,  F,  < ]]
            Output: | A | B | C   * | D |
                    | * | * | E | F | * |
        NOTE:
            1. If you want to draw a rectangle, please use '<' first.
               E.g.
                    Input: [[ A,  B,  <,  C ],
                            [ D,  ^,  <,  E ]]  # notice the second '<' symbol.
                    Output: | A | B   * | C |
                            | D | *   * | E |
               This will be faster than '^' symbol.
            2. For now this method doesn't support symbol '>' or 'v'.
        """
        if self._is_constant_memory is True:
            raise Exception('Cannot effect when constant memory enabled.')
        
        length = tuple(len(x) for x in rows)
        assert min(length) == max(length), 'Please make sure the length of ' \
                                           'each row is equivalent.'
        del length
        
        # encoding mask
        uid = 0  # generally using ascending numbers
        mask_nodes = []  # [<list node>] -> node: [<int uid>]
        uid_2_cell = {}  # {<int uid>: <tuple cell>} -> cell: (rowx, colx)
        
        for rowx, row in enumerate(rows):
            node = []  # [uid1, uid2, uid2, uid3, uid3, ...], the same uid will
            #   be merged later.
            for colx, cell in enumerate(row):
                if cell == to_left:  # cell's value == to_left symbol
                    """ E.g.
                    node = [uid1, uid2] -> [uid1, uid2, uid2]
                    """
                    node.append(node[-1])
                elif cell == to_up:
                    """ E.g.
                    last_node = [uid1, uid2, ... uid9]
                    curr_node = [uid10, ] -> [uid10, uid2]
                    """
                    node.append(mask_nodes[rowx - 1][colx])
                else:
                    uid += 1
                    node.append(uid)
                    uid_2_cell[uid] = cell
            mask_nodes.append(node)
        
        # if cells with the same uid, they will be merged.
        merging_map = {}  # {uid: [(rowx, colx), ...]}
        
        for rowx, row in enumerate(mask_nodes):
            for colx, uid in enumerate(row):
                node = merging_map.setdefault(uid, [])
                node.append((rowx, colx))
        
        for uid, pos in merging_map.items():
            cell = uid_2_cell[uid]
            if len(pos) == 1:
                self.sheet.write(
                    offset[0] + pos[0][0], offset[1] + pos[0][1], cell,
                    fmt or self._merge_format
                )
            else:
                self.sheet.merge_range(
                    offset[0] + pos[0][0], offset[1] + pos[0][1],
                    offset[0] + pos[-1][0], offset[1] + pos[-1][1],
                    cell, cell_format=fmt or self._merge_format
                )
    
    def merging_logical(self, p: Tuple[int, int], q: Tuple[int, int],
                        value: TypeHint.CellValue, fmt=None):
        """ Merge cells in "logical" mode.
        
        NOTE:
            1. 本方法不检查传入的单元格范围是否有交叠或冲突
            2. 注意 p 和 q 的坐标是 (rowx, colx), 也就是先定义第几行, 再定义第几
               列
        """
        if p == q:  # 如果要合并的单元格范围实际上只有一格, 则不要合并. 否则
            #   xlsxwriter 会发出 "合并无效" 的警告.
            return
        self.sheet.merge_range(
            p[0], p[1], q[0], q[1],
            value, cell_format=fmt or self._merge_format
        )

    # --------------------------------------------------------------------------

    def add_cell_format(self, fmt: dict):
        return self.book.add_format(fmt)

import os
import typing as _t
from collections import defaultdict

import xlsxwriter


class T:
    from xlsxwriter.workbook import Workbook as _Workbook
    from xlsxwriter.workbook import Worksheet as _Worksheet
    
    Dict = _t.Dict
    Optional = _t.Optional
    Union = _t.Union
    
    FileExistsScheme = _t.Literal['new_file', 'overwrite']
    
    Rowx = int
    Colx = int
    Cell = _t.Tuple[Rowx, Colx]
    
    class _CellFormat(_t.TypedDict):
        """
        References:
            xlsxwriter.format.Format
            https://xlsxwriter.readthedocs.io/format.html
        """
        # xlsxwriter.format.Format
        align: _t.Literal['left', 'right', 'center']
        valign: _t.Literal['top', 'bottom', 'vcenter']
        textwrap: bool
        num_percent: str
        # TODO: more...
    
    CellFormat = _t.Union[None, _t.Dict[str, str], _CellFormat]
    
    CellValue = _t.Union[None, bool, float, int, str]
    RowValues = _t.Iterable[CellValue]
    ColValues = _t.Iterable[CellValue]
    Header = _t.List[CellValue]
    
    RowsValues = _t.List[RowValues]
    ColsValues = _t.List[ColValues]
    
    WorkBook = _Workbook
    WorkSheet = _Worksheet
    Sheetx = int
    SheetName = _t.Optional[str]
    
    class SheetInfo(_t.TypedDict):
        sheet_name: _t.Optional[str]
        sheetx: int
        rowx: int
    
    SheetManager = _t.Dict[Sheetx, SheetInfo]


class ExcelWriter:
    """ ExcelWriter is an encapsulated implementation of xlsxwriter module,
        designed to provide more flexible and ease of use excel writing
        experience.
    
    References:
        https://www.jianshu.com/p/187e6b86e1d9
        Palette: `xlsxwriter.format.Format._get_color`
    """
    book: T.WorkBook
    filepath: str
    rowx: T.Rowx  # auto increasing row index, see self.writeln, self.writelnx.
    sheet: T.WorkSheet
    
    _is_constant_memory: bool
    _merge_format: T.CellFormat
    _sheet_mgr: '_SheetManager'
    
    def __init__(self, filepath: str, sheet_name: T.SheetName = 'sheet 1',
                 **options):
        """
        Args:
            filepath: a filepath ends with '.xlsx' ('.xls' is not allowed)
            sheet_name:
                str:
                None: `None` is a special token, it tells ExcelWriter NOT to 
                    create sheet in `__init__` stage.
            **options: workbook format.
        """
        if not filepath.endswith('.xlsx'):
            raise Exception(
                'ExcelWriter only supports .xlsx file type.', filepath
            )
        self.filepath = filepath
        
        # create workbook
        self._is_constant_memory = options.get('constant_memory', False)
        self.book = xlsxwriter.Workbook(
            filename=self.filepath,
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
        
        self._sheet_mgr = _SheetManager()
        # create sheet (if `sheet_name` is not None)
        if sheet_name is not None:
            self.add_new_sheet(sheet_name)
        
        self.rowx = 0  # see `self.writeln:docs:notes`
        
        # the format for merge range
        self._merge_format = self.add_format({
            'align' : 'center',
            'valign': 'vcenter',
            # 'text_wrap': False,  # auto line wrap (default False)
        })  # ref: https://blog.csdn.net/lockey23/article/details/81004249
    
    def __enter__(self):
        """ Return self to use with `with` statement.
        Use case: `with ExcelWriter(filepath) as writer: pass`.
        """
        if os.path.exists(self.filepath):
            raise FileExistsError(self.filepath)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Save and close when leave `with` statement. """
        self._save()
    
    # --------------------------------------------------------------------------
    
    def add_format(self, fmt: T.CellFormat) -> T.CellFormat:
        if fmt is None or fmt is {}:
            return None
        elif isinstance(fmt, dict):
            return self.book.add_format(fmt)
        else:
            return fmt
    
    _convert_format = add_format
    
    def add_new_sheet(self, sheet_name=''):
        # save old sheet info
        self._sheet_mgr.update_info(self.sheetx, {
            'sheet_name': self.sheet_name,
            'sheetx'    : self.sheetx,
            'rowx'      : self.rowx,
        })
        
        new_sheetx = self._sheet_mgr.add_new_sheet()
        if sheet_name:
            assert len(sheet_name) <= 31, 'Sheet name is too long!'
            assert sheet_name not in self._sheet_mgr.sheet_by_name, (
                f'The sheet ("{sheet_name}") already exists!'
            )
        else:
            sheet_name = f'sheet {new_sheetx + 1}'
            #   'sheet 1', 'sheet 2', ...
        self._sheet_mgr.activate(new_sheetx)
        
        self.sheet = self.book.add_worksheet(sheet_name)
        
        self.rowx = 0
        
        # add new sheet info
        self._sheet_mgr.update_info(self.sheetx, {
            'sheet_name': sheet_name,
            'sheetx'    : self.sheetx,
            'rowx'      : self.rowx,
        })
    
    def activate_sheet(self, x: T.Union[T.Sheetx, T.SheetName]):
        if isinstance(x, int):
            sheetx = x
            sheet_name = self._sheet_mgr.sheet_by_index[x]
        else:
            sheet_name = x
            sheetx = self._sheet_mgr.sheet_by_name[sheet_name]
        
        self._sheet_mgr.activate(sheetx)
        self.sheet = self.book.get_worksheet_by_name(sheet_name)
        self.rowx = self._sheet_mgr.sheet_info[sheetx]['rowx']
    
    @property
    def sheetx(self) -> T.Sheetx:
        return self._sheet_mgr.current_index
    
    @property
    def sheet_name(self) -> T.SheetName:
        return self._sheet_mgr.current_name
    
    # --------------------------------------------------------------------------
    
    def write(self, rowx: T.Rowx, colx: T.Colx, data: T.CellValue,
              fmt: T.CellFormat = None):
        """ Write data to cell.
        
        :param rowx: int. Row number, starts from 0.
        :param colx: int. Col number, starts from 0.
        :param data: Union[str, int, float, bool, None]
        :param fmt: Union[None, Dict]
        """
        self.sheet.write(rowx, colx, data, self._convert_format(fmt))
    
    def writeln(self, *row: T.CellValue, auto_index=False,
                purify_values=False, fmt: T.CellFormat = None):
        """ Write line of data to cells (with auto line breaks).
        
        Notes:
            `self.rowx` 须保证在调用本方法之前, 处于空行的开始位置; 调用本方法之
            后, 更新到下一空行的开始位置.
        """
        if purify_values:
            row = self.purify_values(row)
        if self.rowx == 0 or not auto_index:
            self.sheet.write_row(self.rowx, 0, row, self._convert_format(fmt))
        else:
            self.sheet.write(self.rowx, 0, self.rowx, self._convert_format(fmt))
            self.sheet.write_row(self.rowx, 1, row, self._convert_format(fmt))
        self.rowx += 1
    
    def writelnx(self, *row: T.CellValue, fmt: T.CellFormat = None):
        self.writeln(*row, auto_index=True, fmt=self._convert_format(fmt))
    
    def writerow(self, rowx: int, data: T.RowValues, offset=0,
                 purify_values=False, fmt: T.CellFormat = None):
        """ Write row of data to cells. """
        if purify_values:
            data = self.purify_values(data)
        self.sheet.write_row(rowx, offset, data, self._convert_format(fmt))
    
    def writecol(self, colx: int, data: T.ColValues, offset=0,
                 purify_values=False, fmt: T.CellFormat = None):
        """ Write column of data to cells. """
        if purify_values:
            data = self.purify_values(data)
        self.sheet.write_column(offset, colx, data, self._convert_format(fmt))
    
    @staticmethod
    def purify_values(row: T.RowValues):
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
    
    def merging_visual(self, rows: T.RowValues, to_left='<', to_up='^',
                       offset=(0, 0), fmt: T.CellFormat = None):
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
        assert (x := min(length)) == max(length), \
            'Please make sure the length of each row is equivalent.'
        self.rowx = x
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
                    self._convert_format(fmt) or self._merge_format
                )
            else:
                self.sheet.merge_range(
                    offset[0] + pos[0][0], offset[1] + pos[0][1],
                    offset[0] + pos[-1][0], offset[1] + pos[-1][1],
                    cell, cell_format=(self._convert_format(fmt) or
                                       self._merge_format)
                )
    
    def merging_logical(self, p: T.Cell, q: T.Cell, value: T.CellValue,
                        fmt: T.CellFormat = None):
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
            value, cell_format=self._convert_format(fmt) or self._merge_format
        )
    
    # --------------------------------------------------------------------------
    
    def save(self, open_after_save=False,
             exists_scheme: T.FileExistsScheme = 'new_file'):
        self._save(exists_scheme)
        if open_after_save:
            os.startfile(os.path.abspath(self.filepath))
    
    close = save
    
    def _save(self, exists_scheme='new_file'):
        """
        Args:
            exists_scheme: Literal['new_file', 'overwrite']
        """
        from time import strftime
        from xlsxwriter.exceptions import FileCreateError
        
        if exists_scheme == 'overwrite' and os.path.exists(self.filepath):
            os.remove(self.filepath)
        
        try:
            self.book.close()
        except FileCreateError as e:  # FIXME: this is uncaught in macOS!
            if exists_scheme == 'new_file':
                self.book.filename = self.filepath = self.filepath.replace(
                    '.xlsx', strftime('_%Y%m%d_%H%M%S.xlsx')
                )
                self.book.close()
            else:
                raise e
        
        print(f'\n\tExcel saved to "{self.filepath}:0"', ':v2p2')


class _SheetManager:
    
    def __init__(self):
        self.current_index = -1
        
        self.sheet_by_index = {}  # type: T.Dict[T.Sheetx, T.SheetName]
        self.sheet_by_name = {}  # type: T.Dict[T.SheetName, T.Sheetx]
        
        self.sheet_info = defaultdict(  # type: T.SheetManager
            lambda: {
                'sheet_name': '',
                'sheetx'    : -1,
                'rowx'      : -1,
            }
        )
    
    def activate(self, sheetx):
        self.current_index = sheetx
    
    def update_info(self, sheetx: T.Sheetx, info: T.SheetInfo):
        if sheetx == -1:
            return
        self.sheet_by_index[sheetx] = info['sheet_name']
        self.sheet_by_name[info['sheet_name']] = sheetx
        # noinspection PyTypeChecker
        self.sheet_info[sheetx].update(info)
    
    def add_new_sheet(self):
        new_sheetx = len(self.sheet_by_index)
        return new_sheetx
    
    @property
    def current_name(self) -> T.Optional[T.SheetName]:
        if self.current_index == -1:
            return None
        else:
            return self.sheet_by_index[self.current_index]

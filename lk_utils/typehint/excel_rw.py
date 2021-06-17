from typing import *

from xlsxwriter.format import Format as _CellFormat
from xlsxwriter.workbook import Workbook as _Workbook
from xlsxwriter.workbook import Worksheet as _Worksheet

TRowx = int
TColx = int
TCell = Tuple[TRowx, TColx]


class _TCellFormat(TypedDict):
    """
    References:
        xlsxwriter.format.Format
        https://xlsxwriter.readthedocs.io/format.html
    """
    # xlsxwriter.format.Format
    align: Literal['left', 'right', 'center']
    valign: Literal['top', 'bottom', 'vcenter']
    textwrap: bool
    num_percent: str
    # TODO: more...


TCellFormat = Union[None, Dict[str, str], _CellFormat]
#                         ^^^^^^^^^^^^^^ see `class:_TCellFormat`

TCellValue = Union[None, bool, float, int, str]
TRowValues = Iterable[TCellValue]
TColValues = Iterable[TCellValue]
THeader = List[TCellValue]

TRowsValues = List[TRowValues]
TColsValues = List[TColValues]

TWorkBook = _Workbook
TWorkSheet = _Worksheet
TSheetx = Union[int, str]
TSheetName = Optional[str]


# TSheetNames = Dict[TSheetx, TSheetName]


class _TSheetManagerValues(TypedDict):
    sheet_name: TSheetName
    sheetx: TSheetx
    rowx: TRowx
    header: THeader


TSheetManager = Dict[Union[TSheetx, TSheetName], _TSheetManagerValues]

from typing import *

from xlsxwriter.format import Format as _Format
from xlsxwriter.workbook import Workbook as _Workbook
from xlsxwriter.workbook import Worksheet as _Worksheet

TRowx = int
TColx = int
TCell = Tuple[TRowx, TColx]

TCellFormat = _Format
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

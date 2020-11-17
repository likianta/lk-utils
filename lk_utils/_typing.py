"""
@Author   : Likianta <likianta@foxmail.com>
@FileName : _typing.py
@Version  : 0.1.0
@Created  : 2020-11-17
@Updated  : 2020-11-17
@Desc     : 
"""
from typing import *


class ExcelWriterHint:
    from xlsxwriter.format import Format as _Format
    from xlsxwriter.workbook import Workbook as _Workbook
    from xlsxwriter.workbook import Worksheet as _Worksheet
    
    Rowx = int
    Colx = int
    Cell = Tuple[Rowx, Colx]
    
    CellFormat = _Format
    CellValue = Union[None, bool, float, int, str]
    RowValues = Iterable
    ColValues = Iterable
    
    RowsValues = List[RowValues]
    ColsValues = List[ColValues]
    
    WorkBook = _Workbook
    WorkSheet = _Worksheet
    SheetName = Union[str, None]


class ReadAndWriteHint:
    File = str
    FileName = str
    FilePath = str
    FileNames = List[FileName]
    FilePaths = List[FilePath]
    FileDict = Dict[FilePath, FileName]
    LoadedData = Union[str, list, dict]
    DumpableData = Union[str, list, dict]

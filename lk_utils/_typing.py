"""
@Author   : Likianta <likianta@foxmail.com>
@FileName : _typing.py
@Version  : 0.1.4
@Created  : 2020-11-17
@Updated  : 2020-12-13
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
    RowValues = Iterable[CellValue]
    ColValues = Iterable[CellValue]
    Header = List[CellValue]
    
    RowsValues = List[RowValues]
    ColsValues = List[ColValues]
    
    WorkBook = _Workbook
    WorkSheet = _Worksheet
    Sheetx = Union[int, str]
    SheetName = Union[str, None]
    SheetManager = Dict[Union[str, int], Union[List[str], dict]]
    ''' {
            'sheets': [str sheet_name, ...],
            0: {'sheet_name': str, 'sheetx': int, 'rowx': int,
                'header': Header, ...},
            ...
        }
    '''
    

class FilesniffHint:
    File = str
    FileName = str
    FilePath = str
    
    FileNames = List[FileName]
    FilePaths = List[FilePath]
    
    FileDict = Dict[FilePath, FileName]
    FileZip = Iterable[Tuple[FilePath, FileName]]
    FileDualList = Tuple[FilePaths, FileNames]
    
    FinderReturn = Union[FilePaths, FileNames, FileDict, FileZip, FileDualList]
    
    Suffix = Union[str, tuple]


class ReadAndWriteHint:
    from io import TextIOWrapper
    FileHandle = TextIOWrapper
    
    PlainFileTypes = ('.txt', '.html', '.md', '.rst', '.htm', '.ini')
    StructFileTypes = ('.json', '.json5', '.yaml')
    BinaryFileTypes = ('.xlsx', '.xls', '.pdf')
    
    PlainData = str
    StructData = Union[dict, list]
    LoadedData = Union[str, list, dict]
    DumpableData = Union[dict, list, tuple, str, set, None]

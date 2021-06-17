from io import TextIOWrapper as _TextIOWrapper
from typing import *

TFile = str
TFileMode = Literal['a', 'r', 'rb', 'w', 'wb']
TFileHandle = _TextIOWrapper

TPlainFileTypes = Literal['.txt', '.html', '.md', '.rst', '.htm', '.ini']
TStructFileTypes = Literal['.json', '.json5', '.yaml']
TBinaryFileTypes = Literal['.xlsx', '.xls', '.pdf']

TDumpableData = Union[None, dict, list, set, str, tuple]

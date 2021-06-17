from typing import *

TFile = str
TDir = str

TPath = str  # file path or dir path
TNormPath = str  # normalized path, use only '/', and rstrip '/' in tail

TPathType = Literal['file', 'dir']
TPathFormat = Literal['filepath', 'dirpath', 'path',
                      'filename', 'dirname', 'name',
                      'zip', 'dict', 'list', 'dlist']

TFileName = str
TFilePath = TNormPath

_TFileDict = Dict[TFilePath, TFileName]
_TFileZip = Iterable[Tuple[TFilePath, TFileName]]
_TFileDualList = Tuple[List[TFilePath], List[TFileName]]

TFileZip = _TFileZip

TFinderReturn = Union[
    List[TFilePath], List[TFileName],
    _TFileDict, _TFileZip, _TFileDualList
]

TSuffix = Union[str, tuple]

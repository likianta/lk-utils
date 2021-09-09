from contextlib import contextmanager
from json import dump as _jdump
from json import load as _jload
from os.path import exists
from pickle import dump as _pdump
from pickle import load as _pload

from .typehint.read_and_write import *


@contextmanager
def ropen(file: TFile, mode: TFileMode = 'r', encoding='utf-8') -> TFileHandle:
    """
    Args:
        file
        mode: ('r'|'rb')
        encoding: ('utf-8'|'utf-8-sig')
    """
    if 'b' in mode:
        handle = open(file, mode=mode)
    else:
        handle = open(file, mode=mode, encoding=encoding)
    try:
        yield handle
    finally:
        handle.close()


@contextmanager
def wopen(file: TFile, mode: TFileMode = 'w', encoding='utf-8') -> TFileHandle:
    """
    Args:
        file:
        mode: ('w'|'a'|'wb')
            w: 写入前清空原文件已有内容
            a: 增量写入
            wb: 以二进制字节流写入
        encoding ('utf-8'|'utf-8-sig'):
    """
    if 'b' in mode:
        handle = open(file, mode=mode)
    else:
        handle = open(file, mode=mode, encoding=encoding)
    try:
        yield handle
    finally:
        handle.close()


def not_empty(file: TFile) -> bool:
    """
    References:
        https://www.imooc.com/wenda/detail/350036?block_id=tuijian_yw
    
    Returns (bool):
        True: file has content
        False: file is empty
    """
    from os.path import getsize
    return bool(exists(file) and getsize(file))


def read_file(file: TFile) -> str:
    with ropen(file) as f:
        content = f.read()
        # https://blog.csdn.net/liu_xzhen/article/details/79563782
        if content.startswith(u'\ufeff'):
            # Strip BOM charset at the start of content.
            content = content.encode('utf-8')[3:].decode('utf-8')
    return content


def read_lines(file: TFile, offset=0) -> List[str]:
    """
    References:
        https://blog.csdn.net/qq_40925239/article/details/81486637
    """
    with ropen(file) as f:
        out = [line.rstrip() for line in f]
    return out[offset:]


def write_file(content: Union[iter, list, str, tuple],
               file: TFile, mode: TFileMode = 'w', adhesion='\n'):
    """ 写入文件, 传入内容可以是字符串, 也可以是数组.

    Args:
        content: 需要写入的文本, 可以是字符串, 也可以是数组. 传入数组时, 会自动
            将它转换为 "\n" 拼接的文本
        file: 写入的路径, 建议使用相对路径
        mode: 写入模式, 有三种可选:
            a: 增量写入 (默认)
            w: 清空原内容后写入
            wb: 在 w 的基础上以比特流的形式写入
        adhesion: ('\n'|'\t'|...). 拼接方式, 只有当 content 为列表时会用到, 用于
            将列表转换为文本时选择的拼接方式
            Example:
                content = adhesion.join(content)
                # ['a', 'b', 'c'] -> 'a\nb\nc'

    Refer:
        python 在最后一行追加 https://www.cnblogs.com/zle1992/p/6138125.html
        python map https://blog.csdn.net/yongh701/article/details/50283689
    """
    if not isinstance(content, str):
        content = adhesion.join(map(str, content))
    with wopen(file, mode) as f:
        f.write(content + '\n')


def read_json(file: TFile) -> Union[dict, list]:
    with ropen(file) as f:
        return _jload(f)


def write_json(data: TDumpableData, file: TFile, pretty_dump=False):
    if isinstance(data, set):
        data = list(data)
    
    with wopen(file) as f:
        _jdump(data, f, ensure_ascii=False, default=str,
               indent=None if pretty_dump is False else 4)
        #   ensure_ascii=False
        #       https://www.cnblogs.com/zdz8207/p/python_learn_note_26.html
        #   default=str
        #       When something is not serializble, callback `__str__`.
        #       It is useful to resolve `pathlib.PosixPath`


# ------------------------------------------------------------------------------

def loads(file: TFile, **kwargs) -> Union[dict, list, str]:
    """
    Args:
        file:
        **kwargs:
            offset: Optional[int]
    """
    if file.endswith(('.txt',)):
        if (offset := kwargs.get('offset', None)) is None:
            return read_file(file)
        else:
            return read_lines(file, offset)
    
    if file.endswith(('.htm', '.html', '.md', '.rst', '.txt')):
        return read_file(file)
    
    if file.endswith(('.json', '.json5')):
        return read_json(file)
    
    if file.endswith(('.yaml', '.yml')):  # pip install pyyaml
        # noinspection PyUnresolvedReferences
        from yaml import safe_load as _yload
        with ropen(file) as f:
            return _yload(f)
    
    if file.endswith(('.pkl',)):
        with ropen(file, 'rb') as f:
            return _pload(f)
    
    # unregistered file types, like: .js, .css, .py, etc.
    return read_file(file)


def load_list(file: TFile, offset=0) -> List[str]:
    return read_lines(file, offset)


def load_dict(file: TFile) -> Union[dict, list]:
    return read_json(file)


def dumps(data: TDumpableData, file: TFile, **kwargs):
    """
    Args:
        data
        file
        **kwargs:
            mode: TMode, default 'w'
            adhesion: str, default '\n'
            pretty_dump: bool, default False
            
    """
    if file.endswith(('.htm', '.html', '.md', '.rst', '.txt')):
        return write_file(data, file, **kwargs)
    
    if file.endswith(('.json', '.json5')):
        return write_json(data, file, **kwargs)
    
    if file.endswith(('.yaml', '.yml')):  # pip install pyyaml
        # noinspection PyUnresolvedReferences
        from yaml import dump as _ydump
        with wopen(file) as f:
            return _ydump(data, f, **kwargs)
    
    if file.endswith(('.pkl',)):
        with wopen(file, 'wb') as f:
            return _pdump(data, f, **kwargs)
    
    # unregistered file types, like: .js, .css, .py, etc.
    return write_file(data, file, **kwargs)


# ------------------------------------------------------------------------------

@contextmanager
def read(file: TFile, **kwargs) -> Union[dict, list, str]:
    """ Open file as a read handle.
    
    Usage:
        with read('input.json') as r:
            print(len(r))
    """
    data = loads(file, **kwargs)
    try:
        yield data
    finally:
        del data


@contextmanager
def write(file: TFile, data: Union[dict, list, set] = None, **kwargs):
    """ Create a write handle, file will be generated after the `with` block
        closed.
        
    Args:
        file: See `dumps`.
        data (list|dict|set|str): If the data type is incorrect, an Assertion
            Error will be raised.
        kwargs: See `dumps`.
        
    Usage:
        with write('output.json', []) as w:
            for i in range(10):
                w.append(i)
        print('See "result.json:1"')
    """
    assert isinstance(data, (list, dict, set))
    try:
        yield data
    finally:
        dumps(data, file, **kwargs)

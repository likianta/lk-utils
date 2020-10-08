"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : read_and_write.py
@Created : 2018-08-00
@Updated : 2020-09-06
@Version : 1.7.2
@Desc    :
"""
from json import dumps as jdumps, loads as jloads
from os.path import exists, getsize


def get_num_of_lines(filepath: str) -> int:
    """ 该方法可以高效地读取文件一共有多少行, 支持大文件的读取.
    python 统计文件行数 - CSDN博客 https://blog.csdn.net/qq_29422251/article
        /details/77713741
    """
    # noinspection PyUnusedLocal
    return len(["" for line in open(filepath, mode='r')])


def is_file_empty(filepath: str) -> bool:
    """
    https://www.imooc.com/wenda/detail/350036?block_id=tuijian_yw
    :return: bool.
        True: file has content.
        False: file is empty.
    """
    return bool(exists(filepath) and getsize(filepath))


def read_file(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        contents = f.read()
        # https://blog.csdn.net/liu_xzhen/article/details/79563782
        if contents.startswith(u'\ufeff'):
            # 说明文件开头包含有 BOM 信息, 我们将它移除.
            # Strip BOM charset at the start of contents.
            contents = contents.encode('utf8')[3:].decode('utf8')
    return contents


def read_file_by_line(path: str, offset=0) -> list:
    """
    IN: path: str. e.g. 'test.txt'
        offset: int.
            0: 表示返回完整的列表
            n: 传一个大于 0 的数字, 表示返回 list[n:]. (ps: 如果该数字大于列表的
               长度, python 会返回一个空列表, 不会报错)
    OT: list<str>. e.g. ['aaa', 'bbb', 'ccc', ...]
    """
    # https://blog.csdn.net/qq_40925239/article/details/81486637?utm_source
    # =blogxgwz7
    with open(path, 'r', encoding='utf-8-sig') as file:
        out = [line.strip('\n') for line in file]
    return out[offset:]


def write_file(contents: iter, filepath: str, mode='w', adhesion='\n'):
    """ 写入文件, 传入内容 (参数1) 可以是字符串, 也可以是数组.

    ARGS:
        contents: 需要写入的文本, 可以是字符串, 也可以是数组. 传入数组时, 会自动
            将它转换为 "\n" 拼接的文本
        filepath: 写入的路径, 建议使用相对路径
        mode: 写入模式, 有三种可选:
            [a] 增量写入 (默认是 [a])
            [w] 清空原内容后写入
            [wb] 在 [w] 的基础上以比特流的形式写入
        adhesion: 拼接方式, 只有当 content 为列表时会用到, 用于将列表转换为文本
            时选择的拼接方式, 默认是以 "\n" 拼接
            E.g.
                content = adhesion.join(content)
                # ['a', 'b', 'c'] --> 'a\nb\nc'

    参考:
        python 在最后一行追加 - 张乐乐章 - 博客园 https://www.cnblogs.com
            /zle1992/p/6138125.html
        python map https://blog.csdn.net/yongh701/article/details/50283689
    """
    if not isinstance(contents, str):
        contents = adhesion.join(map(str, contents))
        ''' 注: 暂不支持对二维数组操作.
            如果 contents 的形式为:
                contents = [[1, 2, 3], [4, 5, 6]]
            请使用 write_multi_list(contents)
        '''
    with open(filepath, encoding='utf-8', mode=mode) as f:
        f.write(contents + '\n')


def read_json(path: str) -> dict:
    # 注意: 如果文件内容不符合 json 格式, jloads() 会报 JSONDecodeError.
    jsondata = jloads(read_file(path))
    return jsondata


def write_json(data: [dict, list, tuple], path: str):
    """
    REF: json.dumps 如何输出中文: https://www.cnblogs.com/zdz8207/p/python_learn
        _note_26.html
    """
    assert '.json' in path and isinstance(data, (dict, list, tuple))
    with open(path, encoding='utf-8', mode='w') as f:
        f.write(jdumps(data, ensure_ascii=False))


def write_multi_list(path: str, *mlist):
    """
    REF: 数组 (矩阵) 转置: https://blog.csdn.net/yongh701/article/details
        /50283689
    """
    transposited_list = zip(*mlist)
    # [[1, 2, 3], [4, 5, 6], [7, 8, 9]] -> ((1, 4, 7), (2, 5, 8), (3, 6, 9))
    contents = ['\t'.join(map(str, x)) for x in transposited_list]
    # -> [('1', '4', '7'), ('2', '5', '8'), ('3', '6', '9')]
    # -> ['1\t4\t7', '2\t5\t8', '3\t6\t9']
    write_file(contents, path)


# ------------------------------------------------------------------------------

def loads(path: str, offset=0) -> [str, list, dict]:
    """
    ARGS:
        path
        offset: 默认为 0, 表示调用 read_file_by_line(path, offset=0)
            -1: 当为负数时, 表示调用 read_file()
            0, 1, 2, 3, ...: 表示调用 read_file_by_line(), offset 作为
                read_file_by_line() 的相应参数传入
    """
    if path.endswith('.json'):
        return read_json(path)
    elif path.endswith(('.html', '.htm')):
        return read_file(path)
    elif path.endswith('.txt'):
        if offset >= 0:
            return read_file_by_line(path, offset)
        else:
            return read_file(path)
    # elif path.endswith('.xlsx'):
    #     from .excel_reader import ExcelReader
    #     return ExcelReader(path)
    else:
        raise ValueError('Unknown filetype!', path)


def dumps(data: [dict, list, tuple], path: str):
    if path.endswith('.json'):
        write_json(data, path)
    elif path.endswith(('.txt', '.html', '.htm')):
        write_file(data, path)
    # elif path.endswith(('.xlsx', '.xls')):
    #     from .excel_writer import ExcelWriter
    #     w = ExcelWriter(path)
    #     for row in data:
    #         w.writeln(*row)
    #     w.save()
    else:
        raise ValueError('Unknown filetype!', path)


read = loads
write = dumps

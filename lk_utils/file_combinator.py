"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : file_combinator.py
@Created : 2019-00-00
@Updated : 2020-09-06
@Version : 2.3.1
@Desc    :
    使用方法:
        合并指定目录下的所有 txt 文件, 并在同目录下生成 "result.txt" 文件:
            file_combinator.combine_txt(my_dir)
        合并指定目录下的所有 excel 文件, 并在同目录下生成 "result.xlsx" 文件:
            file_combinator.combine_excel(my_dir)
        合并指定目录下的所有 csv 文件, 并在同目录下生成 "result.xlsx" 文件:
            file_combinator.combine_csv(my_dir)
    注意事项:
        如果要生成的 result 文件已存在, 则会被覆盖.
"""
import os

from lk_logger import lk

from . import filesniff, read_and_write
from .excel_reader import ExcelReader
from .excel_writer import ExcelWriter


def combine_txt(idir: str, trim_header=True):
    sum_file = idir + 'result.txt'
    
    if os.path.exists(sum_file):
        cmd = input('[INFO][file_combinator] The sum file ({}) already exists, '
                    'do you want to overwrite it? (y/n) '.format(sum_file))
        if cmd == 'y':
            pass
        else:
            raise AttributeError('Please delete the sum file and retry')
    
    files = os.listdir(idir)
    
    writer = read_and_write.FileSword(
        sum_file, 'a', clear_any_existed_content=True)
    
    for f in files:
        if '.txt' in f and f != 'result.txt':
            f = idir + f
            content = read_and_write.read_file(f).strip()
            writer.write(content)
    
    writer.close()
    
    if trim_header:
        from re import compile
        content = read_and_write.read_file(sum_file)
        header = compile(r'^[^\n]+').search(content).group()
        content = content.replace(header + '\n', '')
        content = header + '\n' + content
        read_and_write.write_file(content, sum_file)


def combine_csv(idir='', ofile='result.xls', module=True, ignore=None):
    import csv
    
    if not idir:
        idir = filesniff.get_curr_dir()
    else:
        idir = filesniff.prettify_dir(idir)
    
    writer = ExcelWriter(idir + ofile)
    header = False
    
    files = filesniff.find_filenames(idir, '.csv')
    for f in files:
        if f == ofile or (ignore and f in ignore):
            continue
        
        lk.logax(f, h='parent')
        
        with open(idir + f, newline='', encoding='utf-8') as csvfile:
            spamreader = csv.reader(csvfile)
            
            for index, row in enumerate(spamreader):
                if index == 0:
                    if header:
                        continue
                    else:
                        header = True
                if module:
                    if index == 0:
                        row = ['module'] + row
                    else:
                        row = [f.split('.')[0]] + row
                writer.writeln(*row)
    
    writer.save()


def combine_excel(ifiles, ofile='', module=True, one_sheet=True):
    """ 合并指定表格文件为一个.
    
    :param ifiles: 来源文件, 可以是多个, 以列表或 iterable 形式传入
    :param ofile: 目标输出文件的路径. 为空则表示在 idir 目录下生成一个 merged.
        xlsx 文件. ofile 的后缀名只能是 '.xlsx' (当为 '.xls' 时, 会被强制转换)
    :param module: 是否在合并结果中添加一个 "module" 列, 以显示分文件的来源 (文
        件名)
    :param one_sheet:
        True: 将分文件的数据合并到输出文件的一个 sheet 中. 建议当分文件的字段格
            式相同时使用.
        False: 将分文件的数据按照其文件名创建到输出文件的不同 sheet 中. 建议:
            (1) 当分文件的字段不同时使用;
            (2) 当分文件是不同的年份的数据, 我们想要按照年份来分放到输出文件的不
                同 sheet 时使用.
            PS: 此时建议 module 参数传 False.
    """
    if not ofile:
        ofile = filesniff.prettify_file(
            os.path.join(os.path.dirname(ifiles[0]), 'merged.xlsx')
        )
    assert ofile not in ifiles
    
    writer = ExcelWriter(ofile, sheetname='sheet 1' if one_sheet else None)
    header = None
    
    for fileno, exl in lk.enum(ifiles, 1):
        filename = filesniff.get_filename(exl, False)
        lk.logax(fileno, filename, h='parent')
        
        reader = ExcelReader(exl)
        if one_sheet is False:
            writer.add_new_sheet(f'{fileno}-{filename[:29]}')
            """
            注意: 这里用 filename 作 sheet name 有隐患, 当名称过长 (超过 31 个字
                符) 或重名时会报错, 因此我们加一个 modulex 前缀避免重名, 再裁剪
                至最多 31 个字符.
            """
        
        if header is None or one_sheet is False:
            header = reader.get_header()
            if module:
                writer.writeln('module', *header)
            else:
                writer.writeln(*header)
        
        for row in reader.walk_rows(1):
            if module:
                writer.writeln(filename, *row)
            else:
                writer.writeln(*row)
    
    writer.save()

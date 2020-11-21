"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : data_convert.py
@Created : 2018-00-00
@Updated : 2020-11-22
@Version : 3.0.2
@Desc    : Convert source file type to target file type.
"""
import re

from bs4 import BeautifulSoup
from bs4.element import Tag
from lk_logger import lk

from lk_utils import easy_launcher
from lk_utils.excel_reader import ExcelReader
from lk_utils.excel_writer import ExcelWriter
from lk_utils.read_and_write import read_file, write_file


def json_2_excel(ifile='../temp/in.json', ofile='../temp/out.xlsx',
                 header=None, auto_index=False, purify_values=False):
    """
    SPEC:
        支持的数据格式:
            Rows = List[Union[List/Str/Int/Float]]
            Dict[str, Union[Str, Int, Float]]
        不支持的:
            List[Dict]
            Dict[str, Rows] (未来将尽快支持)
            Dict[str, Dict]
    """
    from ..excel_writer import ExcelWriter
    from ..read_and_write import read_json
    
    rdata = read_json(ifile)
    with ExcelWriter(ofile) as writer:
        if header:
            writer.writeln(*header)
        
        if isinstance(rdata, list):
            for row in rdata:
                writer.writeln(
                    *row, auto_index=auto_index, purify_values=purify_values
                )
        else:  # type: dict
            for k, v in rdata.items():
                writer.writeln(
                    k, v, auto_index=auto_index, purify_values=purify_values
                )


# ------------------------------------------------------------------------------

def excel_2_json(ifile='../temp/in.xlsx', ofile='../temp/out.json',
                 key='index'):
    """ 将 excel 转换为 json.
    
    :param ifile
    :param ofile
    :param key: 主键依据. 默认是行号, 因为行号是不重复的, 适合作为字典的键. 您也
        可以定义表格中的某个字段为主键. 另外, 如果 key 设为空字符串, 则以列表形
        式输出每一行.
    """
    from ..excel_reader import ExcelReader
    from ..read_and_write import write_json
    
    reader = ExcelReader(ifile)
    writer = {}
    
    if key == 'index':
        if key not in reader.get_header():
            mode = 0
        else:
            mode = 1
    elif key == '':
        # 如果 key 为空字符串, 则以列表形式输出每一行.
        writer = tuple(reader.row_values(rowx) for rowx in reader.get_range(1))
        write_json(writer, ofile)
        return
    else:
        mode = 2
    
    for rowx in reader.get_range(1):
        row = reader.row_dict(rowx)
        
        if mode == 0:
            writer[rowx] = row
        elif mode == 1:
            writer[row['index']] = row
        elif mode == 2:
            # noinspection PyBroadException
            try:
                writer[row[key]] = row
            except Exception:
                lk.logt('[data_converter][W0536]',
                        'Cannot convert this row because of KeyError',
                        row, key, h='parent')
    
    write_json(writer, ofile)


def excel_2_json_kv(ifile='../temp/in.xlsx', ofile='../temp/out.json',
                    header=False):
    """ 将 excel 转换为 json 文件.
    要求 excel 只有两列数据 (占据第一, 第二列位置), 且目标数据位于 sheet 1. 最后
    转换的结果是以第一列为 keys, 第二列为 values.
    """
    from ..excel_reader import ExcelReader
    from ..read_and_write import write_json
    
    reader = ExcelReader(ifile)
    
    offset = 0 if header else 1
    
    writer = {k: v for k, v in zip(
        reader.col_values(0, offset),
        reader.col_values(1, offset)
    )}
    
    write_json(writer, ofile)


# ------------------------------------------------------------------------------

# noinspection PyUnresolvedReferences
def pdf_2_txt(ifile: str, ofile: str, page_start=0, page_end=0, dump_images=''):
    """ Extract plain text from pdf file.
    REF: https://github.com/pdfminer/pdfminer.six/blob/master/tools/pdf2txt.py
    
    :param ifile: 要传入的 pdf 文件路径, 以 '.pdf' 结尾.
    :param ofile: 要输出的文本文件路径. 以 '.txt' 结尾.
    :param page_start: 开始页. 从 0 开始数.
    :param page_end: 结束页. 从 0 开始数. 当为 0 时, 表示导出到最后一页.
    :param dump_images: 是否导出 pdf 中的图片. 传入一个目录. 空字符串表示不导出.
    """
    from pdfminer import layout
    from pdfminer.converter import TextConverter
    from pdfminer.image import ImageWriter
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser
    
    laparams = layout.LAParams()
    image_writer = ImageWriter(dump_images) if dump_images else None
    # NOTE: 我对 pdfminer.image 的源码 ($VENV$\Lib\site-packages\pdfminer\image.
    #   py) 进行了修改, 增加了 self.picno 变量以避免导出时的图片名重复, 详见源码
    #   中的 "LKDO" 标记.
    
    reader = open(ifile, 'rb')
    writer = open(ofile, 'w', encoding='utf-8')
    
    manager = PDFResourceManager(caching=False)
    device = TextConverter(manager, writer, codec='utf-8', laparams=laparams,
                           imagewriter=image_writer)
    interpreter = PDFPageInterpreter(manager, device)
    parser = PDFParser(reader)
    doc = PDFDocument(parser, caching=False)
    
    if not doc.is_extractable:
        lk.logt('[data_converter][E0906]', 'extraction forbidden', ifile,
                h='parent')
        raise Exception
    
    for pageno, page in enumerate(PDFPage.create_pages(doc)):
        if pageno < page_start:
            continue
        if page_end and pageno > page_end:
            break
        lk.loga(pageno, h='parent')
        interpreter.process_page(page)
    
    if dump_images:
        lk.loga(f'there are {image_writer.picno} images dumped', h='parent')
    
    device.close()
    reader.close()
    writer.close()


# noinspection PyUnresolvedReferences
def pdf_2_excel(ifile: str, ofile: str, page_start=0, page_end=0,
                indicator=True):
    """
    REF: https://www.jianshu.com/p/f33233e4c712
    
    :param ifile: postfixed with '.pdf'
    :param ofile: postfixed with '.xlsx'
    :param page_start: count from 0
    :param page_end: 0 means 'auto detect all pages'
    :param indicator: True means adding pageno, tableno and lineno fields
    """
    import pdfplumber
    from .excel_writer import ExcelWriter
    
    reader = pdfplumber.open(ifile)
    writer = ExcelWriter(ofile or ifile.replace('.pdf', '.xlsx'))
    
    if indicator:
        writer.writeln('pageno', 'tableno', 'lineno')
    
    if page_end == 0:
        pages = reader.pages[page_start:]
    else:
        pages = reader.pages[page_start:page_end]
    
    pageno = tableno = lineno = 0
    
    for p in pages:
        pageno += 1
        lk.logd(f'pageno = {pageno}, lineno = {lineno}', h='parent')
        for table in p.extract_tables():
            tableno += 1
            for row in table:
                lineno += 1
                if indicator:
                    writer.writeln(pageno, tableno, lineno, *row)
                else:
                    writer.writeln(*row)
    
    reader.close()
    writer.save()


# ------------------------------------------------------------------------------

def excel_2_html(ifile, ofile, title='', dialog=False):
    """
    IN: ifile. e.g. 'in.xlsx'
    OT: ofile. e.g. 'out.html'
    
    黑魔法:
        假设待处理的表格中有一列是 url (假设 title 为 'homepage'). 您想要让 url
        变成可点击的蓝色链接, 并且尽可能简洁地显示, 请这样做:
            header before:
                index  name       homepage
                1      Li, Ming   http://abc.com/li-ming
                2      Lin, Fang  http://abc.com/lin-fang
            header after: (注意 homepage 标题头的变化)
                index  name       homepage|visit me
                1      Li, Ming   http://abc.com/li-ming
                2      Lin, Fang  http://abc.com/lin-fang
                
        前者的生成效果如下:
            <tr>
                <td>1</td>
                <td>Li, Ming</td>
                <td>http://abc.com/li-ming</td>
            <tr>
        后者的生成效果如下:
            <tr>
                <td>1</td>
                <td>Li, Ming</td>
                <td><a href="http://abc.com/li-ming" target="view_window">visit
                me</a></td>
            <tr>
            
        黑魔法使用注意事项:
            1. 链接必须以 'http' 或 'https' 开头
            2. 单个单元格必须有且只有一个链接 (如果有多个, 则不作处理)
            3. 链接所属的标题头必须含 "|" 符号, 您可以使用 "homepage|", 本脚本会
               使用一个默认值: "visit"
    """
    
    reader = ExcelReader(ifile)
    
    if dialog:
        def select_sheet():
            preview = ['\tindex\t|\tsheet name']
            
            for index, sheet_name in enumerate(reader.get_name_of_sheets()):
                preview.append(f'\t{index}\t|\t{sheet_name}')
            
            print('\n'.join(preview))
            cmd = input('请选择您要处理的 sheet 序号 (从零开始数): ')
            
            # noinspection PyBroadException
            try:
                cmd = int(cmd)
                reader.activate_sheet(cmd)
            except Exception:
                easy_launcher.main('无法处理您的命令')
        
        select_sheet()
    else:
        pass
    
    # html head
    if title == '':
        title = 'html table converter result'
    
    head = f"""
<head>
    <title>{title}</title>
    <link rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap
◆.min.css"
          integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz
◆/K68vbdEjh4u"
          crossorigin="anonymous">
</head>
<body>
    <div id="excel-2-html-result" class="container">
        <table class="table table-striped table-hover table-bordered">
    """.replace('\n◆', '')
    tail = """
        </table>
    </div>
</body>
    """
    
    html = [head]
    """
    html 打算按照这个结构来设计:
        <table>
            <tbody>
                <tr>  # 第一个 tr 是 header
                    <th>...<th>
                    <th>...<th>
                    <th>...<th>
                </tr>
                <tr>
                    <td>...</td>
                    <td>...</td>
                    <td>...</td>
                </tr>
                <tr>
                    <td>...</td>
                    <td>...</td>
                    <td>...</td>
                </tr>
                ...
            </tbody>
        </table>
    """
    
    class DetectLink:
        
        def __init__(self, _header):
            self.link_title = {}
            self.clean_header = []
            
            for index, cell in enumerate(_header):
                if '|' in cell:
                    a, b = cell.split('|', 1)
                    # 'homepage|visit me' -> ['homepage', 'visit me']
                    self.clean_header.append(a)
                    self.link_title[index] = b if b else 'visit'
                    """
                    -> self.link_title = {
                        3: 'visit me',
                        4: 'visit',
                    }
                    """
                else:
                    self.clean_header.append(cell)
            # lk.logt('[TEMPRINT]', self.link_title)
            
            self.reg = re.compile(r'https?://')
        
        def get_clean_header(self):
            return self.clean_header
        
        def detect_link(self, index, cell):
            if not self.link_title:
                return cell
            
            if not isinstance(cell, str):
                return cell
            
            if index not in self.link_title:
                return cell
            
            found = self.reg.findall(cell)  # 检测是否包含链接特征
            # lk.logt('[TEMPRINT]', cell, found)
            
            if len(found) != 1:
                # 暂不支持处理 len == 0 或 len > 1 的情况.
                return cell
            else:
                return '<a href="{}" target="view_window">{}</a>'.format(
                    cell, self.link_title[index]
                )
    
    detecter = None
    
    for rowx in range(reader.get_num_of_rows()):
        row = reader.row_values(rowx)
        
        if rowx == 0:
            detecter = DetectLink(row)
            header = detecter.get_clean_header()
            cells = (f'<th>{x}</th>' for x in header)
        else:
            cells = (f'<td>{detecter.detect_link(i, x)}</td>'
                     for i, x in enumerate(row))
        
        row = '<tr>{}</tr>'.format('\n'.join(cells))
        html.append(row)
    
    html.append(tail)
    
    # TODO: 整理一下 html, 使美观.
    
    write_file(html, ofile)


def html_2_excel(ifile, ofile, single_sheet=True):
    """
    NOTE: 若转换结果为空, 请从以下方面排查:
        1. 源网页的标签名大小写是否规范 (本函数只支持正确的大小写)
        2. 源网页的表格是否是 <p> 组成的 (如果是则本函数不支持)
        3. 如果源网页格式错乱, 可以尝试先用 chrome 打开, 再从开发者工具中复制网
           页 html (该 html 是经过 chrome 优化过的, 可以解决很多不规范问题)
    IN: ifile. e.g. 'in.html'
    OT: ofile. e.g. 'out.xlsx'
    """
    try:
        soup = BeautifulSoup(read_file(ifile), 'html.parser')
    except UnicodeDecodeError:
        easy_launcher.main(
            'UnicodeDecodeError. please make sure the target file should be '
            'encoded with "utf-8"', 5
        )
        return
    
    # 找到 html 中的所有 <table>.
    # tables = [i for i in soup.find_all('table') if not i.is_empty_element]
    tables = [i for i in _find_direct_parent_nodes('table', soup, [])
              if not i.is_empty_element]
    # lk.logt('[TEMPRINT]', len(tables), len(soup.find_all('table')))
    """
    解释: `i.is_empty_element` 表示 table 的内容是非空的
    """
    if not tables:
        easy_launcher.main('未能在目标文件中发现表格, 请检查输入文件是否有误')
        return
    
    # ------------------------------------------------
    
    if single_sheet:
        writer = ExcelWriter(ofile)
        # writer.writeln('tablex', 'rowx')
    else:
        writer = ExcelWriter(ofile, sheetname=None)
    
    for tablex, table in enumerate(tables, 1):
        rowsplug = {}  # {rowx: [pos]}
        merge = []
        
        if not single_sheet:
            writer.add_new_sheet(f'sheet {tablex}')
        
        for rowx, row in enumerate(table.find_all('tr')):
            # lk.logt('[TEMPRINT]', tablex, rowx, row)
            row_values = _get_row_values(rowsplug, merge, rowx, row)
            # lk.loga(rowx, row_values, h='parent')
            writer.writeln(*row_values)
        
        for i in merge:
            writer.merging_visual(i)
    
    writer.save()


def _find_direct_parent_nodes(target, etree, holder):
    """
    假设有:
        <a>
            <b>      # e1
                <b>  # e2
        <b>          # e3
            <b>      # e4
    我们只想要 e1 和 e3, 不要内部的同名子标签, 该怎么做?
    效果:
        soup.find_all('b", recursive=True) -> [e1, e2, e3, e4]
        soup.find_all('b", recursive=False) -> [e3]
        使用本方法 -> [e1, e3]
    
    FEATURE: 本方法支持忽略大小写. 例如 target = 'table', 则 <TABLE> 标签也可以
        被查找到.
    ARGS:
        target (str): 目前仅支持 str 类型的 tag name, 例如 'table'
        etree: 初始化请传入 soup 或 master_element
        holder (list): 初始化请传入空的列表
    """
    for e in etree.children:
        if isinstance(e, Tag):
            if e.name.lower() == target:
                holder.append(e)
            else:
                _find_direct_parent_nodes(target, e, holder)
    return holder


def _get_row_values(rowsplug, merge, rowx, row):
    """
    GLOBALS:
        merge: [(x1, y1, x2, y2, data), ...]
        rowsplug: dict. {rowx: [pos]}
    """
    
    es = row.find_all('td') or row.find_all('th')
    row_values = []
    
    for pos in rowsplug.get(rowx, []):
        es.insert(pos, None)
    
    for colx, e in enumerate(es):
        if e is None:
            row_values.append(None)
            continue
        
        span1 = int(e.get('colspan', 1))
        span2 = int(e.get('rowspan', 1))
        col_offset = len(row_values)
        
        # 获取 cell 的值
        # 注意, 通常来说, cell.text 就能拿到值; 此外还有一种情况, cell 的值是存
        # 储在 'value' 属性里的, 比如 <td><input value="ABC"/></td>, 这时就要通
        # 过 cell['input']['value'] 来取值了
        if x := e.input:
            value = _clean(x.get('value', ''))
        else:
            value = _clean(e.text)
        
        # update merge range
        if span1 > 1 or span2 > 1:
            row_values.extend([None] * span1)
            merge.append(
                (rowx, col_offset,
                 rowx + span2 - 1, len(row_values) - 1,
                 value)
            )
            lk.loga('merge cell', merge[-1], h='grand_parent')
        else:
            row_values.append(value)
        
        # update rowsplug
        if span2 > 1:
            for i in range(col_offset, len(row_values)):  # colx
                for j in range(rowx, rowx + span2):  # rowx
                    node = rowsplug.setdefault(j, [])
                    node.append(i)
    
    return row_values


def _clean(v):
    """
    处理:
        1. 删除换行符
        2. 特殊字符变为空格
        3. 去除前后空字符串
        4. 对中文之间的空格删除, 例如 "张 三" 变成 "张三", 且保护英文的
           "zhang san" 不会变成 "zhangsan"
    """
    reg1 = re.compile(r'\n')  # '\n' -> ''
    reg2 = re.compile(r'\s+')  # '  ' -> ' '
    reg3 = re.compile(r'(?<=[\u4e00-\u9fa5]) +(?=[\u4e00-\u9fa5])')
    # '张 三' -> '张三'
    v = re.sub(reg1, '', v)
    v = re.sub(reg2, ' ', v)
    v = re.sub(reg3, '', v)
    return v.strip()

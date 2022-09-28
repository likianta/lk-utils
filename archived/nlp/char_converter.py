"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : char_converter.py
@Created : 2018-00-00
@Updated : 2020-09-06
@Version : 2.1.5
@Desc    :
"""
import re


class DiacriticalMarksCleaner:
    """ 变音符号清理.
    注意事项:
        本模块对 "ü" 将转换为 "u". 如果您在进行中国人名的转换, 请预先将待处理的
        文本中的 "ü" 自处理为 "v".
    """
    _reg1: re.Pattern
    _reg2: re.Pattern
    _reg3: re.Pattern
    _strict_mode = False
    # 变音符号转换字典
    # 注: 这里的变音符号, 仅收集 strip_accents() 无法处理的部分. 例如 ø -> o,
    #   在 strip_accents() 中是做不到的, 所以把这类情况记为一张字典.
    cedilla_dict: dict
    symbols_dict: dict
    
    def __init__(self, custom_dict=None):
        self._reg1 = re.compile(r'\s')
        self._reg2 = re.compile(r' +')
        self._reg3 = re.compile(r"[^-~()\[\]@'\",.:;?! "
                                r"a-zA-Z0-9"
                                r"\u4e00-\u9fa5"
                                r"\u0800-\u4e00"
                                r"\uAC00-\uD7A3]")
        self.cedilla_dict = {
            'ҫ': 'c',
            'đ': 'd',
            'Đ': 'D',
            'ƒ': 'f',
            '¡': 'i',
            'ı': 'i',
            'ł': 'l',
            'Ł': 'L',
            'ø': 'o',
            'Ø': 'O',
            'æ': 'ae',
            'œ': 'oe',
            'Æ': 'AE',
            'Œ': 'CE',
            'ß': 'ss',
        }
        self.symbols_dict = {
            '‘': "'", '’': "'", "ʼ": "'",
            '¨': ' ', "ˇ": " ", "´": " ",
            "°": "°",
            '÷': '/',
            '†': '',
            '¼': '1/4', '³': '3'
        }
        if custom_dict:  # type: dict
            self.symbols_dict.update(custom_dict)
    
    @staticmethod
    def strip_accents(text: str) -> str:
        """ 去除变音符号.
        
        IO: Ramírez Sánchez -> Ramirez Sanchez
        
        NOTE: This works fine for spanish, but not always works for other
            languages (e.g. ø -> ø). So I prepare another dict to handle the
            latter ones (see `self.cedilla_dict`).
        
        REF: https://stackoverflow.com/questions/4512590/latin-to-english
            -alphabet-hashing
        """
        import unicodedata
        # if 'ü' in text:  # for Chinese
        #     text = text.replace('ü', 'v')
        return ''.join(
            char for char in unicodedata.normalize('NFKD', text)
            if unicodedata.category(char) != 'Mn'
        )
    
    def main(self, word: str, trim_symbols=True) -> str:
        return '' if word.strip() == '' else self._trans(word, trim_symbols)
    
    def _trans(self, word: str, trim_symbols=True) -> str:
        word = re.sub(self._reg1, ' ', word)
        
        for k, v in self.cedilla_dict.items():
            word = word.replace(k, v)
        
        word = self.strip_accents(word)
        
        if trim_symbols:
            for k, v in self.symbols_dict.items():
                word = word.replace(k, v)
        
        if self._strict_mode:
            if x := self._reg3.findall(word):
                # uniq: unique; unreg: unregisted
                print(':v3p', 'found uniq and unreg symbol', word, x)
                word = re.sub(self._reg3, '', word)
        
        word = re.sub(self._reg2, ' ', word)
        return word.strip()


class PunctuationConverter:
    symbols_ch2en_dict: dict
    
    def __init__(self):
        self.symbols_ch2en_dict = {
            '，' : ', ', '。': '. ', '、': ', ',
            '“' : '"', '”': '"', '‘': '\'', '’': '\'',
            '：' : ': ', '；': '; ',
            '·' : ' ', '~': '~',
            '？' : '? ', '！': '! ',
            '（' : ' (', '）': ') ',
            '【' : '[', '】': ']',
            '《' : '"', '》': '"',
            '……': '...', '——': ' - ',
        }
        # | self.symbols_ch2en_dict = {
        # |     'en': r',.:;!?"\'`^+-*/\%<=>@#$&_()[]{}|~',
        # |     'cn_all': '，。、：；！？·“”‘’（）【】《》—…',
        # |     'cn': '，。、：；！？·',
        # |     'cn_pair': ('“”', '‘’', '（）', '【】', '《》'),
        # |     'cn_double': ('——', '……')
        # | }
    
    def main(self, q: str) -> str:
        return '' if q.strip() == '' else self._trans(q.strip())
    
    def _trans(self, q: str) -> str:
        for k, v in self.symbols_ch2en_dict.items():
            q = q.replace(k, v)
        q = re.sub(' +', ' ', q.strip())
        return q


def discover(ifile: str, ofile: str):
    from ..read_and_write import loads, dumps
    
    cleaner = DiacriticalMarksCleaner()
    cleaner._strict_mode = False
    # noinspection PyProtectedMember
    regex = cleaner._reg3
    
    ilist1 = loads(ifile)
    ilist2 = []
    for i in ilist1:
        for j in regex.findall(i):
            if j not in ilist2:
                ilist2.append(j)
    
    odict = {}
    for i in ilist2:
        odict[i] = cleaner.main(i)
    dumps(odict, ofile)


if __name__ == '__main__':
    discover('in.txt', 'out.json')

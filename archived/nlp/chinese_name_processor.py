import re
from typing import List
from typing import Union

from .tree_and_trie import Trie
from ..read_and_write import read_json
from ..read_and_write import read_lines


class Lexicon:
    
    def __init__(self):
        from os.path import split as osplit
        
        self_file = __file__.replace('\\', '/')
        resrc_dir = osplit(self_file)[0] + '/resource'  # resource dir
        self.resrc_dir = resrc_dir
        
        """
        metadata:
            拼音表 => 拼音表_标准集
            拼音表 + 非标准拼音表 => 拼音表_扩展集
            韦氏拼音表 => 韦氏拼音表_标准集
            韦氏拼音表 + 非标准韦氏拼音表 => 韦氏拼音表_扩展集
        其中, 等式左侧的 "拼音表", "非标准拼音表", "韦氏拼音表", "非标准韦氏拼音
            表" 是由人工维护和定期更新的, 等式右侧的 "拼音表_标准集", "拼音表_扩
            展集", "韦氏拼音表_标准集", "韦氏拼音表_扩展集" 包括后面会涉及到的前
            缀树, 后缀树等衍生品, 都是由脚本根据 metadata 组合生成的 (脚本见
            metadata/lexicon_generator.py).
        
        下面的 self.resrc 就是脚本生成的资源文件路径字典.
        """
        # 该字典是一个三级结构. 领域 > 数据集 > 文件类型.
        self.resrc = {
            'pinyin'      : {
                'standard': {
                    'plain'  : f'{resrc_dir}/拼音表_标准集.txt',
                    'trie'   : f'{resrc_dir}/拼音表_标准集_前缀树.json',
                    'postrie': f'{resrc_dir}/拼音表_标准集_后缀树.json',
                },
                'extend'  : {
                    'plain'  : f'{resrc_dir}/拼音表_扩展集.txt',
                    'trie'   : f'{resrc_dir}/拼音表_扩展集_前缀树.json',
                    'postrie': f'{resrc_dir}/拼音表_扩展集_后缀树.json',
                }
            },
            'wade'        : {
                'standard': {
                    'plain'  : f'{resrc_dir}/韦氏拼音表_标准集.txt',
                    'trie'   : f'{resrc_dir}/韦氏拼音表_标准集_前缀树.json',
                    'postrie': f'{resrc_dir}/韦氏拼音表_标准集_后缀树.json',
                },
                'extend'  : {
                    'plain'  : f'{resrc_dir}/韦氏拼音表_扩展集.txt',
                    'trie'   : f'{resrc_dir}/韦氏拼音表_扩展集_前缀树.json',
                    'postrie': f'{resrc_dir}/韦氏拼音表_扩展集_后缀树.json',
                }
            },
            'pinyin+wade' : {
                'ss': {
                    'plain'  : f'{resrc_dir}/拼音表(标准集)+韦氏拼音表(标准集).txt',
                    'trie'   : f'{resrc_dir}/拼音表(标准集)+韦氏拼音表(标准集)_前缀树.json',
                    'postrie': f'{resrc_dir}/拼音表(标准集)+韦氏拼音表(标准集)_后缀树.json',
                },
                'se': {
                    'plain'  : f'{resrc_dir}/拼音表(标准集)+韦氏拼音表(扩展集).txt',
                    'trie'   : f'{resrc_dir}/拼音表(标准集)+韦氏拼音表(扩展集)_前缀树.json',
                    'postrie': f'{resrc_dir}/拼音表(标准集)+韦氏拼音表(扩展集)_后缀树.json',
                },
                'es': {
                    'plain'  : f'{resrc_dir}/拼音表(扩展集)+韦氏拼音表(标准集).txt',
                    'trie'   : f'{resrc_dir}/拼音表(扩展集)+韦氏拼音表(标准集)_前缀树.json',
                    'postrie': f'{resrc_dir}/拼音表(扩展集)+韦氏拼音表(标准集)_后缀树.json',
                    
                },
                'ee': {
                    'plain'  : f'{resrc_dir}/拼音表(扩展集)+韦氏拼音表(扩展集).txt',
                    'trie'   : f'{resrc_dir}/拼音表(扩展集)+韦氏拼音表(扩展集)_前缀树.json',
                    'postrie': f'{resrc_dir}/拼音表(扩展集)+韦氏拼音表(扩展集)_后缀树.json',
                }
            },
            'chinese_name': {
                'pinyin': {
                    'single': f'{resrc_dir}/中国姓氏_拼音_单姓.txt',
                    'double': f'{resrc_dir}/中国姓氏_拼音_复姓.txt',
                    'wade'  : f'{resrc_dir}/中国姓氏_拼音_韦氏.txt',
                },
                'hanz'  : {
                    'single': f'{resrc_dir}/中国姓氏_汉字_单姓.txt',
                    'double': f'{resrc_dir}/中国姓氏_汉字_复姓.txt',
                    # 韦氏没有汉字
                }
            }
        }
    
    def get(self, data_type, data_spec, data_fmt):
        # Use case: e.g. lexicon.get('pinyin', 'standard', 'trie')
        return self.resrc[data_type][data_spec][data_fmt]


lexicon = Lexicon()


# ------------------------------------------------------------------------------

class PinyinCutter:
    
    def __init__(self, wade_mode=False, trie_mode='postrie'):
        """
        :param wade_mode: bool
        :param trie_mode: str. 'postrie'/'trie'.
            'postrie': 反向最大匹配切词法. 例如:
                'yangan' -> ['yan', 'gan']
                'daniel' -> ['da', 'nie', 'l']
            'trie': 正向最大匹配切词法. 例如:
                'yangan' -> ['yang', 'an']
                'daniel' -> ['dan', 'i', 'e', 'l']
        """
        self.obsv_mode = 'trie'  # obsv: observer (no usage)
        self.trie_mode = trie_mode
        
        if wade_mode:
            ifile1 = lexicon.get('pinyin+wade', 'se', 'plain')
            ifile2 = lexicon.get('pinyin+wade', 'se', trie_mode)
        else:
            ifile1 = lexicon.get('pinyin', 'standard', 'plain')
            ifile2 = lexicon.get('pinyin', 'standard', trie_mode)
        
        self.pinyin_list = read_lines(ifile1)  # type: list
        self.root = read_json(ifile2)  # type: dict
        
        self.reg = re.compile(r'\w+')
    
    def main(self, name: str) -> list:
        """
        IO: 'wang, kworay dongyang' -> ['wang', 'kworay', 'dong', 'yang']
        """
        # name = 'wang, kworay dongyang'
        segs = self.reg.findall(name)
        # -> ['wang', 'kworay', 'dongyang']
        if self.trie_mode == 'postrie':
            segs = [self.cut_segs_2(x) for x in segs]
        else:
            segs = [self.cut_segs_1(x) for x in segs]
        # refer_segs = [self.cut_segs_1(x) for x in segs]
        # segs = refer_segs.copy() if self.obsv_mode == self.trie_mode \
        #     else [self.cut_segs_2(x) for x in segs]
        # print(segs)
        # -> [['wang'], ['kwo', 'r', 'a', 'y'], ['dong', 'yang']]
        
        out = []
        
        for i in segs:
            i = self.merge_segs(i)
            """
            ['wang'] -> 'wang'
            ['kwo', 'r', 'a', 'y'] -> 'kworay'
            ['dong', 'yang'] -> 'dong yang'
            """
            if ' ' in i:
                out.extend(i.split(' '))
            else:
                out.append(i)
        # ['wang', 'kworay', 'dong yang'] -> ['wang', 'kworay', 'dong', 'yang']
        
        return out
    
    def cut_segs_1(self, word: str) -> list:
        """ 适用于 trie_mode = 'trie'.
        
        IO: 'wang'   -> ['wang']
            'chihau' -> ['chih', 'au']
            'xingan' -> ['xing', 'an']
            'daniel' -> ['dan', 'i', 'e', 'l']
            'frank'  -> ['f', 'ran', 'k']
            'kworay' -> ['kwo', 'r', 'a', 'y']
        """
        node = self.root
        out = []
        found = ''
        
        for i, w in enumerate(word):
            node = node.get(w, None)
            if node:
                found += w
            else:
                # submit and reset
                if found:
                    out.append(found)
                found = w
                node = self.root.get(w, None)
                if node:
                    continue
                else:
                    # submit and reset
                    out.append(found)
                    found = ''
                    node = self.root
        if found:
            out.append(found)
        # -> ['wang', ' ', 'chi', 'hau', ' ', 'f', 'ran', 'k']
        
        return out
    
    def cut_segs_2(self, word: str) -> list:
        """ 适用于 trie_mode = 'postrie'. 这是默认的选择.
        
        IO: 'wang'   -> ['wang']
            'chihau' -> ['chi', 'hau']
            'xingan' -> ['xin', 'gan']
            'daniel' -> ['da', 'nie', 'l']
            'frank'  -> ['f', 'ran', 'k']
            'kworay' -> ['kwo', 'r', 'a', 'y']
        """
        node = self.root
        out = []
        found = ''
        
        for i, w in enumerate(word[::-1]):
            node = node.get(w, None)
            if node:
                found += w
            else:
                # submit and reset
                if found:
                    out.append(found)
                found = w
                node = self.root.get(w, None)
                if node:
                    continue
                else:
                    # submit and reset
                    out.append(found)
                    found = ''
                    node = self.root
        if found:
            out.append(found)
        # -> ['k', 'nar', 'f', ' ', 'uah', 'ihc', ' ', 'gnaw']
        
        out = [x[::-1] for x in out][::-1]
        # -> ['k', 'ran', 'f', ' ', 'hau', 'chi', ' ', 'wang']
        # -> ['wang', ' ', 'chi', 'hau', ' ', 'f', 'ran', 'k']
        
        return out
    
    def merge_segs(self, segs: list) -> str:
        """
        策略:
            case 1: (TODO)
                假设有 'jonathan' 被切分为 segs (trie_mode = 'postrie'):
                    ['jo', 'nat', 'han'].
                我们期望的结果是, 经本方法处理后, 返回的字符串为: 'jonathan'.
                则通过以下策略实现:
                    1. 通过正向切分, 获得一个序列: ['jo', 'na', 't', 'han']
                    2. 观察其中有一个单字母, 则认定为切分不正确, 那么就合并它
                    3. 合并后结果: 'jonathan'. 返回
                    
        IO:
            ['wang', 'ge'] -> 'wang ge'
            ['kwo', 'r', 'a', 'y'] -> 'kwo ray'
            ['j', 'am', 'es', 'liu'] -> 'james liu'
            ['f', 'ran', 'k'] -> 'frank'
        """
        if any(x for x in segs if len(x) == 1):
            # 'samuel' -> ['sa', 'm', 'ue', 'l'] -> 'samuel'
            return ''.join(segs)
        
        # if all(bool(x in self.pinyin_list) for x in segs):
        #     # 'hongsheng' -> ['hong', 'sheng'] -> 'hong sheng'
        #     return ' '.join(segs)
        
        out = []
        holder = []
        
        for i in segs:
            holder.append(i)
            if i in self.pinyin_list:
                out.append(''.join(holder))
                holder.clear()
            else:
                continue
        
        if holder:
            out.append(''.join(holder))
        
        if len(out) >= 3:
            return ''.join(out)
        else:
            return ' '.join(out)


class PinyinProcessor:
    pinyin_cutter: PinyinCutter
    pinyin_patterns: dict
    pinyin_patterns_4_name: dict
    wade_mode: bool
    word_pattern: re.Pattern
    trie: Trie
    
    def __init__(self, wade_mode=False, trie_mode='postrie'):
        self.wade_mode = wade_mode
        self.pinyin_cutter = PinyinCutter(wade_mode, trie_mode)
        self._init_tries(wade_mode)
        self._init_pinyin_patterns(wade_mode)
    
    def _init_tries(self, wade_mode: bool):
        self.trie = Trie()
        if wade_mode:
            self.trie.load(lexicon.get('pinyin+wade', 'se', 'trie'))
            # -> 拼音表(标准集)+韦氏拼音表(扩展集)_前缀树.json
        else:
            self.trie.load(lexicon.get('pinyin', 'standard', 'trie'))
            # -> 拼音表_标准集_前缀树.json
    
    def _init_pinyin_patterns(self, wade_mode: bool):
        """ 读取中国姓氏拼音列表. """
        # self.word_pattern 该匹配式用于匹配人名中所有连续字符串, 从而剔除掉逗
        #   号, 引号, 句点之类的干扰因素.
        self.word_pattern = re.compile(r'\w+')
        
        self.pinyin_patterns = {
            'pinyin'     : read_lines(
                lexicon.get('pinyin', 'extend', 'plain')
            ),
            'wade'       : read_lines(
                lexicon.get('wade', 'extend', 'plain')
            ),
            'pinyin+wade': read_lines(
                lexicon.get('pinyin+wade', 'ee', 'plain')
            )
        }
        
        self.pinyin_patterns_4_name = {
            'single'    : read_lines(
                lexicon.get('chinese_name', 'pinyin', 'single')
            ),  # -> 中国姓氏_拼音_单姓.txt
            'double'    : read_lines(
                lexicon.get('chinese_name', 'pinyin', 'double')
            ),  # -> 中国姓氏_拼音_复姓.txt
            'wade'      : read_lines(
                lexicon.get('chinese_name', 'pinyin', 'wade')
            ),  # -> 中国姓氏_拼音_韦氏.txt
            'exceptions': (
                # 'ai',
                'al',
                'de la', 'de', 'der', 'des', 'di',
                'el',
                'fits', 'fitz', 'ftz',
                'jr', 'jun', 'junior',
                'la', 'le',
                'mac', 'mc',
                # 'o',
                'van', 'von',
            )
        }
        
        if wade_mode:
            self.pinyin_patterns['default'] = \
                self.pinyin_patterns['pinyin+wade']
            self.pinyin_patterns_4_name['default'] = [
                *self.pinyin_patterns_4_name['single'],
                *self.pinyin_patterns_4_name['double'],
                *self.pinyin_patterns_4_name['wade'],
            ]
        else:
            self.pinyin_patterns['default'] = self.pinyin_patterns['pinyin']
            self.pinyin_patterns_4_name['default'] = [
                *self.pinyin_patterns_4_name['single'],
                *self.pinyin_patterns_4_name['double'],
            ]
    
    # --------------------------------------------------------------------------
    # pinyin patterns
    
    def is_chinese(self, name: str) -> bool:
        """ 给定一个名字, 根据他的姓氏来判断是不是中国人.
        
        NOTE:
            1. name 全小写.
            2. 当传入全名时, 必须使用姓前名后且姓和名之间用英文逗号加空格分隔,
               也就是 'lastname, firstname' 的形式. 例如 "zhang, san".
            3. 由于针对全名的判断 (e.g. "jan, edward" 和 "jan, ping xin") 并不完
               善, 所以目前 (2019年12月3日) 不启用.
        
        IO: da         -> True
            hu         -> True
            baker      -> False
            ouyang     -> True
            ou yang    -> True
            von briton -> False
            
        :param name: 您可以传整个姓名, 也可以只传姓氏. 姓名只支持 'lastname,
            firstname' 格式的姓名. 当传入姓名时, 判断可能会更加准确. 例如, 如果
            只传入 "jan", 那么在 `self.wade_mode is True` 的情况下, 会判断为
            True; 而传入 "jan, edward" 和 "jan, ping xin", 则会分别判断为 False
            和 True.
        """
        name = name.lower()
        
        if ', ' in name:
            lastname, firstname = name.split(', ', 1)
            # 'zhang, tiejun' -> 'zhang', 'tiejun'
        else:
            lastname, firstname = name, ''
        # NOTE: 由于针对 firstname 的判断并不完善, 且容易存在误判, 所以
        # firstname 变量暂时 (2019年12月3日) 没有任何作用.
        
        if lastname in self.pinyin_patterns_4_name['double']:
            # e.g. lastname = 'ouyang' -> True
            return True
        
        if ' ' in lastname and any(
                lastname.startswith(x)
                for x in self.pinyin_patterns_4_name['exceptions']
        ):  # e.g. lastname = 'von briton'
            return False
        
        """
        NOTE: 原先是打算用 self.pinyin_patterns_4_name 的 pinyin 和 wade 的值来
            判断的, 后来发现有些罕见的姓, 虽然符合拼音或韦氏拼音的构造规则, 但由
            于不在 self.pinyin_patterns_4_name 范围内, 所以会被误判为非中国人名.
            为避免这种情况, 不再使用 self.pinyin_patterns_4_name 提供的 pinyin
            和 wade, 改用 self.pinyin_patterns 的 'pinyin+wade'.
        """
        if self.wade_mode:
            return lastname in self.pinyin_patterns['pinyin+wade']
        else:
            return lastname in self.pinyin_patterns['pinyin']
    
    # --------------------------------------------------------------------------
    # tries
    
    def is_pinyin(self, name, strict=False):
        """ 判断名字是英文单词还是拼音的形式.
        
        IO: | gerald    | False | 识别出英文名         |
            | ming      | True  | 识别出拼音           |
            | lee       | True  | 支持韦氏拼音         |
            | guangshan | True  | 支持拼接在一起的拼音 |
            
        NOTE:
            1. 请确保 name 是全小写, 否则 self.trie 无法正常工作.
            2. 建议 name 只传入单词.
            3. 可能存在误识别. 例如 "sheer" 会被认作 ["she", "er"] -> True. 您可
               以通过传递 strict=True 参数来关闭分词模式.
            4. 对于中英混合的情况, 会返回 False. 例如 "zhen cool" -> False.
        """
        if name in self.pinyin_patterns['default']:
            return True
        elif strict:
            return False
        else:
            name1 = ''.join(self.word_pattern.findall(name))
            name2 = ''.join(self.trie.findall(name1))
            return name1 == name2
    
    def cut_pinyin(self, name: str) -> list:
        """ 对中国人名拼音的切分.
        
        特点:
            1. 支持对普通拼音的切分
            2. 支持对中国复姓的切分
            3. 支持对有歧义的发音的切分
            4. 支持单音节词 (比如 a, o, e, er, ai, ang 等) 的发音匹配
            5. 当 wade_mode 为 True 时, 支持韦氏拼音的切分
            6. 即便在切分失败的情况下, 也能返回较理想的切分结果
                示例:
                    'li, gerald adam'
                    -> 英文单词无法正常切分
                    -> 返回 ['li', 'gerald', 'adam']
                    'fan, taiping d.'
                    -> 'd' 无法正常切分
                    -> 返回 ['fan', 'tai', 'ping', 'd']
            
        效果:
            一般人名 (朱自清): 'zhuziqing' -> ['zhu', 'zi', 'qing']
            复姓 (欧阳修): 'ouyangxiu' -> ['ou', 'yang', 'xiu']
            歧义组合 (柴凤安): 'chaifengan' -> ['chai', 'feng', 'an'] (注: 不支
                持切出 chai fen gan)
            单音节词1 (刘酬安): 'liuchouan' -> ['liu', 'chou', 'an']
            单音节词2 (刘马鄂): 'liumae' -> ['liu', 'ma', 'e']
    
        注:
            对于某些歧义组合, 只支持最大向前匹配. 例如:
                "fangan" -> ["fang", "an"]
            wade_mode 可能引发切分错误. 错误主要发生在韦氏拼音的韵母的最后一个字
            母和下一个字的声母的首字母冲突, 例如:
                "wang, wiehen" -> ["wang", "wieh", "en"] (切分不当)
    
        参考:
            https://blog.csdn.net/lemon_tree12138/article/details/49074809
                #commentBox
            https://zhidao.baidu.com/question/21799136.html
        """
        return self.pinyin_cutter.main(name)


# ------------------------------------------------------------------------------

class HanzProcessor:
    
    def __init__(self):
        self.lastname_single = read_lines(
            lexicon.get('chinese_name', 'hanz', 'single')
        )  # -> 中国姓氏_汉字_单姓.txt
        self.lastname_double = read_lines(
            lexicon.get('chinese_name', 'hanz', 'double')
        )  # -> 中国姓氏_汉字_复姓.txt
        self.is_letter = re.compile('[a-zA-Z]')
    
    def is_chinese(self, name: str) -> bool:
        if self.is_letter.findall(name):
            return False
        if 2 <= len(name) <= 4:
            if name[0] in self.lastname_single \
                    or name[0:2] in self.lastname_double:
                # TODO: 检查常用名 (参考盘古分词)
                return True
        return False
    
    def chinese_name_to_pinyin(self, name: str,
                               conjunction='') -> Union[str, List[str]]:
        """ 将中国人名 (中文名) 转换成拼音.
        
        IO: conjunction = ''
                诸葛孔明 -> 'Zhuge, Kongming'
                刘长卿   -> 'Liu, Changqing'
            conjunction = ' '
                诸葛孔明 -> 'Zhu Ge, Kong Ming'
                刘长卿   -> 'Liu, Chang Qing'
            conjunction = '-'
                诸葛孔明 -> 'Zhu-Ge, Kong-Ming'
                刘长卿   -> 'Liu, Chang-Qing'
            conjunction = 'list'
                诸葛孔明 -> ['zhu', 'ge', 'kong', 'ming']
                刘长卿   -> ['liu', 'chang', 'qing']
            ...
        
        本函数特点:
            1. 支持多音字姓氏的简易转换, 以规避误发音的情况
            2. 针对常见复姓做了调整, 可以正确地把复姓当做姓氏
        """
        # noinspection PyUnresolvedReferences
        from pypinyin import lazy_pinyin
        name = self.polyphonic_conversion(name)
        pinyin = lazy_pinyin(name)
        # '张磊' -> ['zhang', 'lei']
        if conjunction == 'list':
            return pinyin
        
        compound_surnames = (
            "欧阳", "诸葛", "东方", "端木", "上官", "公孙", "司马"
        )
        if any(x for x in compound_surnames if x in name):
            cut_point = 2
        else:
            cut_point = 1
        
        if conjunction == '':
            lastname = (conjunction.join(pinyin[:cut_point])).title()
            firstname = (conjunction.join(pinyin[cut_point:])).title()
        else:
            lastname = conjunction.join((x.title()
                                         for x in pinyin[:cut_point]))
            firstname = conjunction.join((x.title()
                                          for x in pinyin[cut_point:]))
        return f'{lastname}, {firstname}'
    
    @staticmethod
    def polyphonic_conversion(name: str) -> str:
        """ 将百家姓中的多音字转换为同音的非多音字.
        
        百家姓里的多音字: https://zhidao.baidu.com/question/188597315.html?qbl=
            relate_question_0&word=%B0%D9%BC%D2%D0%D5%20%B6%E0%D2%F4%D7%D6
        
        注意:
            1. "汤" -> "商" 变换未认证, 所以没收录
            2. "黑" -> "he" 情况比较复杂, 有些地方的人还是读成 "hei", 所以不收录
            2. 一般来说, "长" 在人名中经常被读 "chang", 例如 "左长宁", "杨虎长",
               另外, 也有一个例外情况是 "杨成长", 这时适合读 "zhang", 可根据这种
               规则来调节
        """
        
        polyphonic = {
            '秘': '必', '薄': '博', '卜': '补', '重': '崇', '都': '杜',
            '盖': '葛', '缪': '妙', '区': '欧', '朴': '飘', '仇': '求',
            '单': '善', '折': '舌', '冼': '显', '解': '谢', '员': '蕴',
            '曾': '增', '查': '渣', '翟': '宅',
            # 其他常用字 (非姓氏, 常见于名)
            '伽': '加', '长': '常',
        }
        
        # 针对 '长' 多音字的特别处理
        if '成长' in name:
            # e.g. name = '杨成长' -> zhang
            name = name.replace('成长', '成章')
        
        for i in name:
            if i in polyphonic:
                name = name.replace(i, polyphonic[i])
        
        return name

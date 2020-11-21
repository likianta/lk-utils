"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : lk_wrapper.py
@Created : 2019-10-25
@Updated : 2020-08-09
@Version : 0.3.0
@Desc    : 对一些常用模块的进一步封装, 以便于更加简洁地调用.
"""
import re

# noinspection PyProtectedMember
from bs4 import (BeautifulSoup as _BeautifulSoup,
                 NavigableString, SoupStrainer, Tag)


class BeautifulSoup(_BeautifulSoup):
    
    def __init__(self, ifile, ftype='file', parser='lxml', **kwargs):
        if ftype == 'file':
            from . import read_and_write
            html = read_and_write.read_file(ifile)
        else:  # ftype == 'text'
            html = ifile
        super().__init__(html, parser, **kwargs)
    
    def insert_before(self, successor):
        super().insert_before(successor)
    
    def insert_after(self, successor):
        super().insert_after(successor)

    # --------------------------------------------------------------------------

    @staticmethod
    def _find_sequent_siblings(source, name: str, attrs: dict, limit=0,
                               direction='next'):
        """
        本方法根据 bs4.element.Tag._find_all() 改编.
        
        假设 HTML 为:
            <h3>管理部门</h3> --- e1 (source)
            <p>张</p> ----------- e2
            <p>李</p> ----------- e3
            <h3>财务部门</h3> --- e4
            <p>王</p> ----------- e5
            <p>刘</p> ----------- e6
        其中 e1 为 source 参数. e2, e3, e5, e6 的标签特征相同. 如果我们想获得
        [e2, e3], 怎么做?
        bs4 提供的 find_next_siblings() 方法, 仅能获得 [e2, e3, e5, e6]. 而本方
        法则可以只获得 [e2, e3].
        
        更准确的描述是: 本方法可以找到 source 元素之前/之后的连续的符合目标条件
        的兄弟元素. 以目标元素第一次出现开始计算, 直到目标元素第一次被其他元素打
        断为结束, 这段区间的目标元素作为列表返回.
        
        IN: attrs: dict
            direction: 'next' | 'previous'
        OT: [<bs4.element.Tag element>]
        """
        generator = source.next_siblings if direction == 'next' \
            else source.previous_siblings
        generator = filter(lambda x: isinstance(x, Tag), generator)
        
        if ':' in name:
            prefix, name = name.split(':', 1)
        else:
            prefix, name = None, name
        
        if attrs:
            check = SoupStrainer(name, attrs).search
        else:
            # we can do it faster if there's only name to find.
            def check(x):
                return bool(
                    x.name == name
                    and (prefix is None or x.prefix == prefix)
                )
        
        out = []
        for index, element in enumerate(generator):
            if limit == 0 or index <= limit:
                if check(element):
                    out.append(element)
                elif out:
                    break
            else:
                break
        return out
    
    def find_sequent_next_siblings(self, source: Tag, name, attrs=None):
        return self._find_sequent_siblings(
            source, name, attrs or {}, direction='next'
        )
    
    def find_sequent_previous_siblings(self, source: Tag, name, attrs=None):
        return self._find_sequent_siblings(
            source, name, attrs or {}, direction='previous'
        )

    # --------------------------------------------------------------------------

    @staticmethod
    def find_tail(source: Tag):
        for i in source.contents:
            if i == '\n':
                continue
            if isinstance(i, NavigableString):
                return i
            else:
                return None
    
    @staticmethod
    def find_bare_strings(element: Tag):
        """
        IN: <p>
                "AAA"
                <span>CCC</span>
                <br>
                "BBB"
            </p>
        OT: ["AAA", "BBB"]
        """
        out = []
        for i in element.contents:
            if isinstance(i, NavigableString):
                if j := i.strip():
                    out.append(j)
        return out


class Regex:
    exp = None
    
    def compile(self, exp):
        self.exp = re.compile(exp)
        return self
    
    def _find(self, x, pos: int):
        try:
            return self.exp.findall(x)[pos]
        except AttributeError:
            return None
    
    def find_one(self, x, pos=0):
        return self._find(x, pos)
    
    find = find_one
    
    def find_last(self, x):
        return self._find(x, -1)
    
    def find_all(self, x):
        return self.exp.findall(x)
    
    @staticmethod
    def sub(a, b, c):
        return re.sub(a, b, c)


lkre = Regex()

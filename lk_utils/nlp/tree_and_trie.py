"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : tree_and_trie.py
@Created : 2019-00-00
@Updated : 2020-08-09
@Version : 1.1.5
@Desc    : 前缀树和后缀树.
"""
from .. import read_and_write


class Prototype:
    root = None
    end = '/'
    
    def __init__(self, x=''):
        if not x:
            self.root = {}
        else:
            self.load(x)
    
    def load(self, x):
        if isinstance(x, str):
            # 说明 x 是一个 json 文件路径. 那么读取 json 并载入为字典
            self.root = read_and_write.read_json(x)
        else:
            # 说明 x 是一个字典
            self.root = x
    
    def update(self, x):
        if isinstance(x, str):
            self.root.update(read_and_write.read_json(x))
        else:
            self.root.update(x)
    
    def save(self, path):
        read_and_write.write_json(self.root, path)
        
    def clear(self):
        self.root.clear()


class Tree(Prototype):
    
    def get(self, *data):
        if len(data) == 1:
            return self.root.get(data[0], None)
        
        node = self.root
        for i, d in enumerate(data):
            try:
                node = node[d]
            except KeyError:
                return None
        return node
    
    def set(self, *data):
        if len(data) == 1:
            # NOTICE: cannot set a data with only one or less element.
            raise AttributeError
        elif len(data) == 2:
            k, v = data
            self.root[k] = v
        else:
            temp_dict = {}
            node = temp_dict
            for i in data[:-2]:
                node = node.setdefault(i, {})
            node.setdefault(data[-2], data[-1])
            self.root.update(temp_dict)


class Trie(Prototype):
    """ 前缀树. """
    bad_return = ''
    
    def add_list(self, words: list, end=''):
        for w in words:
            self.add(w, end)
    
    def add(self, word: str, end=''):
        """ 将传入的单词逐字符更新到前缀树中
        效果:
            假设有以下单词: tie, tea, try, tree
            则生成前缀树:
                {'t': {'i': {'e': {'/': ''}}, 'e': {'a': {'/': ''}, 'e': {'/':
                ''}}, 'r': {'y': {'/': ''}}}
        参考:
            https://blog.csdn.net/handsomekang/article/details/41446319
        """
        if not isinstance(word, str):  # TODO temp method (20190426)
            raise AttributeError
        node = self.root
        for w in word:
            node = node.setdefault(w, {})
        node[self.end] = end
    
    def find(self, word, allow_partial=True):
        """
        查找单词的在树字符部分.

        示例:
            假设前缀树中已储存了 "talk" 的链.
            allow_partial = True
                word = 'told' -> 't'
                word = 'talking' -> 'talk'
            allow_partial = False
                word = 'told' -> ''
                word = 'talking' -> ''
        """
        node = self.root
        for i, w in enumerate(word):
            try:
                node = node[w]
            except KeyError:
                if allow_partial:
                    return word[:i]
                else:
                    return self.bad_return
        
        if allow_partial or self.end in node:
            return word
        else:
            return self.bad_return
    
    def findall(self, word: str, allow_partial=False):
        """ 从文本中, 查找全部在树的单词.

        :param word:
        :param allow_partial:
        :return:
        """
        found = []
        
        node = self.root
        offset = 0
        
        for i, w in enumerate(word):
            try:
                node = node[w]
            except KeyError:
                if allow_partial or self.end in node:
                    # update (method 1)
                    found.append(word[offset:i])
                
                node = self.root
                
                try:
                    node = node[w]
                    offset = i
                except KeyError:
                    if offset == 1:
                        offset += 1
                    else:
                        if allow_partial or self.end in node:
                            # update (method 1)
                            found.append(word[offset:i])
                        offset = i + 1
                    node = self.root
        
        if offset != len(word):
            if allow_partial or self.end in node:
                # update (method 2)
                found.append(word[offset:])
        
        return found
    
    def find_node(self, word, allow_partial=False, use_copy=False):
        node = self.root
        for i, w in enumerate(word):
            try:
                node = node[w]
            except KeyError:
                if allow_partial:
                    if use_copy:
                        return node.copy()
                    else:
                        return node
                else:
                    return self.bad_return
        
        if allow_partial or self.end in node:
            if use_copy:
                return node.copy()
            else:
                return node
        else:
            return self.bad_return


class ElementTrie(Trie):
    
    def add(self, data, end=None):
        node = self.root
        for i in data:
            node = node.setdefault(i, {})
        node[self.end] = end
    
    # def find(self, data, allow_partial=True):
    #     """
    #     查找单词的在树字符部分.
    # 
    #     示例:
    #         假设前缀树中已储存了 "talk" 的链.
    #         allow_partial = True
    #             word = 'told' --> 't'
    #             word = 'talking' --> 'talk'
    #         allow_partial = False
    #             word = 'told' --> ''
    #             word = 'talking' --> ''
    #     """
    #     node = self.root
    #     for i, datum in enumerate(data):
    #         try:
    #             node = node[datum]
    #         except KeyError:
    #             if allow_partial:
    #                 return data[:i]
    #             else:
    #                 return ''
    # 
    #     if allow_partial or self.end in node:
    #         return data
    #     else:
    #         return ''


""" The differences of Tree, Trie and ElementTrie:
    The root of a Tree instance for example:
        {
            school: {
                grade1: {students: 50},
                grade2: {students: 40}
            }
        }
    The root of a Trie instance for example:
        {
            's': {
                'c': {'h': {'o': {'o': {'l': {'/': ''}}}}},
                't': {'u': {'d': {'e': {'n': {'t': {'s': {'/': ''}}}}}}}
            }
        }
    The root of a ElementTrie instance for example:
        {
            school: {
                grade1: {students: {'/': 50}},
                grade2: {students: {'/': 40}},
            }
        }
"""


def simple_lexicon_generate(i='../temp/in.txt', o='../temp/out.json'):
    words = read_and_write.read_lines(i)
    trie = Trie()
    for w in words:
        trie.add(w)
    trie.save(o)

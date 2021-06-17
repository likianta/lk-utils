from shutil import copyfile

from lk_utils import lk
from lk_utils import read_and_write
from lk_utils.tree_and_trie import Trie


def main():
    """
    IN:
        拼音表.txt
        非标准拼音表.txt
        韦氏拼音表.txt
        非标准韦氏拼音表.txt
    OT:
        拼音表_标准集.txt
        拼音表_标准集_前缀树.json
        拼音表_标准集_后缀树.json
        拼音表_扩展集.txt
        拼音表_扩展集_前缀树.json
        拼音表_扩展集_后缀树.json
        韦氏拼音表_标准集.txt
        韦氏拼音表_标准集_前缀树.json
        韦氏拼音表_标准集_后缀树.json
        韦氏拼音表_扩展集.txt
        韦氏拼音表_扩展集_前缀树.json
        韦氏拼音表_扩展集_后缀树.json
        拼音表(标准集)+韦氏拼音表(标准集).txt
        拼音表(标准集)+韦氏拼音表(标准集)_前缀树.json
        拼音表(标准集)+韦氏拼音表(标准集)_后缀树.json
        拼音表(标准集)+韦氏拼音表(扩展集).txt
        拼音表(标准集)+韦氏拼音表(扩展集)_前缀树.json
        拼音表(标准集)+韦氏拼音表(扩展集)_后缀树.json
        拼音表(扩展集)+韦氏拼音表(标准集).txt
        拼音表(扩展集)+韦氏拼音表(标准集)_前缀树.json
        拼音表(扩展集)+韦氏拼音表(标准集)_后缀树.json
        拼音表(扩展集)+韦氏拼音表(扩展集).txt
        拼音表(扩展集)+韦氏拼音表(扩展集)_前缀树.json
        拼音表(扩展集)+韦氏拼音表(扩展集)_后缀树.json
        
    注: 关于 lk 打印的 WARNING 级别错误, 我们只需看 "拼音表 标准集", "拼音表 扩
    展集", "韦氏拼音表 标准集" 和 "韦氏拼音表 扩展集" 这四个. 关注点在于:
        1. "拼音表 标准集" 是否有重复的拼音
        2. "拼音表 扩展集" 是否有非标准拼音在标准拼音里能找到 (如果有请从非标准
        拼音文件中删除)
        3. "韦氏拼音表 标准集" 是否有重复的拼音
        4. "韦氏拼音表 扩展集" 是否有非标准韦氏拼音在标准韦氏拼音里能找到 (如果
        有请删除)
    一般来说, 经过一两次纠正, 1 和 3 的情况就会彻底消失; 而 2 和 4 是时常出现的
    问题, 所以要重点关照.
    另外, 可以放心的是, 重复的拼音在任何导出文件中都不会重复存在. 因为本脚本在导
    出时会做去重识别.
    """
    ifile1 = '拼音表.txt'
    ifile2 = '非标准拼音表.txt'
    ifile3 = '韦氏拼音表.txt'
    ifile4 = '非标准韦氏拼音表.txt'
    
    # ------------------------------------------------
    lk.logd('拼音表 标准集')
    
    # 拼音表_标准集.txt
    generate_plain_file(
        ifile1,
        ofile='../拼音表_标准集.txt', check_duplicate=True
    )
    
    # 拼音表_标准集_前缀树.json
    generate_trie_file(
        ifile1,
        ofile='../拼音表_标准集_前缀树.json', check_duplicate=True
    )
    
    # 拼音表_标准集_后缀树.json
    generate_postrie_file(
        ifile1,
        ofile='../拼音表_标准集_后缀树.json', check_duplicate=True
    )
    
    # ------------------------------------------------
    lk.logd('拼音表 扩展集')
    
    # 拼音表_扩展集.txt
    generate_plain_file(
        ifile1, ifile2,
        ofile='../拼音表_扩展集.txt', check_duplicate=True
    )
    
    # 拼音表_扩展集_前缀树.json
    generate_trie_file(
        ifile1, ifile2,
        ofile='../拼音表_扩展集_前缀树.json', check_duplicate=True
    )
    
    # 拼音表_扩展集_后缀树.json
    generate_postrie_file(
        ifile1, ifile2,
        ofile='../拼音表_扩展集_后缀树.json', check_duplicate=True
    )
    
    # ------------------------------------------------
    lk.logd('韦氏拼音表 标准集')
    
    # 韦氏拼音表_标准集.txt
    generate_plain_file(
        ifile3,
        ofile='../韦氏拼音表_标准集.txt', check_duplicate=True
    )
    
    # 韦氏拼音表_标准集_前缀树.json
    generate_trie_file(
        ifile3,
        ofile='../韦氏拼音表_标准集_前缀树.json', check_duplicate=True
    )
    
    # 韦氏拼音表_标准集_后缀树.json
    generate_postrie_file(
        ifile3,
        ofile='../韦氏拼音表_标准集_后缀树.json', check_duplicate=True
    )
    
    # ------------------------------------------------
    lk.logd('韦氏拼音表 扩展集')
    
    # 韦氏拼音表_扩展集.txt
    generate_plain_file(
        ifile3, ifile4,
        ofile='../韦氏拼音表_扩展集.txt', check_duplicate=False
    )
    
    # 韦氏拼音表_扩展集_前缀树.json
    generate_trie_file(
        ifile3, ifile4,
        ofile='../韦氏拼音表_扩展集_前缀树.json', check_duplicate=False
    )
    
    # 韦氏拼音表_扩展集_后缀树.json
    generate_postrie_file(
        ifile3, ifile4,
        ofile='../韦氏拼音表_扩展集_后缀树.json', check_duplicate=False
    )
    
    # ------------------------------------------------
    lk.logd('拼音表 (标准集) + 韦氏拼音表 (标准集)')
    
    # 拼音表(标准集)+韦氏拼音表(标准集).txt
    generate_plain_file(
        ifile1, ifile3,
        ofile='../拼音表(标准集)+韦氏拼音表(标准集).txt'
    )
    
    # 拼音表(标准集)+韦氏拼音表(标准集)_前缀树.json
    generate_trie_file(
        ifile1, ifile3,
        ofile='../拼音表(标准集)+韦氏拼音表(标准集)_前缀树.json'
    )
    
    # 拼音表(标准集)+韦氏拼音表(标准集)_后缀树.json
    generate_postrie_file(
        ifile1, ifile3,
        ofile='../拼音表(标准集)+韦氏拼音表(标准集)_后缀树.json'
    )
    
    # ------------------------------------------------
    lk.logd('拼音表 (标准集) + 韦氏拼音表 (扩展集)')
    
    # 拼音表(标准集)+韦氏拼音表(扩展集).txt
    generate_plain_file(
        ifile1, ifile3, ifile4,
        ofile='../拼音表(标准集)+韦氏拼音表(扩展集).txt'
    )
    
    # 拼音表(标准集)+韦氏拼音表(扩展集)_前缀树.json
    generate_trie_file(
        ifile1, ifile3, ifile4,
        ofile='../拼音表(标准集)+韦氏拼音表(扩展集)_前缀树.json'
    )
    
    # 拼音表(标准集)+韦氏拼音表(扩展集)_后缀树.json
    generate_postrie_file(
        ifile1, ifile3, ifile4,
        ofile='../拼音表(标准集)+韦氏拼音表(扩展集)_后缀树.json'
    )
    
    # ------------------------------------------------
    lk.logd('拼音表 (扩展集) + 韦氏拼音表 (标准集)')
    
    # 拼音表(扩展集)+韦氏拼音表(标准集).txt
    generate_plain_file(
        ifile1, ifile2, ifile3,
        ofile='../拼音表(扩展集)+韦氏拼音表(标准集).txt'
    )
    
    # 拼音表(扩展集)+韦氏拼音表(标准集)_前缀树.json
    generate_trie_file(
        ifile1, ifile2, ifile3,
        ofile='../拼音表(扩展集)+韦氏拼音表(标准集)_前缀树.json'
    )
    
    # 拼音表(扩展集)+韦氏拼音表(标准集)_后缀树.json
    generate_postrie_file(
        ifile1, ifile2, ifile3,
        ofile='../拼音表(扩展集)+韦氏拼音表(标准集)_后缀树.json'
    )
    
    # ------------------------------------------------
    lk.logd('拼音表 (扩展集) + 韦氏拼音表 (扩展集)')
    
    # 拼音表(扩展集)+韦氏拼音表(扩展集).txt
    generate_plain_file(
        ifile1, ifile2, ifile3, ifile4,
        ofile='../拼音表(扩展集)+韦氏拼音表(扩展集).txt'
    )
    
    # 拼音表(扩展集)+韦氏拼音表(扩展集)_前缀树.json
    generate_trie_file(
        ifile1, ifile2, ifile3, ifile4,
        ofile='../拼音表(扩展集)+韦氏拼音表(扩展集)_前缀树.json'
    )
    
    # 拼音表(扩展集)+韦氏拼音表(扩展集)_后缀树.json
    generate_postrie_file(
        ifile1, ifile2, ifile3, ifile4,
        ofile='../拼音表(扩展集)+韦氏拼音表(扩展集)_后缀树.json'
    )


# ------------------------------------------------

def generate_plain_file(*ifiles, ofile, check_duplicate=False):
    if len(ifiles) == 1:
        copyfile(ifiles[0], ofile)
        lk.loga('file saved', ofile)
        return
    
    data_sum = []
    for f in ifiles:
        data = read_and_write.read_lines(f)
        for d in data:
            if d in data_sum:
                if check_duplicate:
                    lk.logt('[W5316]', d, f, h='parent')
            else:
                data_sum.append(d)
    data_sum.sort()
    read_and_write.write_file(data_sum, ofile)
    lk.loga('file saved', ofile)


trie = Trie()


def generate_trie_file(*ifiles, ofile, check_duplicate=False):
    if len(ifiles) == 1:
        words = read_and_write.read_lines(ifiles[0])
        trie.add_list(words)
    else:
        words_sum = []
        for f in ifiles:
            words = read_and_write.read_lines(f)
            for w in words:
                if w in words_sum:
                    if check_duplicate:
                        lk.logt('[W5317]', w, f, h='parent')
                else:
                    words_sum.append(w)
        words_sum.sort()
        trie.add_list(words_sum)
    trie.save(ofile)
    trie.clear()
    lk.loga('file saved', ofile)


def generate_postrie_file(*ifiles, ofile, check_duplicate=False):
    if len(ifiles) == 1:
        words = read_and_write.read_lines(ifiles[0])
        nwords = [x[::-1] for x in words]  # 反转字符串. 'ABC' -> 'CBA'
        trie.add_list(nwords)
    else:
        words_sum = []
        for f in ifiles:
            words = read_and_write.read_lines(f)
            for w in words:
                w = w[::-1]
                if w in words_sum:
                    if check_duplicate:
                        lk.logt('[W5318]', w, f, h='parent')
                else:
                    words_sum.append(w)
        words_sum.sort()
        trie.add_list(words_sum)
    trie.save(ofile)
    trie.clear()
    lk.loga('file saved', ofile)


# ------------------------------------------------

if __name__ == '__main__':
    main()
    lk.print_important_msg(False)
    lk.over()

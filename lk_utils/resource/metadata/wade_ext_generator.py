from lk_utils import read_and_write


def main():
    """
    预测韦氏所有声韵母组合.
    IN: more/韦氏拼音表_{声母,韵母,零声母}.txt
    OT: 非标准韦氏拼音表.txt
            注意: 生成的文件中含有大量的不可靠韦氏拼音, 有些是形而似的, 有些甚至
            毫无逻辑, 可能对英文单词形成干扰. 请谨慎使用.
            请在脚本生成此文件后, 对此文件进行人工清理.
            之后不建议再通过本脚本生成. 以后的维护工作全部转到 "非标准韦氏拼音表
            .txt" 本身由人工维护.
    """
    initials = read_and_write.read_lines('more/韦氏拼音表_声母.txt')
    finals = read_and_write.read_lines('more/韦氏拼音表_韵母.txt')
    aoe = read_and_write.read_lines('more/韦氏拼音表_零声母.txt')
    
    combo = []
    for i in initials:
        for j in finals:
            combo.append(i + j)
    
    combo.extend(aoe)
    combo = list(set(combo))
    
    # extra (customs)
    combo.extend([
        'xean'
    ])
    
    combo.sort()
    read_and_write.write_file(combo, '非标准韦氏拼音表.txt')


if __name__ == '__main__':
    main()

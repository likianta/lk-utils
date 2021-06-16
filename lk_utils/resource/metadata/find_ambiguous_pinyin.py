from lk_utils import read_and_write


def main():
    """
    通过大量的样本来预测可能的 "模棱两可" 的拼音的特征.
    """
    i_file = 'train_in.txt'
    o_file = 'train_out.txt'
    
    aoe = ("a", "ai", "an", "ang", "ao",
           "o", "ou",
           "e", "ei", "en", "eng", "er")
    
    r = read_and_write.read_lines(i_file)
    w = []
    
    for i in r:
        for j in aoe:
            if i.endswith(j) and i.rsplit(j, 1)[0] in r:
                w.append(f'{i}\t{i[:-1 * len(j)]}\t{j}')
                break
    
    read_and_write.write_file(w, o_file)


if __name__ == '__main__':
    main()

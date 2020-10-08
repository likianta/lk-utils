from lk_utils import read_and_write


def main():
    """
    通过大量的样本来预测可能的 "模棱两可" 的拼音的特征.
    """
    ifile = 'train_in.txt'
    ofile = 'train_out.txt'
    
    aoe = ("a", "ai", "an", "ang", "ao",
           "o", "ou",
           "e", "ei", "en", "eng", "er")
    
    r = read_and_write.read_file_by_line(ifile)
    w = []
    
    for i in r:
        for j in aoe:
            if i.endswith(j) and i.rsplit(j, 1)[0] in r:
                w.append(f'{i}\t{i[:-1 * len(j)]}\t{j}')
                break
    
    read_and_write.write_file(w, ofile)


if __name__ == '__main__':
    main()

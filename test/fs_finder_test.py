from lk_utils import fs


def test_260126():
    for d in fs.findall_dirs('lk_utils'):
        print(':i', d.relpath)
    for f in fs.findall_files('lk_utils'):
        print(':i', f.relpath)


if __name__ == '__main__':
    # pox test/fs_finder_test.py
    # py38 test/fs_finder_test.py
    test_260126()

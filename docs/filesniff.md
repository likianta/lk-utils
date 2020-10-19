# 使用演示

## 获取目录下所有文件

```python
from lk_utils import filesniff

"""
D:/Demo
|- A
    |- a001.txt
    |- a002.txt
    |- a003.txt
|- B
    |- B1
        |- b101.png
    |- B2
        |- b201.png
    |- B3
        |- b301.png
"""

rdir = 'D:/Demo'

# list filepaths
filepaths = filesniff.find_files(f'{rdir}/A')
#   -> ['D:/Demo/A/a001.txt', 'D:/Demo/A/a002.txt', 'D:/Demo/A/a003.txt']

# list filenames
filenames = filesniff.find_files(f'{rdir}/A', 'filename')
#   or: filenames = filesniff.find_filenames(f'{rdir}/A')
#   -> ['a001.txt', 'a002.txt', 'a003.txt']

# list filenames without extensions
filenames = filesniff.find_files(f'{rdir}/A', 'filename')


```

# LK Utils

lk-utils is a set of utility wrappers to make data processing more simple and fluent.

# Install

```shell
pip install lk-utils
```

the default pip install doesn't include extra dependencies. to get extra support for excel or nlp processing, pip install this:

```shell
pip install lk-utils  # to add lk-logger (required dependency)
pip install lk-utils[exl]  # to add lk-logger, xlrd, xlsxwriter
pip install lk-utils[nlp]  # to add lk-logger, pypinyin
pip install lk-utils[all]  # to add all of the above
```

lk-utils requires Python 3.8 or higher version.

# Usage

## subproc

### new thread decorator

```python
from lk_utils.subproc import new_thread

@new_thread(daemon=True, singleton=False)
def background_loop():
    from time import sleep
    i = 0
    while i < 10:
        i += 1
        print(i)
        sleep(1)

x = background_loop()
print(type(x))  # -> threading.Thread
```

### run in new thread

```python
from lk_utils.subproc import run_new_thread

def background_loop():
    from time import sleep
    i = 0
    while i < 10:
        i += 1
        print(i)
        sleep(1)

x = run_new_thread(background_loop, args=None, kwargs=None, daemon=True)
print(type(x))  # -> threading.Thread
```

### run cmd args

```python
from lk_utils.subproc import run_cmd_shell, run_cmd_args
run_cmd_shell('python -m pip list')
run_cmd_args('python', '-m', 'pip', 'list')
```

### mklink, mklinks

```python
"""
example structure:
    |= from_dir
       |= folder_xxx
       |- file_xxx.txt
    |= to_dir_1    # empty
    |= to_dir_2    # not empty
       |- ...
"""

from lk_utils.subproc import mklink, mklinks
mklink('/from_dir', '/to_dir_1')
mklinks('/from_dir', '/to_dir_2')

"""
result:
    |= from_dir
       |= folder_xxx
       |- file_xxx.txt
    |= to_dir_1         # this is a symlink
    |= to_dir_2
       |- ...
       |= folder_xxx    # this is a symlink
       |- file_xxx.txt  # this is a symlink
"""
```

## filesniff

### get current dir, get relative path

```python
import os
from lk_utils import filesniff as fs
print(fs.currdir()
      == os.path.dirname(__file__)).replace('\\', '/'))  # -> True
print(fs.relpath('..')
      == os.path.dirname(fs.currdir()))  # -> True
```

### list files/dirs

```python
from lk_utils import filesniff as fs

for path, name in fs.find_files('.'):  # this is an generator.
    print(path, name)
    #   the first element is the **abspath**, the second is path's
    #   basename (<- os.path.basename(path))

for path in fs.find_file_paths('.'):  # this is a list[str]
    print(path)

for name in fs.find_file_names('.'):  # this is a list[str]
    print(name)

# more:
#   fs.findall_files
#   fs.findall_file_paths
#   fs.findall_file_names
#
#   fs.find_dirs
#   fs.find_dir_paths
#   fs.find_dir_names
#
#   fs.findall_dirs
#   fs.findall_dir_paths
#   fs.findall_dir_names
```

## read_and_write

### loads and dumps

```python
from lk_utils import read_and_write as rw

data_r = rw.loads(file_i)
#   it recognizes json, yaml, pkl as sturctured data. others are treated as
#   plain text.

data_w = ...
rw.dumps(data_w, file_o)
#   it recognizes json, yaml, pkl as sturctured data. others are treated as
#   plain text.
```

---

<font color="red">below are marked as deprecated.</font>

## excel

### excel reader and writer

```python
from lk_utils import excel as exl

reader = exl.ExcelReader(file_i)
#   accepts '.xls' and '.xlsx' files.
...  # TODO:CompleteExample

writer = exl.ExcelWriter(file_o)
#   accepts only '.xlsx' files.
...  # TODO:CompleteExample
writer.save()

```

## nlp

*TODO*

# LK Utils

[中文版](./README.zh.md)

lk-utils is a set of utilities to make data processing more simple and fluent.

# Install

```shell
pip install lk-utils
```

lk-utils requires python 3.8 or higher version.

# Usage

## subproc

### new thread decorator

```python
from lk_utils import new_thread


def main(files: list[str]) -> None:
    for f in files:
        handle_file(f)


@new_thread()
def handle_file(file: str) -> None:
    # do something
    ...
```

### fetch results from threads

```python
from lk_utils import new_thread


def main(files: list[str]) -> None:
    pool = []
    for f in files:
        thread = handle_file(f)
        pool.append(thread)
    
    ...
    
    for thread in pool:
        result = thread.join()
        print(result)


@new_thread()
def handle_file(file: str) -> str:
    # do something
    ...
```

### run cmd args

```python
from lk_utils import run_cmd_args
from lk_utils import run_cmd_shell
run_cmd_args('python', '-m', 'pip', 'list')
run_cmd_shell('python -m pip list')
```

advanced filter:

```python
from lk_utils import run_cmd_args


def pip_install(
        dest: str, 
        url_index: str = None
) -> None:
    run_cmd_args(
        ('python', '-m', 'pip'),
        ('install', '-r', 'requirements.txt'),
        ('-t', dest),
        ('-i', url_index),
    )
```

### mklink, mklinks

```python
from lk_utils import mklink, mklinks
mklink('/from_dir', '/to_dir_1')
mklinks('/from_dir', '/to_dir_2')
```

## filesniff

### get current dir, get relative path

```python
import os
from lk_utils import filesniff as fs
print(fs.currdir() == os.path.dirname(__file__).replace('\\', '/'))  # -> True
print(fs.relpath('..') == os.path.dirname(fs.currdir()))  # -> True
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

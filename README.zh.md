# LK Utils

lk-utils 是对一系列数据处理操作的封装, 方便做文件读写, 路径查找, 线程和进程管理等操作.

## 读取文件

支持一些常见的文件格式: csv, json, pickle, toml, txt, yaml.

lk-utils 使用 `lk_utils.load` 作为统一的调用接口. 其基本形式为:

```python
# lk_utils/io.py
def load(file: str, type: str = 'auto', **kwargs):
    ...
```

第一个参数 `file` 传有效的文件路径, 该文件可以是上述支持的类型中的任一种.

第二个参数 `type` 用来判断文件属于什么类型, 默认为根据后缀名自动判断; 你也可以指定其为一个类型, 示例见下.

### 读取 TXT 文件

```python
from lk_utils import load
data = load('test.txt')
print(data)  # e.g. 'aaa\nbbb\nccc'
```

### 读取 CSV 文件

```python
from lk_utils import load
data = load('test.csv')
print(data)
#   e.g.
#       [
#           ['aaa', '123'],
#           ['bbb', '456'],
#           ['ccc', '789'],
#       ]
```

注意事项:

- 所有单元格的值的类型都是 str, 不存在其他类型
- 要读取的文件路径必须以 ".csv" 结尾

### 读取 Excel 文件

支持读取一个或全部 sheet.

如读取一个 sheet, 可以根据 sheet 序号或者 sheet 名称获取.

```python
from lk_utils import load

# get one sheet by sheet number
data = load('test.xlsx', sheet=0)
#   sheet: int | str. if int, the number starts from 0.
#   returns: 
#       [row, ...]
#           row: [value, ...]
#               value: bool | int | float | str

# get one sheet by sheet name
data = load('test.xlsx', sheet='Sheet 1')
#   be noticed the name is case sensitive.

# get all sheets
data = load('test.xlsx')
# -> {sheet_name: [row, ...], ...}
```

注意事项:

- 要读取的文件路径必须以 ".xlsx" 或者 ".xls" 结尾

- 以 sheet 名称获取 sheet 数据时, 名称字母大小写敏感

- 以 sheet 序号获取 sheet 数据时, 序号从 0 开始数

- 如果表格中, 有一列数据既有 float 类型, 又有 int 类型 (例如 "3.14", "2.00", "1.68", ...), 则会得到 int 和 float 混杂的结果; 如果你希望全部以 float 类型表示, 则这样做:

  ```python
  from lk_utils import load
  data = load('test.xlsx', prefer_int_not_float=False)
  print(data)
  #   e.g. [..., [3.14, 2.00, 1.68, ...], ...]
  ```

### 指定文件以什么类型来读取

假设我们有一个 "test.txt" 文件, 其内容实际为 csv 的格式.

我们想要用 csv 格式读取该文件数据.

```python
from lk_utils import load
data = load('test.txt', type='table')
```

完整的类型值如下:

| 类型   | 说明                                 |
| ------ | ------------------------------------ |
| auto   | 根据文件后缀自动识别 (默认)          |
| binary | 以二进制格式读取                     |
| excel  | 读取 ".xlsx" ".xls" 文件             |
| json   | 读取 json 格式, 如 ".json", ".json5" |
| pickle | 读取 ".pkl" 文件                     |
| plain  | 按纯文本来读取, 即视作 ".txt" 文件   |
| table  | 读取 ".csv" 文件                     |
| toml   | 读取 ".toml" 文件                    |
| yaml   | 读取 ".yaml" ".yml" 文件             |

对于自动识别, 常见的判断结果由 `lk_utils/io.py : def _detect_file_type` 完成:

| 类型   | 常见后缀                                           |
| ------ | -------------------------------------------------- |
| binary | .bin .exe .mp3 .mp4 .jpeg .jpg .png .raw .webp ... |
| excel  | .xls .xlsx                                         |
| json   | .json .json5                                       |
| pickle | .pkl                                               |
| plain  | .htm .html .md .rst .svg .txt                      |
| table  | .csv                                               |
| toml   | .tml .toml                                         |
| yaml   | .yaml .yml                                         |

### 读取文件, 如果文件不存在, 则以默认数据创建该文件

```python
from lk_utils import load
data = load('test.json', default={'hello': 'world'})
print(data)  # -> {'hello': 'world'}
```

## 写入文件

### 写入数据到 TXT 文件

...

### 写入数据到 JSON 文件

```python
from lk_utils import dump
dump({'aaa': 123}, 'result.json')
```

支持写入的类型: 任何可被序列化的数据. 一般为 dict 或 list.

此外, list-like 的类型也是支持的, 例如 tuple, set.

### 写入数据到 YAML 文件

```python
from lk_utils import dump
dump({'aaa': 123}, 'result.yaml')
```

### 写入数据到 TOML 文件

```python
from lk_utils import dump
dump({'aaa': 123}, 'result.toml')
```

注意: python 3.10 及以下的版本没有内置 toml 标准库, 需要 `pip install toml`.

### 写入数据到 CSV 文件

```python
from lk_utils import dump
# data type: iterable[iterable[str|int|float|bool, ...], ...]
dump(
    [
        ('name', 'value'),
        ('aaa', 123),
        ('bbb', 456),
        ('ccc', 789),
    ], 
    'result.csv'
)
```

### 写入 Excel (单个 Sheet)

注意: excel 读写需要安装扩展库: `pip install lk-utils[exl]`.

```python
from lk_utils import dump
# dump(data, file)
#   data: (row, ...)
#       row: (value, ...)
#           value: bool | int | float | str
#   file: path that ends with '.xlsx'
dump(
    [
        ('name', 'value'),
        ('aaa', 123),
        ('bbb', 456),
        ('ccc', 789),
    ],
    'result.xlsx'
)
```

### 写入 Excel (多个 Sheet)

注意: excel 读写需要安装扩展库: `pip install lk-utils[exl]`.

```python
from lk_utils import dump
# dump(data, file)
#   data: {sheet_name: (row, ...), ...}
#       row: (value, ...)
#           value: bool | int | float | str
#   file: path that ends with '.xlsx'
dump(
    {
        'sheet 1': [
            ('index', 'name', 'value'),
            (0, 'alpha', '123'),
            (1, 'beta', 456),
            (2, 'gamma', True),
        ],
        'sheet 2': [
            ('name', 'code'),
            ('aaa', 123),
            ('bbb', 456),
            ('ccc', 789),
        ],
    },
    'result.xlsx'
)
```

## 线程和子进程

### 子进程的输出结果返回给主进程

```python
from lk_utils import run_cmd_args
msg = run_cmd_args('python', '--version')
print(msg)  # -> 'Python 3.12.0'
```

### 子进程输出打印到控制台

```python
# --- aaa.py
import sys
from lk_utils import run_cmd_args
msg = run_cmd_args(sys.executable, 'bbb.py', verbose=True)

# --- bbb.py
print('hello world')
```

### 子进程输出的打印带颜色显示

```python
# --- aaa.py
import sys
from lk_utils import run_cmd_args
run_cmd_args(sys.executable, 'bbb.py', verbose=True, force_term_color=True)
#   verbose=True: show prints from subprocess.
#   force_term_color=True: render the prints with ascii color if possible.

# --- bbb.py
import lk_logger
lk_logger.setup()
print(':r', '[green]hello[/] [red]world[/]')
```

注意: 启用 force_term_color 可能导致旧的 windows 控制台输出 "乱码". 如果第三方程序中启用了 force_term_color, 而你不方便去修改他人的代码, 可以通过设置环境变量 `os.environ['LK_LOGGER_MODERN_WINDOW'] = '0'` 来全局禁用颜色输出.

### 以非阻塞的方式运行子进程

阻塞与否通过 `run_cmd_args(..., blocking: bool)` 来控制. 默认是阻塞的.

当设置 `blocking=False`, `run_cmd_args` 会返回一个 `lk_utils.subproc.Popen` 对象. 通过该对象可以查询它的状态, 强制杀死子进程等操作.

```python
import sys
from lk_utils import run_cmd_args

task = run_cmd_args(sys.executable, 'long_lived_task.py', blocking=False)

# continue your work
...

# fetch task status
...
```

## 简易协程 (coroutine)

...


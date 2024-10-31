# LK Utils

lk-utils 是对一系列数据处理操作的封装, 方便做文件读写, 路径查找, 线程和进程管理等操作.

## 读取文件

支持一些常见的文件格式: csv, json, pickle, toml, txt, yaml.

...

### 读取文件, 如果文件不存在, 则创建该文件, 并写入初始化的数据

```python
from lk_utils import load
data = load('an_inexsitent_file.json', default={'hello': 'world'})
print(data)  # -> {'hello': 'world'}
```

## 写入文件

...

## 线程 (threading)

...

## 子进程 (subprocess)

打印进程的输出到控制台.

...

## 简易协程 (coroutine)

...


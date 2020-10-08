# 说明

lk_logger 是一个日志打印模块. 其亮点在于:

1. 可打印代码所在的源码位置
2. 可打印出变量名
3. 支持打印计数
4. 支持打印计时
5. 支持打印信息收集, 分析和导出
6. 可自定义回溯层级



# 使用方法

## 基本使用方法

```python
from lk_utils.lk_logger import lk
x = [1, 2, 3]
lk.loga(x)
```

lk 在打印时, 会将变量名及所在的源码行一同打印出来. 在 Pycharm 中, 源码行会被识别为蓝色的链接, 点击即可跳转到源码所在的位置.

## 内置打印方式

```python
from lk_utils.lk_logger import lk

x = [1, 2, 3]

lk.log(x)  # 普通打印, 不打印变量名.
lk.loga(x)  # 高级打印, 打印时带有变量名.
lk.logd(x)  # 分割线样式打印, 可自定义分割线风格.
lk.logt('[DEBUG]', x)  # TAG 样式打印, 注意 TAG 必须在首位其用中括号包裹.
lk.logdt('[DEBUG]', x)  # 带有 TAG 功能的分割线样式打印.

lk.logx(x)  # 带有计数功能的普通打印, 不打印变量名.
lk.logax(x)  # 带有计数功能的高级打印, 打印时带有变量名.
lk.logdx(x)  # 带有计数功能的分割线样式打印, 可自定义分割线风格.
lk.logtx('[DEBUG]', x)  # 带有计数功能的 TAG 样式打印.
lk.logdtx('[DEBUG]', x)  # 带有计数和 TAG 功能的分割线样式打印.

```

## 计数功能的使用

```python
from lk_utils.lk_logger import lk
for i in [1, 2, 3]:
    lk.logax(i)
```

上述计数方式会在不同循环体中累积计数, 如果想在不同循环体中分别计数, 则使用下面的方法:

方法 1:

```python
from lk_utils.lk_logger import lk
for i in [1, 2, 3]:
    lk.logax(i)

lk.init_count()
for i in [4, 5, 6]:
    lk.logax(i)

```

方法 2:

```python
from lk_utils.lk_logger import lk
for i in lk.count([1, 2, 3]):
    lk.logax(i)

for i in lk.count([4, 5, 6]):
    lk.logax(i)

```

此外还有 `lk.enum()` 计数方法可供选择:

```python
from lk_utils.lk_logger import lk

for index, num in lk.enum([1, 2, 3]):
    lk.logax(num)

# 此法相当于
#   for index, num in enumerate(lk.count([1, 2, 3])):
#       lk.logax(num)
```

## 统计日志

```python
from lk_utils.lk_logger import lk

lk.loga('hello')
lk.logt('[INFO]', 'succeed')

lk.print_important_msg()  # 统计 TAG 信息.
lk.over()  # 计算结束时间.
```

## 调整源码反射层级

通过调整 h 参数的层级, 有利于追踪到我们想要的父级调用者所在的源码行.

```python
from lk_utils.lk_logger import lk

def foo(a, b):
    c = a + b
    lk.loga(c, h='parent')
    return c

foo(1, 2)
foo(4, 2)

```

在该示例中, 我们通过 `lk.loga()` 的 h 参数调整它的反射层级为父级. 这样, 当此处代码被执行时, lk 打印的源码行就不是第 5 行, 而是它的调用者所在的行 (8, 9 行).

该方法的使用场景是, 我们不关注 lk 打印时所在的函数, 而关注是谁调用了这个函数. 例如, `lk_utils.excel_writer.ExcelWriter.save()` 方法是这样的:

```python
from lk_utils.lk_logger import lk

class ExcelWriter:
    
    ...

    def save(self):
        lk.logt('[ExcelWriter][I1139]', f'Excel saved to "{self.filepath}"',
                h='parent')
        self.book.close()
    
```

该信息打印的是 `save` 的调用者的源码行, 因为我们不关注 `ExcelWriter.save()` 方法内部做了什么, 而是想知道是谁调用了这个保存动作.

h 参数可用的值如下:

- 'self' (或者数字 3) (这是缺省值)
- 'parent' (或者数字 4)
- 'grand_parent' (或者数字 5)
- 'great_grand_parent' (或者数字 6)
- 更高的层级, 只能填数字: 7, 8, 9, ...



# 其他说明

## 关闭 lk_logger 的打印

```python
from lk_utils.lk_logger import lk
lk.log_enable = False
```

该方法只是停止了 lk 向控制台输出打印日志, 但内部的流程仍在运转, 不影响 `lk.init_count()`, `lk.over()` 等操作.



# 注意事项

1. 由于 lk_logger 运用了栈帧查找和调用反射, 因此大量使用 lk_logger 模块会显著拖慢程序处理速度 (相较于 print 而言)
2. 高级打印方法在处理句内海象运算符 (e.g. `lk.loga((x := 'name'))`) 和百分号连接的格式化字符串会不准确 (指变量名显示不完全, 值可以全部显示, 不会引起报错), 将在 1.4+ 版本中尽快修复
3. 高级打印方法在折行的情况下无法打印变量名
   e.g.
   ```python
   from lk_utils.lk_logger import lk
   a, b, c = 1, 2, 3
   lk.loga(a, 
           b, 
           c) 
   ```
4. 在循环嵌套中, lk_logger 无法分别对不同循环体分配计数

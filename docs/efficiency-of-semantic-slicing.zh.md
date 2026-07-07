# 语义分割字符串效率演示

假设我们要提取 pyproject.toml 文件中的 `dependencies = [...]` 中列出的每个依赖及其版本.

传统的方法之一是用 flag 来标记指针每次移动时的状态:

```python
flag = 'START'
with open('pyproject.toml', 'r') as f:
    for i, line in enumerate(f.readlines()):
        try:
            if flag == 'START':
                if line.startswith('dependencies'):
                    flag = 'DEPENDENCIES'
                continue
            if flag == 'DEPENDENCIES':
                if line.startswith(']'):
                    flag = 'END'
                    break
                elif line.lstrip().startswith('#'):
                    continue
                else:
                    m = re.fullmatch(r' {4}"(.+)",(?: +#.+)?', line)
                    print(i, m.group(1))
        except Exception as e:
            e.add_note(
                str(
                    {
                        'file': self._file,
                        'line_number': i + 1,
                        'line_content': line,
                    }
                )
            )
            raise
assert flag == 'END'
```

使用 `lk_utils.regex.SemanticSlicer` 可以减少代码, 并降低复杂性. 我们先整块提取想要的部位, 然后再细细切割:

```python
from lk_utils import regex as re
with open('pyproject.toml', 'r') as f:
    text = f.read()
body = (
    re.SemanticSlicer(text)
    .find('dependencies = [').end().cut()
    .find(']').cut()
    .slice()
)
lines = (x.lstrip() for x in body.splitlines())
for i, line in enumerate(lines):
    if not line.startswith('#'):
        print(i, line)
```


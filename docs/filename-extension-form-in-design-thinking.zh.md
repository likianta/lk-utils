# 关于 `fs` 模块中的文件扩展名的格式规范

- 使用 "extension" 表示文件扩展名, "ext" 作为简写.

- 扩展名中的点号和星号是可选的

    例如:

    - 支持: "png", "jpg"
    - 同样支持: ".png", ".jpg"
    - 同样支持: "*.png", "*.jpg"

    如果不确定使用哪种风格, 推荐第一种.

- 当多个扩展名出现时, 有两种表达方式:

    - 元组: `("png", "jpg")`
    - 空格: `"png jpg"` (以一或多个空格分隔)

    注: 同样支持点号和星号.

- 不区分大小写, 推荐使用全小写.

## 为什么这样设计

风格一致性:

```py
dir, stem, ext = fs.split(some_file)
#   'aaa/bbb.txt' -> ('aaa', 'bbb', 'txt')
stem, ext = fs.split_name(some_file)
#   'aaa/bbb.txt' -> ('bbb', 'txt')
```

显式的标点增加可读性:

```py
# bad
print('{}{}-alt{}'.format(dir, stem, ext))

# good (1)
print('{}/{}-alt.{}'.format(dir, stem, ext))
#        ^      ^

# good (2)
print('{dir}/{name}-alt.{ext}'.format(dir=dir, name=stem, ext=ext))
#           ^          ^
```

```py
# bad
for f in fs.find_files(some_dir):
    print(f.dir)  # -> 'aaa/'
    print(f.ext)  # -> '.txt'
    new_file = '{}new{}'.format(f.dir, f.ext)

# good
for f in fs.find_files(some_dir):
    print(f.dir)  # -> 'aaa'
    print(f.ext)  # -> 'txt'
    new_file = '{}/new.{}'.format(f.dir, f.ext)
```

什么时候适用加点号或者星号? -- 当作为入参时使用:

```py
# good
for f in fs.find_files(some_dir, 'txt'): ...
#                                 ^^^

# better (1)
for f in fs.find_files(some_dir, '.txt'): ...
#                                 ^^^^

# better (2)
for f in fs.find_files(some_dir, '*.txt'): ...
#                                 ^^^^^
```

```py
# good
new_name = fs.replace_ext(some_file, 'jpg')
#                                     ^^^

# better
new_name = fs.replace_ext(some_file, '.jpg')
#                                     ^^^^
```

此外, 这种写法符合 "显式标点优先" 的规则.

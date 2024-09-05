# 更新日志

### 2.10.9 (wip)

- 向 `run_cmd_args` 传递环境变量
- 修复 `subproc` 模块的一些问题

### 2.10.8 (2024-08-04)

- 新增 `time_utils.pretty_time` 函数
- 更好地控制子进程在终端的高亮打印效果

### 2.10.7 (2024-07-18)

- 优化 `Popen` 退出逻辑
- 提高 `subprocess` 稳定性

### 2.10.6 (2024-07-11)

- 更好的 `isfile` `isdir` 判断
- 优化 `finder` 默认的过滤器

### 2.10.5 (2024-07-06)

- 优化 subprocess 打印效果

### 2.10.4 (2024-07-01)

- 修复 signal 递归检查

### 2.10.3 (2024-06-29)

- 对 `fs` 模块的一些调整和修复

### 2.10.2 (2024-06-23)

- 新增进度条模块 `progress`
- 对 `fs` 的一些优化和修复

### 2.10.1 (2024-05-29)

- 新增 `fs.make_shortcut` 创建快捷方式

### 2.10.0 (2024-05-10)

- 重构并简化 io 模块
- load/dump 函数支持 csv 读写
- 新增 `importer` 模块

### 2.9.5 (2024-04-23)

- 修复 path filter 并使其私有化

### 2.9.4 (2024-04-08)

- 修复 signal 对重名函数的识别
- 优化 signal 递归警告

### 2.9.3 (2024-03-07)

- 修复 `typing.Self` 相关报错

### 2.9.2 (2024-03-04)

- 修复 timeit 的 with 语法形式

### 2.9.1 (2024-02-19)

- 修复 signal 形式和逻辑

### 2.9.0 (2024-01-30)

- 新增一系列 "binding" 装饰器
- 新增 `timeit` 计时器

### 2.8.1 (2024-01-19)

- 优化 `textwrap:dedent` 对转义字符的处理

### 2.8.0 (2023-12-29)

- 新增 `common_typing` 模块

### 2.7.3 (2023-12-27)

- 修复 `subproc.compose_cmd` 边缘问题

### 2.7.2 (2023-11-02)

- 增强 `run_cmd_args`

### 2.7.1 (2023-10-30)

- 新增 `fs.make_file`

### 2.7.0 (2023-10-07)

- 重构 `filesniff.finder` 模块
- 规范文件后缀名格式
- 更新 `textwrap`, `filesniff`, `subprocess` 等模块

### 2.6.1 (2023-08-18)

- 微调 "overwrite" 逻辑

### 2.6.0 (2023-08-15)

- 新增 `textwrap` 模块
- 优化 `subproc` 模块

### 2.5.6 (2023-06-13)

- 细节修复和更新
- 新增 `fs.split`
- `subproc` 新增 `shell` 参数

### 2.5.5 (2023-03-03)

- 优化 `subproc` 模块

### 2.5.4 (2023-02-21)

- 捕获线程错误
- 修复 fs 的 overwrite 策略

### 2.5.3 (2022-12-15)

- 特定条件下可被打断的线程
- 更新 `time_utils` 模块

### 2.5.2 (2022-12-07)

- 增强线程可复用性

### 2.5.1 (2022-11-25)

- 一些细微调整和优化

### 2.5.0 (2022-11-12)

- 重构 subproc 模块
- 更新 filesniff 模块
    - 注意: `filesniff.relpath` 变更为 `filesniff.xpath`
- 允许用户指定 loads/dumps 时的文件类型

### 2.4.1 (2022-10-18)

- 修复 filesniff.finder 相关的严重错误

### 2.4.0 (2022-10-08)

- 重构 filesniff 模块
- 移除之前声明已废弃的模块

### 2.3.2 (2022-08-31)

- *次要更新*
    - 修复: python 3.8 适配问题

### 2.3.1 (2022-08-08)

- *次要更新*
    - 更新 (filesniff): 一些功能更新和优化

### 2.3.0 (2022-07-26)

- **重要更新**
    - 更新 (subproc): 扩展 `subproc` 功能

### 2.2.1 (2022-03-28)

- *次要更新*
    - 新增 (read_and_write): loads, dumps 支持 toml 格式

### 2.2.0 (2022-03-23)

- **重要更新**
    - 变更 (filesniff): 修改了文件查找的方法, 根据实际使用情况做了功能削减
    - 变更: excel, nlp 相关的模块标记为即将弃用
- *次要更新*
    - 变更: 移除了一些不再维护的模块 (easy_launcher, lk_browser)
    - 优化 (excel): 简化了 `ExcelReader` 的 header 的使用方式
    - 优化 (excel): 调整 `ExcelWriter` 的 save 方法

### 2.1.4 (2022-03-11)

- **重要更新**
    - 更新 (subproc): 调整和优化 `new_thread`, `run_new_thread`

### 2.1.3 (2022-02-11)

- **重要更新**
    - 变更 (subproc): 线程装饰器默认以守护进程运行

### 2.1.2 (2021-12-16)

- *次要更新*
    - 优化 (subproc): `format_cmd` 对 args 和 kwargs 的处理方式
    - 修复 (filesniff): `relpath` 同样有与之前 `currdir` 类似的 bug

### 2.1.1 (2021-12-16)

- *次要更新*
  - 修复 (filesniff): 增强 `currdir()` 获取目录方式的稳定性
  - 更新 (filesniff): 当 `currdir()` 获取失败时予以警告

### 2.1.0 (2021-12-15)

- **重要更新**
    - 新增 (filesniff): `currdir()` 函数获取 caller 所在的目录
- *次要更新*
    - 变更 (filesniff): 优化和调整一些函数
    - 移除 (filesniff): 不常用的函数 (dialog, mkdirs)
    - 优化: 使用局部类型提示取代独立的类型提示包
    - 变更: 将 lk_browser 模块标记为已过时
    - 变更: 调整 time_utils 部分函数命名
    - 优化: read_and_write 写入文本文件时, 仅在末尾无换行符时添加换行符

### 2.0.0 (2021-06-17)

- *次要更新*
    - 优化: 补全类型提示
    - 新增: 并发的封装模块
    - 优化 (filesniff): 整合格式化路径的方法
    - 变更 (filesniff): `find*` 相关函数的 `fmt`, `suffix` 参数仅限关键字形参传入
    - 修复 (filesniff): `find(all)_dirs` 对要排除的路径的漏判
    - 移除 (filesniff): `lkdb` 相关的方法
    - 新增 (excel_writer): 集成 sheet 管理
    - 新增 (excel_writer): 单元格格式添加
    - 修复 (excel_writer): ExcelWriter 激活 sheet
    - 移除: 一部分已弃用的模块: toolbox.py, file_combinator.py, lk_config.py
    - 新增 (read_and_write): `loads`, `dumps` 支持 pickle 格式

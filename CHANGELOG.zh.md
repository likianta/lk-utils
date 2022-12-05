# 更新日志

### 2.5.2 (wip)

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

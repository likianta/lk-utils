### 2.1.3 | 2022-02-11

重要更新:

- 变更: `subproc` 线程默认以守护进程运行

### 2.1.2 | 2021-12-16

次要更新:

- 优化: subproc.format_cmd 对 args 和 kwargs 的处理方式
- 修复: filesniff.relpath 同样有与之前 currdir 类似的 bug

### 2.1.1 | 2021-12-16

次要更新:

- [filesniff]
  - 修复: 增强 currdir() 获取目录方式的稳定性
  - 更新: 当 currdir() 获取失败时予以警告

### 2.1.0 | 2021-12-15

重要更新:

- [filesniff]
  - 新增: currdir 函数

次要更新:

- [filesniff]    
  - 变更: 优化和调整一些函数
  - 移除: 不常用的函数 (dialog, mkdirs)
- 变更: 使用局部类型提示取代独立的类型提示包
- 变更: 将 lk_browser 标记为已过时
- 变更: 调整 time_utils 部分函数命名
- 优化: read_and_write 写入文本文件时, 仅在末尾无换行符时添加换行符

### 2.0.0 | 2021-06-17

重要更新:

- 优化: 类型提示
- 新增: concurrency.py
- [read_and_write]
  - 变更: 部分函数名
- [filesniff]
  - 变更: 格式化路径函数整合为 `normpath`
  - 变更: `find*` 相关函数的 `fmt`, `suffix` 参数仅限关键字形参传入
- [excel_writer]
  - 新增: 集成 sheet 管理

次要更新:

- 移除: 已弃用的模块
  - 移除: toolbox.py
  - 移除: file_combinator.py
  - 移除: lk_config.py
- 优化: `__init__` 导入
- [read_and_write]
  - 新增: `loads`, `dumps` 支持 pickle 格式
- [filesniff]
  - 移除: lkdb 相关方法
  - 修复: find(all)_dirs 对要排除的路径的漏判
- [excel_writer]
  - 优化: 简化 `ExcelWriter.__init__:params:options` 的传值方式
  - 新增: 单元格格式添加
  - 修复: `ExcelWriter.activate_sheet`

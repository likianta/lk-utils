### 2.1.0 | 2021-12-15

- filesniff
    - 新增: currdir 函数
    - 变更: 优化和调整一些函数
    - 移除: 不常用的函数 (dialog, mkdirs)
- 变更: 使用局部类型提示取代独立的类型提示包
- 变更: 将 lk_browser 标记为已过时
- 变更: 调整 time_utils 部分函数命名
- 优化: read_and_write 写入文本文件时, 仅在末尾无换行符时添加换行符

### 2.0.0 | 2021-06-17

- 移除: 已弃用的模块
- 移除: toolbox.py
- 优化: `__init__.py` 导入
- 优化: 类型提示
- 移除: file_combinator.py
- 移除: lk_config.py
- 新增: concurrency.py

**read_and_write.py**

- 新增: `loads`, `dumps` 支持 pickle 格式
- 变更: 部分函数名

**filesniff.py**

- 变更: 格式化路径函数整合为 `normpath`
- 移除: lkdb 相关方法
- 修复: `find(all)_dirs` 对要排除的路径的漏判
- 变更: `find*` 相关函数的 `fmt`, `suffix` 参数仅限关键字形参传入

**excel_writer.py**

- 优化: 简化 `ExcelWriter.__init__:params:options` 的传值方式
- 新增: 单元格格式添加
- 修复: `ExcelWriter.activate_sheet`
- 新增: 集成 sheet 管理

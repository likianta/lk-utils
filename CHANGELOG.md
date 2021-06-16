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

**excel_writer.py**

- 优化: 简化 `ExcelWriter.__init__:params:options` 的传值方式

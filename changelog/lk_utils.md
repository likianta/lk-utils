lk_utils.py

current version: 1.4.4

--------------------------------------------------------------------------------

## 1.4 | 2020-09-06

### 1.4.4 | 2020-11-27

- [修复] read_and_write.py 一系列错误
- [修复] filesniff.py 一系列错误
- [优化] filesniff.py 路径处理
- [变更] 移除一些第三方依赖

### 1.4.3 | 2020-11-22

- [修复] read_and_write.py 错误的 raise Exceptions 行为
- [变更] 将部分模块标记为 depreciated
- [更新] filesniff.py 优化与更新

### 1.4.2 | 2020-11-22

- [变更] 恢复 _typings.py
- [变更] exit_ways.py 重命名为 easy_launcher.py 并重新实现
- [更新] read_and_write.py 优化与更新
- [更新] filesniff.py 优化与更新
- [修复] excel_writer.ExcelWriter 一些错误
- [更新] excel_writer.py 优化与更新

### 1.4.1 | 2020-09-06

- [变更] filesniff._find_paths() 返回格式调整为 fp-fn
- [移除] 将 lk-logger 模块从 lk-utils 中剥离并独立
- [变更] lk-utils 仍将代理提供 lk-logger
- [移除] _typings.py
- [移除] 将 lxml 从 lk-utils 的必须依赖中移除

--------------------------------------------------------------------------------

## 1.3 | 2020-08-09

- html_table_converter.py 合并到 data_convert.py
- 修正方法细节, 提高模块易用性

--------------------------------------------------------------------------------

## 1.2 | 2019-11-01

- 创建 filesniff.py
- toolbox 将 file_sniffer 替换为 filesniff
- toolbox 引入 filesniff 的 stitch_path 方法
- read_and_write_basic.py 重命名为 read_and_write.py
- lk_logger.LKLogger 新增 terminal 类变量, 用于指定输出终端
- toolbox 引入 os.path.exists
- 移除 read_and_write_basic.py
- 移除 file_sniffer.py
- 移除 excel_writer_lazy.py
- 更新词典资源 (metadata)
- 所有模块中的参数 rtype 重命名为 fmt
- 将 lk_wrapper.BeautifulSoup 加入到 toolbox
- 优化模块方法
- 移除废弃的模块 (ast_analyser.py, html_reader.py)

--------------------------------------------------------------------------------

## 1.1 | 2019-09-27

- 创建 toolbox1.py 和 toolbox2.py
- 移除 toolbox2.py, 并将 toolbox1.py 重命名为 toolbox.py
- 移除 excel_2_mongodb.py
- 移除 cols_ratio_calc.py
- 创建 lk_wrapper.py
- 修复打包

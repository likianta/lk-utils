excel_writer.py

current version: 2.3

--------------------------------------------------------------------------------

# 2.3 | 2020-09-05

- [移除] ExccelWriter._increase_rowx()
- [新增] ExccelWriter.writelnx()
- [优化] 简化 ExccelWriter.rowx 自增长过程
- [变更] ExccelWriter.__init__() 调整 options 参数的处理方法
- [更新] ExccelWriter.__init__() 对 filepath 的后缀名使用更严格的检查
- [更新] 保存时的打印信息降级为 DEBUG
- [移除] ExcelWriter.add_new_sheet() 移除 prompt 参数
- [优化] excel_writer.py 自己使用 typing hints
- [修复] ExcelWriter.merging_logical() 逻辑错误
- [新增] ExcelWriter.save() 保存失败时提醒用户重试
- [优化] 类型提示
- [优化] 保存时的提示信息
- [优化] ExcelWriter.merging_visual() 对 ExcelWriter.rowx 更新
- [变更] ExcelWriter.rowx 默认从 0 开始数
- [新增] ExcelWriter._sheet_mgr
- [新增] 支持切换 sheet
- [新增] 当保存失败时, 提供改名后保存的措施
- [新增] ExcelWriter.save() 添加 open_after_saved=False 参数

# 2.2 | 2020-08-02

- 增加 with 语法支持
- 优化合并单元格方法, 创建 "visual" "logical" 两种方式
- 单元格写入方法增加 fmt 参数
- 调整 merging_logical() 方法
- merging_visual() 增加起始位置参数
- 当启用 constant_memory 模式时, 提示合并单元格操作无法生效
- 增加 save() 的别名方法 close()

# 2.1 | 2019-09-10

- ExcelWriterR 及 ExcelCopy 迁移到 excel_writer_lazy.py
- 新增 merge_cells() 方法
- 新增 merge_format 格式变量
- 新增 write_merging_cells() 方法
- write_merging_cells() 使用掩码实现更安全的合并措施
- __init__() 为 sheetname 参数增加识别特殊值 None
- add_new_sheet() 增加 prompt 参数并默认不再提示新增 sheet
- __init__() 设置不自动识别和转换链接字符串
- 新增 clean_values() 方法
- 优化打印的 log 信息
- 优化 add_new_sheet() 的 prompt 逻辑
- clean_values() 重命名为 purify_values()
- 屏蔽由 xlsxwriter 引起的 python 3.8 SyntaxWarning
- 强化 purify_values() 功能
- writecol() offset 参数默认值由 1 改为 0
- __init__() 使用 options 参数取代 constant_memory
- writerow(), writecol() 不使用变长参数

# 2.0 | 2019-09-10

- 创建基于 xlsxwriter 的 ExcelWriter
- 原 ExcelWriter 重命名为 ExcelWriterR 并进入维护状态
- ExcelWriterR 部分变量命名优化
- ExcelWriterR.__init__() 取消目标目录是否存在的检查
- ExcelCopy 移除覆写的 writeln() 方法
- 将原 write_row_values() 移植为 ExcelWriterR 内部方法
- 将原 write_col_values() 移植为 ExcelWriterR 内部方法
- ExcelWriterR 将 add_new_sheet() 操作从 write 改为在初始化期间执行

# 1.6 | 2019-09-10

- 创建 WorkbookYahei 继承自 xlwt.Workbook
- 创建 WorksheetYahei 继承自 xlwt.Worksheet
- 新建表格字体默认改为微软雅黑

# 1.5 | 2019-07-24

- 优化 add_new_sheet() 逻辑, 大幅降低耦合
- writeln() 允许空行写入
- 在初始化时执行一次 add_new_sheet()
- add_new_sheet() 与 add_new_book() 脱耦, 并独立出 _increase_sheetx()
- 移除 self.dirout 变量
- 移除 write_table_data() 方法
- ExcelCopy 覆写 writeln() 方法并增加 offset 参数
- write_row_values(), write_col_values() 使用可变长度的 *data 参数
- write_row_values() 简化传参和逻辑
- 修复自动创建新 sheet 和 header 时的重复写入的错误
- 优化自动增长 rowx, sheetx 和 bookx 的逻辑
- 修复外部调用创建新 sheet/book 的方法导致的 rowx/sheetx 错误
- 去除 self.dirout 变量并简化 add_new_book() 方法
- 修复并优化自动增长 rowx, sheetx 和 bookx 的逻辑
- 新增 self.rowx_offset 类变量并适配相关逻辑
- 修复自动增长 sheetx 的逻辑错误
- 修复因容量上限修改失误引起的严重错误
- 在初始化时, 检查文件的输出目录是否存在
- 修正 ExcelCopy 的初始化行为
- 优化 auto index 的逻辑
- 优化 pathout 父目录是否存在的判断

# 1.4 | 2019-04-28

- 当 cell 文本过长时, 使用更醒目的警告标志
- 创建 set_auto_header()
- 将 writeln() 中有关 rowx 增长的逻辑单独为 _increase_rowx()
- 修复首次 write() 报未定义 self.sheet 的错误
- 限制 writeln() 的 *data 形式
- 优化 auto_index 的逻辑, 简化相关方法
- 修复 auto_index 逻辑错误, 取消 automation['auto_index'] 参数 (使共用 self.rowx)
- 修复 auto_index 引起的新建 sheet 时的编号溢出
- 将 auto_index 转移到 write_row_values() 中实现
- 简化 auto_index 逻辑, 不再支持给 header 加 'index'
- ExcelCopy.__init__() 参数 continue_rowx 重命名为 relay_rowx
- write_col_values() 新增参数 offset=0
- ExcelCopy 增加 activate_sheet() 方法

# 1.3

- 使新建的 part book 自动创建到目标文件所在的目录
- 优化新建 part book 的 book 名称
- 使用 enumerate 替代 range(len()) 结构
- 优化结构及修复若干错误
- excel 在保存时, 增加保存路径的打印信息
- writeln() 实参改为形参
- add_new_sheet() 增加 sheet_name 参数
- 优化新增 sheet 或 book 时的提示信息
- 创建 ExcelCopy
- 关闭 ExcelCopy 的 PyMissingConstructor 语法警告
- 增加自增长 index 功能
- 创建 write_row_values_with_auto_index()
- 简化 ExcelWriter.__init__(), 取消 pathout 参数检查
- 修复 ExcelWriter 共用实例的错误
- self.heder_row 重命名为 self.header
- 修复 ExcelCopy 成员未定义的问题

# 1.2

- 重构为 class (ExcelWriter)
- 增加 add_new_sheet() 方法
- 增加 add_new_book() 方法
- 增加自定义单 book 的容量上限
- 使用 lk_logger 替代 print()
- 优化提示信息
- rite_table_data() 增加 except_header 参数
- 取消 ExcelWriter 的初始化参数
- 将单 book 的默认容量上限调低到 20w
- 将 self.pathout 拆分为 self.dirout 和 self.pathout
- 去除 save() 函数的 path 参数, 只允许在初始化时赋值
- 修复 self.header_row 丢失的问题

# 1.1

- 增加了 write_col_values() 方法
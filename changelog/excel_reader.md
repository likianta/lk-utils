excel_reader.py 

current version: 1.2

--------------------------------------------------------------------------------

## 1.2 | 2019-08-20

- [新增] betterint()
- [新增] get_colx()
- [新增] zip_cols()
- [新增] enum_cols()
- [移除] ColIndexLocator.get_header_dict()
- [优化] 简化 enum_cols()
- [变更] getall_rows() 重命名为 walk_rows()
- [新增] enum_rows()
- [变更] 调整 walk_rows(), enum_rows() 参数及默认值
- [变更] 重构 ColIndexLocator
- [修复] ColIndexLocator 通过 str 类型转化以避免可能的 IndexError
- [变更] ColIndexLocator.get_colx() 重命名为 find_colx()
- [更新] 使 ExcelReader 继承自 ColIndexLocator
- [变更] is_raise_error 参数改为 ignore_error
- [移除] ExcelReader 移除 sheetx 类变量
- [修复] ColIndexLocator.find_colx()
- [优化] enum_cols(), zip_cols() 在请求单列时的返回格式
- [更新] walk_rows() 参数默认值
- [修复] enum_cols() 多列值的返回不当
- [变更] walk_rows(), enum_cols() 的参数顺序
- [优化] 完善类型提示
- [新增] with 语法支持

## 1.1

- ColIndexLocator 并入本模块
- 增加 get_sheet() 方法
- 增加 on_demand 参数及关闭文件方法
- 增加 formmating_info 参数
- 删除 sheet_manager 以及简化 get_sheet() 方法
- 增加 get_name_of_sheets() 方法
- 修复 col_values() 可能引起的错误
- 增加 cell_value() 方法
- 取消 self.on_demond 类变量
- 增加 self.filepath 类变量及相关 get() 方法
- 删除 (无用的) self.sheet_manager 类变量
- 变更 get_sheet() 的逻辑
- 增加 activate_sheet() 方法
- 删除 self.sheetx 类变量
- 增加 self.header 类变量
- 增加 row_dict() 方法
- 增加 get_range() 方法
- activate_sheet() 增加对空 sheet 的预判
- col_values() 增加 offset 参数
- 优化 activate_sheet() 方法

## 1.0

- 创建 ExcelReader
- 引入 ColIndexLocator
- 在初始化中令 ColIndexLocator 的 self.header_row 为全小写
- 将 is_raise_error 提升为成员
- 增加强化版的 col_values() 方法
- 将 is_raise_error 的初始值由 None 改为 True
- __init__() 函数增加 sheetx 参数
- 将 ColIndexLocator 独立为 common_utils 模块
- 增加获取行数和列数的方法
- 增加 row_values() 方法
- 增加 get_header() 方法
- 增加 get_num_of_sheets() 方法

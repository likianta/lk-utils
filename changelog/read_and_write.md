read_and_write.py

current version: 1.8

--------------------------------------------------------------------------------

## 1.8 | 2020-11-22

- [新增] ropen() 和 wopen()
- [优化] 统一参数命名
- [新增] write_json() 支持输出到 yaml 文件
- [新增] write_json() 接受 set 类型的数据
- [变更] read() 和 write() 从 loads()/dumps() 概念中独立, 并使用 with 结构支持
- [修复] 不正确的 raise Exceptions
- [优化] write_json() 增强适应性
- [移除] write() 不再支持 .xlsx 文件格式
- [优化] 类型提示
- [优化] read_json()
- [修复] read_file_by_line() 错误的 strip 行为
- [优化] loads(), dumps() 支持更多文件类型

## 1.7 | 2020-08-09

- [移除] FileSword
- [优化] 完善类型提示
- [移除] 不再调用 lk_logger 模块
- [新增] 引入 _typing.py
- [新增] loads() 支持更多文件格式
- [变更] 将 loads() 读取文本文件的默认行为指向 read_file()
- [新增] load_list()
- [新增] load_dict()
- [变更] is_file_empty() 重命名为 is_file_has_content()

## 1.6 | 2019-11-06

- read_and_write_basic.py 重命名为 read_and_write.py
- loads, dumps 添加别名 read, write
- loads() 调整对 html 文件的读取方式的判别

## 1.5 | 2019-10-25

- 新增 loads(), dumps() 函数
- 移除 _json_holder 变量
- 调整 loads() 传参
- 调整 dumps() 后缀的识别范围

## 1.4

- FileSword 简化文件是否为空的判断方法
- 完善 write_json(), 使 json.dumps() 输出中文不要被转码
- 优化 clear_any_existed_content 对应的判断方法
- 引入 lk_logger 替代 print()
- 优化 write_file() 方法
- 使 read_json() 保持单例模式
- 简化 FileSword 的初始化操作 (删除 is_create_dir 参数)
- FileSword.close() 增加 "保存文件" 的提示
- FileSword 优化 write() 方法
- write_json() 解除与 write_file() 的耦合关系
- 增加 write_json() 对 data 参数的类型断言
- 读取文件流改用 "utf-8-sig" 编码
- 变更 is_empty 返回逻辑
- read_file_by_line() 优化代码
- 简化 write_file() 操作逻辑
- read_file_by_line() 新增 offset=0 参数

## 1.3

- 增加 FileSword
- 减少了旧方法的代码量
- 增加了 FileSword 的注释文档
- write_file() 修改关闭文件的判断逻辑
- 增加 read_json() 和 write_json() 方法
- 完善 init() 函数的 is_create_dir 参数对应的方法
- 优化了 has_content() 的判断逻辑
- 将init() 的 mode 参数默认由 "a+" 改为了 "a"
- write_file() 增加对 tuple 对象的支持
- write_file() 增加对非 str 类型元素的支持
- write_file() 的 mode 参数默认改为 'w'
- 增加 get_file_path() 方法
- 增加 write_multi_lists() 方法
- 在 write_file() 中使用 map() 操作
- 增加一个简单的判断文件是否为空的方法 is_empty()

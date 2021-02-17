"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : lk_config.py
@Created : 2019-00-00
@Updated : 2020-09-06
@Version : 1.6.10
@Desc    :
"""
import os
from re import compile

from lk_logger import lk

from . import filesniff
from .read_and_write import read_json, write_json
from .time_utils import get_file_modified_time


class LKConfig:
    """ LKConfig 是一个适合在项目全局中引用的配置系统. 可以用于跨模块地共享某些
     变量. 使您对共享变量进行集中的, 方便的配置和管理.

    预先配置:
        请确保项目的 conf 目录下有一个 "config.json" 文件: "~/conf/config.json".
         然后您就可以引用本模块, 进行自动化的管理.

    工作原理:
        当导入本模块到您的项目中时, LKConfig 会自动查找 config.json 文件, 并加载
         到自身实例中.
        当用户需要读取来自配置文件的某一参数时, 只需使用 LKConfig 的 get() 方法
         即可 (详见下面的 "基本用法" 一览).

    使用 LKConfig 具有以下优势:
        1. 任何用户参数都可以在配置文件 ("~/data/config.json") 中事先定义好
        2. 在配置文件中, 支持动态路径配置. LKConfig 会自动计算出实际路径以及创建
           缺失的目录 (详见下面的 "高级用法" 一览)
        3. 在多个模块中调用 LKConfig, 只会在第一次导入/初始化时加载一次配置文件,
           不会重复加载

    基本用法:
        假设 config.json 内容为:
            {
                "name": "likianta",
                "gender": "male",
            }

        1. 导入模块:
            from lk_utils.lk_config import cfg
        2. 读取值:
            x = cfg.get("name")  # -> 'likianta'
        3. 写入值:
            # 以键值对形式写入
            cfg.set('age', 24)  # 第一个参数是键名, 第二个参数是值
            # -> 生成 {'age': 24}

            # 以多级键值对形式写入
            cfg.set('birth', 'birthplace', 'China')
            cfg.set('birth', 'birthday', '0101')
            # -> 生成 {'birth': {'birthplace': "China", 'birthday': '0101'}}

    高级用法:
        假设 config.json 内容为:
            {
                "A": "aaa",
                "B": "{A}.txt",
                "C": "../{A}/{B}",
                "init_path": true
                # 注: 只有 "init_path" 为 True 时, LKLogger 才会计算动态路径
            }

        1. 导入模块:
            from lk_utils.lk_config import cfg
            '''
            LKLogger 在第一次导入时, 会自动加载配置文件, 并计算出动态路径的实际
             值. 此时的 LKLogger 储存的配置实例为:
                self.root = {
                    "A": "aaa",
                    "B": "aaa.txt",
                    "C": "../aaa/aaa.txt",
                    "init_path": False
                }
            '''

    参考:
        https://www.cnblogs.com/huchong/p/8244279.html
        https://stackoverflow.com/questions/6760685/creating-a-singleton-in
         -python/48074157#answer-48074157
        https://blog.csdn.net/bf02jgtrs00xktcx/article/details/78900961
    """
    config_shot_path = config_path = ''
    aestus_estus = root = None
    
    def __init__(self, config_path: str):
        """
        ARGS:
            config_path (str): 配置文件的路径, 为空则不从配置文件读取配置
        """
        if config_path:
            self.load_config(config_path)
        else:
            self.aestus_estus = {}
            self.root = {}
    
    def load_config(self, config_path):
        self.config_path = config_path
        self.config_shot_path = config_path.replace('.json', '.shot.json')
        
        self.aestus_estus = read_json(self.config_path)
        
        if self._is_cache_available():
            lk.logt('[LKConfig][D1130]',
                    'restore config shot from "{}"'.format(
                        self.config_shot_path
                    ),
                    h='self')
            # using cache
            self.root = read_json(self.config_shot_path)
        else:
            self.root = self.aestus_estus.copy()
            # link the fire
            collected_paths = init_path(self.root)
            validate_path(collected_paths)
    
    def _is_cache_available(self):
        """ try to restore the shot of config if exists.
        
        NOTE: LKConfig will not auto generate shot files unless you called
        cfg.save(). so as a more common case, you will see this method usually
        returns False.
        """
        if not os.path.exists(self.config_shot_path):
            return False
        
        # check the latest edit timestamp
        modified_time1 = get_file_modified_time(self.config_path)
        modified_time2 = get_file_modified_time(self.config_shot_path)
        
        return modified_time2 > modified_time1
    
    def set(self, *data):
        # 仿照 tree_and_trie.Tree.set() 设计.
        if len(data) == 1:
            # NOTICE: cannot set a data with only one or less element.
            raise AttributeError
        elif len(data) == 2:
            k, v = data
            self.root[k] = v
        else:
            temp_dict = {}
            node = temp_dict
            for i in data[:-2]:
                node = node.setdefault(i, {})
            node.setdefault(data[-2], data[-1])
            self.root.update(temp_dict)
    
    def get(self, *data):
        """
        NOTE: LKConfig 重写了 get() 方法, 使用了更严格的方式. 当找不到目标 key
         时, LKConfig 会报 KeyError 错误.
        """
        if not data:
            # get() 参数不能为空
            raise AttributeError
        
        if len(data) == 1:
            return self.root[data[0]]
        
        node = self.root
        for i, d in enumerate(data):
            node = node[d]
        return node
    
    def get_config(self):
        return self.root
    
    def save(self, path='', clear=False):
        """ 生成配置文件的快照. """
        from .time_utils import simple_timestamp
        
        """
        说明: 为什么不覆盖保存原文件?
            假设我们的原文件为:
                // config.json
                {'A': 'hello', 'B': '{A}', 'init_path': True}
            当我们要保存时, 此时的 self.root 为:
                {
                    'A': 'hello',
                    'B': 'hello',
                    'init_path': False
                }
            我们需要保持原 config.json 中的结构, 这些结构是由开发者定义的, 也是
             由开发者来管理的. 如果覆盖保存了, 就会导致信息降维, 使开发者无法知
             道之前定义的 `'B': '{A}'` 结构, 这是不可取的.
        """
        
        # save config shot
        if not path:
            path = self.config_shot_path
        
        self.set('init_path', False)
        self.set('_snapshot_timestamp', simple_timestamp('y-m-d h:n:s'))
        
        write_json(self.root, path)
        lk.logt('[LKConfig][D1131]', 'saved config info {}'.format(path),
                h='parent')
        
        if clear:
            self.root.clear()


# ------------------------------------------------------------------------------

def init_path(config: dict):
    """ 对配置文件中的动态路径初始化.
    LKConfig 会检测 config 中的 'init_path' 字段 (如果有的话), 请确保它的值为一
     个布尔值.
    
    IN: config = {
            "A": "aaa",
            "B": "{A}.txt",
            "C": "{A}/{B}",
            "init_path": True
        }
    OT: config = {
            "A": "aaa",
            "B": "aaa.txt",
            "C": "D:/my_project/aaa/aaa.txt",
            "init_path": True
        }
        
    支持内置键:
        init_path
    支持关键字:
        LKDB: 表示项目在 lkdb 目录下的文件夹
        PRJ: 表示项目名称 (不是项目路径)
        当用户显式声明这两个键时, config 会直接使用; 否则 config 将自动创建
    
    注意:
        1. self.config['init_path'] 的值必须是布尔值
        2. 键的顺序有要求. 请按照键的动态计算顺序来添加, 比如上例中, 先计算出
           "B" 然后才能计算 "C", 所以 "C" 不可以放在 "B" 前面
        3. 如果里面有子字典, 则优先会使用内部的替换值, 例如:
            config = {
                "A": "AAA"
                "B": {
                    "A": "BBB"
                    "B": "{A}"  # -> "BBB"
                }
            }
    技巧:
        1. LKConfig 将不计算 "init_path" 后面的键值对, 你可以利用此特性把不需要
           计算的路径放在 "init_path" 后面:
            config = {
                "A": "AAA.txt",
                "B": "{A}",  # 会被计算 -> "AAA.txt"
                "init_path": True,
                "C": "D:/D/EEE.txt"  # 不会被计算
            }
    """
    if not config.get('init_path', False):
        return None
    if 'PRJ' not in config:
        config['PRJ'] = filesniff.get_dirname(filesniff.PRJDIR)
    if 'LKDB' not in config:
        config['LKDB'] = filesniff.lkdb('{PRJ}')
    
    collect_paths = []
    
    p = compile(r'{[^{}]+}')
    '''
    pattern to catch the braket.
    examples:
        './A/B/{C}/D' --> ['{C}']
        './A/{B}/{C}/D' --> ['{B}', '{C}']
    note:
        cannot catch nested structure like '{A{B}}'. (and this is not allowed)
    '''
    
    # --------------------------------------------------------------------------
    
    def recurse(obj_entity, obj_cursor, obj_value):
        if isinstance(obj_value, str):
            recurse_by_str(obj_entity, obj_cursor, obj_value)
        elif isinstance(obj_value, dict):
            recurse_by_dict(obj_value)
        elif isinstance(obj_value, list) or isinstance(obj_value, tuple):
            recurse_by_array(obj_value)
        else:
            # int, float, ...
            return
    
    def recurse_by_str(obj_entity, obj_cursor, obj_value):
        path_handler(obj_entity, obj_cursor, obj_value)
    
    def recurse_by_dict(obj_entity: dict):
        for step_limit, obj_key, obj_value in zip(
                range(101), obj_entity.keys(), obj_entity.values()
        ):
            if obj_key[0] in ('_', '/'):
                continue
            recurse(obj_entity, obj_key, obj_value)
            
            # if step_limit == 100:
            #     pass  # TODO: 可能需要一个步进限制避免处理大字典时过于耗时
    
    def recurse_by_array(obj_entity):
        for obj_index, obj_value in enumerate(obj_entity):
            recurse(obj_entity, obj_index, obj_value)
    
    # --------------------------------------------------------------------------
    
    def path_handler(obj_entity, obj_cursor, obj_value):
        place_holders = p.findall(obj_value)
        if place_holders:
            for holder in place_holders:
                # holder = '{A}'
                holder_stripped = holder.strip('{}')
                if holder_stripped == obj_cursor:
                    substitution = config[holder_stripped]
                else:
                    try:
                        substitution = obj_entity[holder_stripped]
                    except (KeyError, TypeError):
                        substitution = config[holder_stripped]
                obj_value = obj_value.replace(holder, substitution, 1)
        
        '''
        NOTE: LKConfig 对路径 (obj_value) 的处理方案:
            1. 路径以 "./" 开头: "./" 是一种特殊标识, 将会被转换为项目路径
            2. 路径以 "../" 开头: "../" 被认为是相对路径, 不会被处理
            3. 路径以 "*:/" 开头: "*:/" 被认为是绝对路径, 不会被处理
        '''
        if obj_value.startswith('./'):
            # a relative path. eg "./A/B/C.txt"
            real_path = filesniff.getpath(obj_value)
        elif obj_value.startswith('../'):
            real_path = obj_value
        elif obj_value[1:3] == ':/':
            # an absolute path. eg "D:/workspace/..."
            real_path = obj_value
        else:
            return
        
        obj_entity[obj_cursor] = real_path
        
        if real_path.strip('/') not in collect_paths:
            collect_paths.append(real_path.strip('/'))
    
    # --------------------------------------------------------------------------
    
    for key, value in config.items():
        if key == 'init_path':
            break
        if key[0] in ('_', '/'):
            """
            eg: "_comment", "//", "/0/", ...
            """
            continue
        recurse(config, key, value)
    
    return collect_paths


def validate_path(collected_paths: list, sorting_file_and_dir=True, ask=True):
    """ 检查是否有未创建的文件夹. 如果有, 则询问创建.
    
    :param collected_paths: list. 路径列表. 路径可以是绝对路径或相对路径.
    :param sorting_file_and_dir: bool
        True: 表示 collected_paths 中可能混杂有文件路径和文件夹路径, 需要本函数
         分拣
        False: 表示 collected_paths 中没有混杂路径 (全部都是文件夹路径), 无需分
         拣
    :param ask: bool
        True: 表示当发现有未创建的文件夹时, 需要询问用户是否创建 (input())
        False: 表示无需过问, 直接创建未存在的文件夹路径 (推荐开发者在事先知情的
         情况下使用)
    """
    if not collected_paths:
        return
    
    missing_dir_collector = []
    
    if sorting_file_and_dir:
        dir_collector = []
        
        for p in collected_paths:
            if filesniff.is_dir_like(p):
                dir_collector.append(p)
            else:
                dir_collector.append(os.path.dirname(p))
    else:
        # assumed collected_paths are all dir-like paths.
        dir_collector = collected_paths
        assert isinstance(dir_collector, (list, tuple))
    
    if not dir_collector:
        return
    
    for p in dir_collector:
        if not os.path.exists(p) and p not in missing_dir_collector:
            missing_dir_collector.append(p)
    
    missing_dir_collector.sort()
    if missing_dir_collector:
        lk.logt('[LKConfig][I3118]', "found uncreated paths:\n\t{}".format(
            '\n\t'.join(missing_dir_collector)), h='parent')
        
        if ask:
            cmd = input('\twould you allow LKConfig to create them? (y/n) ')
        else:
            cmd = 'y'
        
        if cmd.lower() == 'y' or cmd == '':
            for d in missing_dir_collector:
                os.mkdir(d)
            lk.logt('[LKConfig][I3119]', 'creating path succeed', h='parent')
        else:
            from . import easy_launcher
            easy_launcher.main('please create by yourself')


# ------------------------------------------------------------------------------

def _find_config_file():
    for i in (
            filesniff.getpath('conf/config.json'),
            filesniff.getpath('data/config.json'),
            filesniff.getpath('config.json'),
    ):
        if os.path.exists(i):
            return i
    else:
        # raise FileNotFoundError
        return ''


cfg = LKConfig(_find_config_file())

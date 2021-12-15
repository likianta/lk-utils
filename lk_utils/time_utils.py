"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : time_utils.py
@Created : 2019-00-00
@Updated : 2020-08-08
@Version : 1.1.3
@Desc    :
"""
import time
from os import stat


def timestamp(style='y-m-d h:n:s', ctime=0.0) -> str:
    """ 生成时间戳.
    
    转换关系:
        year  : %Y
        month : %m
        day   : %d
        hour  : %H
        minute: %M
        second: %S
    
    E.g. 'y-m-d h:n:s' -> '2018-12-27 15:13:45'
    """
    style = style \
        .replace('y', '%Y').replace('m', '%m').replace('d', '%d') \
        .replace('h', '%H').replace('n', '%M').replace('s', '%S')
    if ctime:
        return time.strftime(style, time.localtime(ctime))
    else:
        return time.strftime(style)


def seconds_to_hms(second: int):
    """ 将秒数转换成 hms 格式.
    REF: https://www.jb51.net/article/147479.htm
    """
    m, s = divmod(second, 60)
    h, m = divmod(m, 60)
    hms = "%02d%02d%02d" % (h, m, s)
    return hms


def get_file_modified_time(filepath, style=''):
    """
    REF: demos/os_demo#get_file_created_time
    """
    time_float = stat(filepath).st_mtime
    if style:
        return timestamp(style, time_float)
    else:
        return time_float


def get_file_created_time(filepath, style=''):
    """
    REF: demos/os_demo#get_file_created_time
    """
    time_float = stat(filepath).st_ctime
    if style:
        return timestamp(style, time_float)
    else:
        return time_float

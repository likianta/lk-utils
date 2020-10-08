"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : exit_ways.py
@Created : 2019-05-29
@Updated : 2020-08-09
@Version : 1.0.7
@Desc    :
"""
from time import sleep
from sys import exit


def main(msg='', sleepsecs=0):
    """
    :param msg
    :param sleepsecs: 0 表示按任意键退出; 大于 0 表示 n 秒后自动关闭
    """
    if msg:
        if isinstance(msg, str):
            print(msg.strip(' \n'))
        else:
            print(msg)
    
    if sleepsecs == 0:  # press_any_key
        input('按任意键退出程序 ')
    else:  # sleep_secs_to_leave
        print(f'脚本将在 {sleepsecs}s 后自动关闭...')
        sleep(sleepsecs)

    exit(1)

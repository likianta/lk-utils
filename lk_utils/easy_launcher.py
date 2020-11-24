"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : easy_launcher.py
@Created : 2019-05-29
@Updated : 2020-11-24
@Version : 2.0.2
@Desc    :
"""


def run(func, *args, **kwargs):
    """
    Usage:
        # my_main.py
        from lk_utils.easy_launcher import run
        
        def main(a, b):
            print(a + b)
            
        run(main, a=1, b=2)
    """

    # noinspection PyUnusedLocal
    def show_err_on_console(err):
        print('Runtime Error:', f'\n\t{err}')
        input('Prgress terminated, press ENTER to leave...')
    
    def show_err_on_msgbox(err):
        # https://stackoverflow.com/questions/17280637/tkinter-messagebox
        # -without-window
        from tkinter import Tk, messagebox
        root = Tk()
        root.withdraw()
        messagebox.showerror(title='Runtime Error', message=err)
    
    try:
        func(*args, **kwargs)
    except:
        # To obtain more message about this error.
        #   https://stackoverflow.com/questions/1278705/when-i-catch-an
        #   -exception-how-do-i-get-the-type-file-and-line-number
        import traceback
        msg = traceback.format_exc()
        show_err_on_msgbox(msg)
        #   show_err_on_console(msg)


def main(msg='', sleepsecs=0):  # DELETE ME
    """
    Args:
        msg
        sleepsecs: 0 表示按任意键退出; 大于 0 表示 n 秒后自动关闭
    """
    from time import sleep
    from sys import exit
    
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


if __name__ == '__main__':
    pass

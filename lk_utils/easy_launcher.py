"""
@Author  : likianta <likianta@foxmail.com>
@Module  : easy_launcher.py
@Created : 2019-05-29
@Updated : 2020-11-19
@Version : 2.1.0
@Desc    :
"""
from functools import wraps


def launch(func):
    """ 此模块旨在发生报错时, 使窗口不要立即关闭, 留给用户查看错误信息的时间.
        当错误发生时, 按下任意键可结束程序.
        
    REF: https://www.runoob.com/w3cnote/python-func-decorators.html
    
    如何使用?
        # myprj/main.py
        from lk_utils.easy_launcher import launch
        
        @launch
        def main():
            print('hello world')
        
        if __name__ == '__main__':
            main()
    """

    # noinspection PyUnusedLocal
    def show_err_on_console(err):
        print('Runtime Error:', f'\n\t{err}')
        input('Press any key to leave...')
    
    def show_err_on_msgbox(err):
        # https://stackoverflow.com/questions/17280637/tkinter-messagebox
        # -without-window
        from tkinter import Tk, messagebox
        root = Tk()
        root.withdraw()
        messagebox.showerror(title='Runtime Error', message=err)
    
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            # To gain more message about this error.
            #   https://stackoverflow.com/questions/1278705/when-i-catch-an
            #   -exception-how-do-i-get-the-type-file-and-line-number
            import traceback
            msg = traceback.format_exc()
            show_err_on_msgbox(msg)
            #   show_err_on_console(msg)
        # finally:
        #     input('Prgress finished, press ENTER to leave...')
    
    return decorated

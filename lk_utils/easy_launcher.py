"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : easy_launcher.py
@Created : 2019-05-29
@Updated : 2020-11-28
@Version : 2.1.2
@Desc    :
"""
from functools import wraps


def show_err_on_console(msg: str):
    print('Runtime Error:', f'\n\t{msg}')
    input('Prgress terminated, press ENTER to leave...')


def show_err_on_msgbox(msg: str):
    # https://stackoverflow.com/questions/17280637/tkinter-messagebox-without
    # -window
    from tkinter import Tk, messagebox
    root = Tk()
    root.withdraw()
    messagebox.showerror(title='Runtime Error', message=msg)


def launch(func):
    """ 此模块旨在发生报错时, 使窗口不要立即关闭, 留给用户查看错误信息的时间.
        当错误发生时, 按下任意键可结束程序.
        
    References:
        https://www.runoob.com/w3cnote/python-func-decorators.html
        
    Usages:
        # myprj/main.py
        from lk_utils.easy_launcher import launch
        
        @launch
        def main():
            print('hello world')
        
        if __name__ == '__main__':
            main()
    """

    @wraps(func)
    def decorated(*args, **kwargs):
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

    return decorated


def run(func, *args, **kwargs):
    """ 另一种写法.
    
    Usage:
        # myprj/main.py
        from lk_utils.easy_launcher import run

        def main(a: int, b: int):
            print(a + b)

        run(main, a=1, b=2)
    """
    try:
        func(*args, **kwargs)
    except:
        import traceback
        msg = traceback.format_exc()
        show_err_on_msgbox(msg)
        #   show_err_on_console(msg)

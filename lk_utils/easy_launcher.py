"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : easy_launcher.py
@Created : 2019-05-29
@Updated : 2020-11-17
@Version : 2.0.0
@Desc    :
"""


def launch(func):
    """
    如何使用?
    您可以复制此文件到您的项目下, 再对 try 块中的内容进行自定义, 完成后, 在外部双击
    此文件 (指您在项目中的副本) 运行.
    此模块旨在发生报错时, 使窗口不要立即关闭, 留给用户查看错误信息的时间.
    当错误发生时, 按下任意键可结束程序.
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
    
    try:
        func()  # edit your main function here
    except Exception:
        # To gain more message about this error.
        #   https://stackoverflow.com/questions/1278705/when-i-catch-an
        #   -exception-how-do-i-get-the-type-file-and-line-number
        import traceback
        msg = traceback.format_exc()
        show_err_on_msgbox(msg)
        #   show_err_on_console(msg)
    finally:
        input('Prgress finished, press ENTER to leave...')


def main(msg='', sleepsecs=0):  # DELETE ME
    """
    :param msg
    :param sleepsecs: 0 表示按任意键退出; 大于 0 表示 n 秒后自动关闭
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

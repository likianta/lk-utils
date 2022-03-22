from lk_utils import subproc


def show_python_version():
    print(subproc.run_cmd_shell('python -V'))
    print(subproc.run_cmd_args('python', '-V'))


def show_pip_version():
    print(subproc.run_cmd_args('python', '-m', 'pip', '-V'))


def raise_an_error():
    print(subproc.run_cmd_args('depsland', '-V'))


def is_still_running_when_main_thread_crashed():
    from time import sleep
    
    def main_thread():
        subproc.run_new_thread(sub_thread)
        # subproc.run_new_thread(sub_thread, daemon=False)
        sleep(5)
        raise Exception
    
    def sub_thread():
        with open('test0.log', 'a') as f:
            for i in range(10):
                f.write(str(i))
                f.flush()
                print(i)
                sleep(1)
    
    main_thread()


if __name__ == '__main__':
    # show_python_version()
    # show_pip_version()
    # raise_an_error()
    is_still_running_when_main_thread_crashed()

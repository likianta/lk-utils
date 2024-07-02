from time import sleep

# from argsense import cli
from lk_utils.time_utils import timeit


@timeit('test1')
def test1():
    for i in range(3):
        sleep(0.1)
        print('test1', i)


# test1()

with timeit('test2'):
    for i in range(3):
        sleep(0.1)
        print('test2', i)

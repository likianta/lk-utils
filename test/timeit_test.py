import typing as t
from lk_utils import timing
from random import randint
from time import sleep

cnt: t.Callable
with timing() as cnt:
    for i in range(5):
        sleep(randint(1, 10) * 0.1)
        cnt()

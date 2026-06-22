from lk_utils.time import timing
from random import randint
from time import sleep

with timing() as cnt:
    for i in range(5):
        sleep(randint(1, 10) * 0.1)
        cnt()

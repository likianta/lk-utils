from random import randint
from time import sleep

from lk_utils import spinner

with spinner():
    sleep(randint(1, 3))
print('done')

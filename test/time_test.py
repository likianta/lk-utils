from random import randint

from lk_utils.time_utils import pretty_time

print(pretty_time(randint(3600, 7200)))
print(pretty_time(randint(60, 3600)))
print(pretty_time(randint(1, 60)))
print(pretty_time(randint(1, 60) / 1000))
print(pretty_time(randint(1, 60) / 1000000))
print(pretty_time(randint(1, 60) / 1000000000))

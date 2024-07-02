from lk_utils import Signal

a = Signal()


@a
def b(msg):
    print(msg)


def c():
    @a
    def d(msg):
        print(msg)
    return a

a.emit('ccc')
a.emit('ddd')

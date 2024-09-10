from lk_utils import coro


def main() -> None:
    @coro.on_update(loop)
    def _(v):
        print('updated', v, ':i')
    # print(loop, loop._updated_callbacks)
    loop()


@coro()
def loop() -> None:
    for i in range(5):
        print(i, 'hello')
        yield i
        yield coro.sleep(1)
    print('over')


if __name__ == '__main__':
    # pox test/force_stop_coro.py
    main()
    coro.join_all()

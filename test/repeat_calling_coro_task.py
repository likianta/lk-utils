from lk_utils import coro


@coro()
def foo(text) -> None:
    for i in range(10):
        print(text, ':i')
        yield coro.sleep(10e-3)


def main() -> None:
    foo('hello')
    foo('world')
    coro.join_all()


if __name__ == '__main__':
    main()

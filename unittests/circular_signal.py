from lk_utils import Signal

a = Signal(str)
b = Signal(str)


@a
def _(msg: str) -> None:
    print("msg from a", msg)
    b.emit("hello from b")


@b
def _(msg: str) -> None:
    print("msg from b", msg)
    a.emit("hello from a")


a.emit("hello world I", error_level=1)
a.emit("hello world II", error_level=2)
a.emit("hello world III", error_level=3)

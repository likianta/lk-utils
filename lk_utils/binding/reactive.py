import typing as t
from functools import partial

from .signal import Signal
from .signal import StopSignalEmission
from .signal import config
from .signal import get_func_id
from .signal import prop_chain


class T:
    OnChangedListener = t.Union[
        t.Callable[[], t.Any],
        t.Callable[[t.Any], t.Any],
        t.Callable[[t.Any, t.Any], t.Any],
        t.Callable[[t.Any, t.Any, t.Any], t.Any],
    ]
    Reactive = t.ForwardRef('Reactive')
    Value = t.TypeVar('Value', bound=t.Any)
    
    Boundable = t.Union[
        OnChangedListener,
        Signal,
        object,
        'Reactive',
    ]


class Reactive(Signal):
    __value: T.Value
    
    # type annotation
    def __class_getitem__(cls, type: t.Type) -> t.Type[T.Reactive]:
        return cls
    
    def __init__(self, value: t.Union[T.Value, T.Reactive]) -> None:
        super().__init__()
        if isinstance(value, Reactive):
            value = value.get()
        self.__value = value
    
    @property
    def value(self) -> T.Value:  # alias to `get`
        return self.__value
    
    def get(self) -> T.Value:
        return self.__value
    
    def set(self, value: T.Value, mute: bool = False) -> bool:
        if isinstance(value, Reactive):
            value = value.get()
        old_value = self.__value
        if old_value != value:
            self.__value = value
            if not mute:
                self._emit(old_value, value)
            return True
        return False
    
    def _quick_set(self, value: T.Value) -> None:
        old, new = self.__value, value
        self.__value = new
        self._emit(old, new)
    
    # set + get
    def setx(self, value: T.Value, mute: bool = False) -> T.Value:
        self.set(value, mute)
        return self.get()
    
    def bind(self, item: T.Boundable, attr: str = None) -> str:
        if attr:
            func_id = '{}:{}'.format(id(item), attr)
            self._funcs[func_id] = (lambda new: setattr(item, attr, new), 1)
            return func_id
        else:
            if isinstance(item, Reactive):
                item = item.set
            elif isinstance(item, Signal):
                item = item.emit
            func_id = get_func_id(item)
            # noinspection PyTypeChecker
            args_cnt = get_func_args_count(item)
            assert args_cnt in (0, 1, 2, 3)
            if (
                func_id in self._funcs and
                config.duplicate_locals_scheme == 'ignore'
            ):
                return func_id
            self._funcs[func_id] = (item, args_cnt)
            return func_id
    
    # on_change = bind  # alias
    
    @property
    def on_change(self):
        return self
    
    # noinspection PyMethodOverriding
    def emit(self) -> None:
        self._emit(self.__value, self.__value)
    
    notify = emit  # alias. TODO: we're considering `notify` as the formal name.
    
    def _emit(self, old_value: T.Value, new_value: T.Value) -> None:
        if not self._funcs: return
        try:
            with prop_chain.locking(self):
                for f, n in tuple(self._funcs.values()):
                    try:
                        if n == 0:
                            f()
                        elif n == 1:
                            f(new_value)
                        elif n == 2:
                            f(old_value, new_value)
                        else:
                            f(self, old_value, new_value)
                    except Exception as e:
                        print(':e', e)
        except StopSignalEmission:
            if config.circular_signal_error == 'prompt':
                print(
                    'signal is prevented because of circular emissions',
                    ':p2vs'
                )
            elif config.circular_signal_error == 'raise':
                raise StopSignalEmission(
                    '\n' + prop_chain.describe_call_chain()
                )
    
    # -------------------------------------------------------------------------
    # orverriden dunder methods
    # cheatsheet:
    #   https://www.pythonmorsels.com/every-dunder-method/
    # except:
    #   __await__
    #   __buffer__
    #   __class_getitem__
    #   __del__
    #   __delattr__
    #   __dir__
    #   __get__
    #   __getattr__ (wip)
    #   __getattribute__
    #   __hash__
    #   __new__
    #   __repr__
    #   __setattr__ (wip)
    
    def __abs__(self):
        return self.__value.__abs__()
    
    def __add__(self, other):
        return self.__value.__add__(other)
        # if isinstance(other, Reactive):
        #     other = other.get()
        # return Reactive(self.__value.__add__(other))
    
    def __and__(self, other):
        return self.__value.__and__(other)
    
    def __bool__(self):
        return self.__value.__bool__()
    
    def __bytes__(self):
        return self.__value.__bytes__()
    
    def __ceil__(self):
        return self.__value.__ceil__()
    
    def __complex__(self):
        return self.__value.__complex__()
    
    def __contains__(self, item):
        return self.__value.__contains__(item)
    
    def __delitem__(self, key):
        return self.__value.__delitem__(key)
    
    def __divmod__(self, other):
        return self.__value.__divmod__(other)
    
    def __enter__(self):
        return self.__value.__enter__()
    
    def __eq__(self, other):
        return self.__value.__eq__(other)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.__value.__exit__(exc_type, exc_val, exc_tb)
    
    def __float__(self):
        return self.__value.__float__()
    
    def __floor__(self):
        return self.__value.__floor__()
    
    def __floordiv__(self, other):
        return self.__value.__floordiv__(other)
    
    def __format__(self, format_spec):
        return self.__value.__format__(format_spec)
    
    def __ge__(self, other):
        return self.__value.__ge__(other)
    
    def __getitem__(self, item):
        return self.__value.__getitem__(item)
    
    def __gt__(self, other):
        return self.__value.__gt__(other)
    
    def __hash__(self):
        return self.__value.__hash__()
    
    def __iadd__(self, other):
        if isinstance(other, Reactive):
            other = other.get()
        self._quick_set(self.__value + other)
        return self
    
    # TODO: modify `__i<xxx>__` methods...
    def __iand__(self, other):
        return self.__value.__iand__(other)
    
    def __ifloordiv__(self, other):
        return self.__value.__ifloordiv__(other)
    
    def __ilshift__(self, other):
        return self.__value.__ilshift__(other)
    
    def __imatmul__(self, other):
        return self.__value.__imatmul__(other)
    
    def __imod__(self, other):
        return self.__value.__imod__(other)
    
    def __imul__(self, other):
        return self.__value.__imul__(other)
    
    def __index__(self):
        return self.__value.__index__()
    
    def __int__(self):
        return self.__value.__int__()
    
    def __invert__(self):
        return self.__value.__invert__()
    
    def __ior__(self, other):
        return self.__value.__ior__(other)
    
    def __ipow__(self, other):
        return self.__value.__ipow__(other)
    
    def __irshift__(self, other):
        return self.__value.__irshift__(other)
    
    def __isub__(self, other):
        return self.__value.__isub__(other)
    
    def __iter__(self):
        return self.__value.__iter__()
    
    def __itruediv__(self, other):
        return self.__value.__itruediv__(other)
    
    def __ixor__(self, other):
        return self.__value.__ixor__(other)
    
    def __le__(self, other):
        return self.__value.__le__(other)
    
    def __len__(self):
        return self.__value.__len__()
    
    def __lshift__(self, other):
        return self.__value.__lshift__(other)
    
    def __lt__(self, other):
        return self.__value.__lt__(other)
    
    def __matmul__(self, other):
        return self.__value.__matmul__(other)
    
    def __mod__(self, other):
        return self.__value.__mod__(other)
    
    def __mul__(self, other):
        return self.__value.__mul__(other)
    
    def __ne__(self, other):
        return self.__value.__ne__(other)
    
    def __neg__(self):
        return self.__value.__neg__()
    
    def __or__(self, other):
        return self.__value.__or__(other)
    
    def __pos__(self):
        return self.__value.__pos__()
    
    def __pow__(self, other):
        return self.__value.__pow__(other)
    
    def __radd__(self, other):
        return self.__value.__radd__(other)
        # if isinstance(other, Reactive):
        #     other = other.get()
        # return Reactive(self.__value.__radd__(other))
    
    def __rand__(self, other):
        return self.__value.__rand__(other)
    
    def __rdivmod__(self, other):
        return self.__value.__rdivmod__(other)
    
    def __rfloordiv__(self, other):
        return self.__value.__rfloordiv__(other)
    
    def __rlshift__(self, other):
        return self.__value.__rlshift__(other)
    
    def __rmatmul__(self, other):
        return self.__value.__rmatmul__(other)
    
    def __rmod__(self, other):
        return self.__value.__rmod__(other)
    
    def __rmul__(self, other):
        return self.__value.__rmul__(other)
    
    def __ror__(self, other):
        return self.__value.__ror__(other)
    
    def __round__(self, n=None):
        return self.__value.__round__(n)
    
    def __rpow__(self, other):
        return self.__value.__rpow__(other)
    
    def __rrshift__(self, other):
        return self.__value.__rrshift__(other)
    
    def __rshift__(self, other):
        return self.__value.__rshift__(other)
    
    def __rsub__(self, other):
        return self.__value.__rsub__(other)
    
    def __rtruediv__(self, other):
        return self.__value.__rtruediv__(other)
    
    def __rxor__(self, other):
        return self.__value.__rxor__(other)
    
    def __setitem__(self, key, value):
        return self.__value.__setitem__(key, value)
    
    def __sizeof__(self):
        return self.__value.__sizeof__()
    
    def __str__(self):
        return self.__value.__str__()
    
    def __sub__(self, other):
        return self.__value.__sub__(other)
    
    def __truediv__(self, other):
        return self.__value.__truediv__(other)
    
    def __trunc__(self):
        return self.__value.__trunc__()
    
    def __xor__(self, other):
        return self.__value.__xor__(other)


def get_func_args_count(func: t.Any) -> int:
    if isinstance(func, partial):
        func = func.func
    cnt = func.__code__.co_argcount - len(func.__defaults__ or ())
    if 'method' in str(func.__class__): cnt -= 1
    return cnt

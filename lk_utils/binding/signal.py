import typing as t
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from types import FunctionType


class T:
    _Event = t.Any
    _NewValue = t.Any
    _OldValue = t.Any
    DuplicateLocalsScheme = t.Literal['exclusive', 'ignore', 'override']
    Func = t.TypeVar(
        'Func',
        bound=t.Union[
            t.Callable[[], t.Any],
            t.Callable[[_NewValue], t.Any],
            t.Callable[[_Event, _NewValue], t.Any],
            t.Callable[[_Event, _OldValue, _NewValue], t.Any],
        ],
    )
    FuncArgsNum = int  # the number of arguments. 0-3
    FuncId = str
    Funcs = t.Dict[FuncId, t.Tuple[Func, FuncArgsNum]]


class _Config:
    duplicate_locals_scheme: T.DuplicateLocalsScheme = 'override'
    use_thread_pool: bool = False


config = _Config()
# http://c.biancheng.net/view/2627.html
_pool = ThreadPoolExecutor(max_workers=1)


class Signal:
    _funcs: T.Funcs
    
    def __init__(self):
        self._funcs = {}
    
    def __bool__(self) -> bool:
        return bool(self._funcs)
    
    def __len__(self) -> int:
        return len(self._funcs)
    
    # decorator
    def __call__(self, func: T.Func) -> T.Func:
        self.bind(func)
        return func
    
    def emit(self, *args) -> t.Optional[Future]:
        if not self._funcs: return
        # print(self._funcs, ':l')
        if config.use_thread_pool:
            future: Future = _pool.submit(self._emit, args)
            return future
        else:
            self._emit(args)
    
    def _emit(self, args: tuple) -> None:
        assert len(args) in (0, 1, 3)
        #   0: no args (usually used by user)
        #   1: new value (usually used by user)
        #   3: component, old value, new value (usually used by internal)
        #       see `Component.__setattr__ > somewhere used "emit" etc.`
        # if len(args) == 0:
        #     comp, old, new = None, None, None
        # elif len(args) == 1:
        #     comp, old, new = None, None, args[0]
        # else:
        #     comp, old, new = args
        
        # print(self._funcs, ':l')
        with _propagation_chain.locking(self):
            for f, n in tuple(self._funcs.values()):
                if _propagation_chain.check(f):
                    try:
                        if n == 0:
                            f()
                            # _futures.append(_pool.submit(f))
                        elif n > len(args):
                            raise TypeError(
                                'function `{}` takes {} positional arguments '
                                'but {} were given'.format(
                                    f.__name__, n, len(args)
                                )
                            )
                        # if n == 1, `args` is `(new,)` or `(comp, old, new)`
                        # if n == 2, `args` can only be `(comp, old, new)`
                        # if n == 3, `args` can only be `(comp, old, new)`
                        elif n == 1:
                            f(args[-1])
                            # _futures.append(_pool.submit(f, args[-1]))
                        elif n == 2:
                            f(args[0], args[-1])
                            # _futures.append(_pool.submit(f, args[0], args[-1]))
                        else:
                            f(args[0], args[-2], args[-1])
                            # _futures.append(
                            #     _pool.submit(f, args[0], args[-2], args[-1])
                            # )
                    except Exception as e:
                        print(':e', e)
                else:
                    print(
                        'function prevented because out of propagation chain', f
                    )
    
    # noinspection PyUnresolvedReferences
    def bind(self, func: T.Func) -> None:
        id = get_func_id(func)
        if (
            id in self._funcs and
            config.duplicate_locals_scheme == 'ignore'
        ):
            return
        argcount = get_func_args_count(func)
        assert argcount in (
            0, 1, 2, 3  # fmt:skip
        ), f'''
            invalid argcount: {argcount}
            the function should take 0-3 positional arguments for:
                0: no args
                1: new value
                2: old value, new value
                3: component, old value, new value
        '''
        self._funcs[id] = (func, argcount)
    
    def unbind(self, func: T.Func) -> None:
        self._funcs.pop(get_func_id(func), None)
    
    def unbind_all(self) -> None:
        self._funcs.clear()
    
    clear = unbind_all


class SignalFactory:
    """
    mimic the struct of `brilliant.component.property.PropFactory`.

    note: `__getitem__` and `__call__` do the same. they are just for \
    different usages - in convention - like below:
        class SomeComponent:
            aaa: signal[str]  # good to use square brackets
            def __init__(self, ...):
                self.bbb = signal(bool)
                #   good to use parentheses in assignment statement.
                #   unlike qt, we can init signal in `__init__` method.
                self.ccc = signal()
                #   the type can be omitted, which is slightly different with \
                #   the squared form: `signal[must_give_a_type]`.
    """
    
    def __getitem__(self, *types: t.Type) -> Signal:
        return Signal()
    
    def __call__(self, *types: t.Type) -> Signal:
        return Signal()


signal = SignalFactory()


class _PropagationChain:
    """
    a chain to check and avoid infinite loop, which may be caused by mutual
    signal binding.
    """
    
    _chain: t.Set[T.FuncId]
    _is_locked: bool
    _lock_owner: t.Optional[Signal]
    
    def __init__(self):
        self._chain = set()
        self._is_locked = False
        self._lock_owner = None
    
    @property
    def lock_owner(self) -> t.Optional[Signal]:
        return self._lock_owner
    
    @contextmanager
    def locking(self, owner: Signal) -> None:
        self.lock(owner)
        yield
        self.unlock(owner)
    
    def check(self, func: T.Func) -> bool:
        """
        check if function already triggered in this propagation chain.
        """
        if (id := get_func_id(func)) not in self._chain:
            self._chain.add(id)
            return True
        else:
            return False
    
    def lock(self, owner: Signal) -> bool:
        if self._lock_owner:
            return False
        self._is_locked = True
        self._lock_owner = owner
        # assert not self._chain
        # # self._chain.clear()
        # print(f'locked by {owner}', ':pv')
        return True
    
    def unlock(self, controller: Signal) -> bool:
        if self._lock_owner != controller:
            return False
        self._is_locked = False
        self._lock_owner = None
        self._chain.clear()
        return True


def get_func_args_count(func: FunctionType) -> int:
    cnt = func.__code__.co_argcount - len(func.__defaults__ or ())
    if 'method' in str(func.__class__): cnt -= 1
    return cnt


def get_func_id(func) -> T.FuncId:
    # related test: tests/duplicate_locals.py
    if config.duplicate_locals_scheme == 'exclusive':
        return str(id(func))
    else:
        # https://stackoverflow.com/a/46479810
        return func.__qualname__


_propagation_chain = _PropagationChain()

import typing as t
from contextlib import contextmanager
from functools import partial
from types import FunctionType


class T:
    DuplicateLocalsScheme = t.Literal['exclusive', 'ignore', 'override']
    Func = t.Union[FunctionType, t.Callable]
    # Func = FunctionType
    # Func = t.Callable
    FuncId = str
    Funcs = t.Dict[FuncId, Func]


class _Config:
    duplicate_locals_scheme: T.DuplicateLocalsScheme = 'override'
    # use_thread_pool: bool = False


config = _Config()


class _Signal:
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
    
    def emit(self, *_args, **_kwargs) -> None:
        if not self._funcs: return
        # print(self._funcs, ':l')
        with _propagation_chain.locking(self):
            f: T.Func
            for f in tuple(self._funcs.values()):
                if _propagation_chain.check(f):
                    try:
                        f(*_args, **_kwargs)
                    except Exception as e:
                        print(':e', e)
                else:
                    print(
                        'function prevented because '
                        'out of propagation chain', f
                    )
    
    # DELETE: we don't want to use `name` param in future.
    def bind(self, func: T.Func, name: str = None) -> T.FuncId:
        id = name or get_func_id(func)
        if (
            id in self._funcs and
            config.duplicate_locals_scheme == 'ignore'
        ):
            return id
        self._funcs[id] = func
        return id
    
    def unbind(self, func_or_id: t.Union[T.Func, T.FuncId]) -> None:
        id = (
            func_or_id if isinstance(func_or_id, str)
            else get_func_id(func_or_id)
        )
        self._funcs.pop(id, None)
    
    def unbind_all(self) -> None:
        self._funcs.clear()
    
    clear = unbind_all


class SignalFactory:
    
    def __getitem__(self, *types: t.Type) -> t.Type[_Signal]:
        return _Signal
    
    def __call__(self, *types: t.Type) -> _Signal:
        return _Signal()


Signal = SignalFactory()


class _PropagationChain:
    """
    a chain to check and avoid infinite loop, which may be caused by mutual
    signal binding.
    """
    
    _chain: t.Set[T.FuncId]
    _is_locked: bool
    _lock_owner: t.Optional[_Signal]
    
    def __init__(self):
        self._chain = set()
        self._is_locked = False
        self._lock_owner = None
    
    @property
    def lock_owner(self) -> t.Optional[_Signal]:
        return self._lock_owner
    
    @contextmanager
    def locking(self, owner: _Signal) -> None:
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
    
    def lock(self, owner: _Signal) -> bool:
        if self._lock_owner:
            return False
        self._is_locked = True
        self._lock_owner = owner
        # assert not self._chain
        # # self._chain.clear()
        # print(f'locked by {owner}', ':pv')
        return True
    
    def unlock(self, controller: _Signal) -> bool:
        if self._lock_owner != controller:
            return False
        self._is_locked = False
        self._lock_owner = None
        self._chain.clear()
        return True


# def get_func_args_count(func: FunctionType) -> int:
#     cnt = func.__code__.co_argcount - len(func.__defaults__ or ())
#     if 'method' in str(func.__class__): cnt -= 1
#     return cnt


def get_func_id(func: T.Func) -> T.FuncId:
    # related test: tests/duplicate_locals.py
    if config.duplicate_locals_scheme == 'exclusive':
        return str(id(func))
    else:
        # https://stackoverflow.com/a/46479810
        if isinstance(func, partial):
            # fix: `functools.partial` has no `__qualname__`.
            return func.func.__qualname__
        else:
            return func.__qualname__


_propagation_chain = _PropagationChain()

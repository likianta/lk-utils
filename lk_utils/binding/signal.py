import re
import textwrap
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


class _Config:  # DELETE
    duplicate_locals_scheme: T.DuplicateLocalsScheme = 'override'
    # use_thread_pool: bool = False


config = _Config()


class Signal:
    _funcs: T.Funcs

    def __class_getitem__(cls, *_: t.Any) -> t.Type['Signal']:
        """
        use square brackets to annotate a signal type.
        https://stackoverflow.com/a/68982326
        usage:
            some_signal: Signal[int, str]
        """
        return cls
    
    def __init__(self, *_) -> None:
        self._funcs = {}
    
    def __bool__(self) -> bool:
        return bool(self._funcs)
    
    def __len__(self) -> int:
        return len(self._funcs)
    
    # decorator
    def __call__(self, func: T.Func) -> T.Func:
        self.bind(func)
        return func
    
    def emit(self, *_args, error_level: int = 1, **_kwargs) -> None:
        """
        error_level: see `_PropagationChain._error_level:comment`
        """
        if not self._funcs: return

        # print(self._funcs, ':l')
        with _prop_chain.locking(self, error_level):
            f: T.Func
            for f in tuple(self._funcs.values()):
                if _prop_chain.check(f):
                    try:
                        f(*_args, **_kwargs)
                    except Exception as e:
                        print(':e', e)
                # else:  # TODO: should we break here or use `config` to decide?
                #     break
    
    # DELETE: param `name` may be removed in future.
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


class _PropagationChain:
    """
    a chain to check and avoid infinite loop, which may be caused by mutual -
    signal binding.
    """
    
    _chain: t.List[T.FuncId]
    _error_level: int
    #   0: no error print
    #   1: brief error print
    #   2: detailed error print
    #   3: detailed error print and raise error
    _is_locked: bool
    _lock_owner: t.Optional[Signal]
    
    def __init__(self) -> None:
        self._chain = []
        self._error_level = 0
        self._is_locked = False
        self._lock_owner = None
    
    # @property
    # def chain(self) -> t.List[T.FuncId]:
    #     return self._chain

    @property
    def lock_owner(self) -> t.Optional[Signal]:
        return self._lock_owner
    
    @contextmanager
    def locking(self, owner: Signal, error_level: int = 1) -> t.Iterator[None]:
        self.lock(owner, error_level)
        yield
        self.unlock(owner)
    
    def check(self, func: T.Func) -> bool:
        """
        check if function already triggered in this propagation chain.
        """
        if (id := get_func_id(func)) not in self._chain:
            self._chain.append(id)
            return True
        
        def print_error_details() -> None:
            chain = tuple(map(_pretty_id, self._chain))
            if len(chain) == 1:
                diagram = (
                    '╭─▶ 1. {}'.format(chain[0]),
                    '╰─x 2. {}'.format(chain[0]),
                )
            else:
                diagram = (
                    '╭─▶ 1. {}'.format(chain[0]),
                    *(
                        '│   {}. {}'.format(i, x) 
                        for i, x in enumerate(chain[1:], 2)
                    ),
                    '╰─x {}. {}'.format(len(chain) + 1, chain[0]),
                )

            print(textwrap.dedent('''
                signal prevented because of circular emissions:
                    {}
            ''').format(
                textwrap.indent('\n'.join(diagram), '    ').lstrip()
            ), ':p3v4s')

        def _pretty_id(func_id: T.FuncId) -> str:
            a, b, c = re.fullmatch(r'(.+)\((.+):(.+)\)', func_id).groups()
            b = re.split(r'[/\\]', b)[-1]
            return f'{a} ({b}:{c})'

        if self._error_level == 1:
            print('signal prevented because of circular emissions', ':p2vs')
        elif self._error_level == 2:
            print_error_details()
        elif self._error_level == 3:
            print_error_details()
            raise RecursionError('circular signal emissions')
        return False
    
    def lock(self, owner: Signal, error_level: int = 1) -> bool:
        if self._lock_owner:
            return False
        # assert not self._chain
        self._error_level = error_level
        self._is_locked = True
        self._lock_owner = owner
        return True
    
    def unlock(self, controller: Signal) -> bool:
        if controller is not self._lock_owner:
            return False
        self._chain.clear()
        self._error_level = 0
        self._is_locked = False
        self._lock_owner = None
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
            func = func.func
        # # return func.__qualname__
        return '{}({}:{})'.format(
            func.__qualname__,
            func.__code__.co_filename, 
            func.__code__.co_firstlineno,
        )


_prop_chain = _PropagationChain()

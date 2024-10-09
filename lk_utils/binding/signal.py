import typing as t
from contextlib import contextmanager
from functools import partial
from os.path import basename
from traceback import extract_stack
from types import FunctionType


class T:
    CircularSignalErrorScheme = t.Literal['ignore', 'prompt', 'raise']
    DuplicateLocalsScheme = t.Literal['exclusive', 'ignore', 'override']
    Func = t.Union[FunctionType, t.Callable]
    FuncId = str
    Funcs = t.Dict[FuncId, Func]


class _Config:
    circular_signal_error: T.CircularSignalErrorScheme = 'prompt'
    duplicate_locals_scheme: T.DuplicateLocalsScheme = 'override'
    # use_thread_pool: bool = False


class StopSignalEmission(Exception):
    pass


config = _Config()


class Signal:
    id: t.Tuple[str, int, str]
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
        stack = extract_stack(limit=2)[0]
        # self._id = 'Signal at {}:{} ("{}")'.format(
        #     basename(stack.filename), stack.lineno, stack.line
        # )
        self.id = (stack.filename, stack.lineno, stack.line)
        self._funcs = {}
    
    def __bool__(self) -> bool:
        return bool(self._funcs)
    
    # decorator
    def __call__(self, func: T.Func) -> T.Func:
        self.bind(func)
        return func
    
    def __len__(self) -> int:
        return len(self._funcs)
    
    def __str__(self) -> str:
        return '<Signal object at {}:{}>'.format(self.id[0], self.id[1])
    
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
    
    def emit(self, *args, **kwargs) -> None:
        if not self._funcs: return
        # print(self._funcs, ':l')
        try:
            with prop_chain.locking(self):
                f: T.Func
                for f in tuple(self._funcs.values()):
                    try:
                        f(*args, **kwargs)
                    except Exception as e:
                        print(':e', e)
        except StopSignalEmission:
            if config.circular_signal_error == 'prompt':
                print(
                    'signal is prevented because of '
                    'circular emissions', ':p2vs'
                )
            elif config.circular_signal_error == 'raise':
                raise StopSignalEmission(
                    '\n' + prop_chain.describe_call_chain()
                )
    
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
    _chain: t.List[Signal]
    
    def __init__(self) -> None:
        self._chain = []
    
    # @property
    # def chain(self) -> t.List[T.FuncId]:
    #     return self._chain
    
    @property
    def is_locked(self) -> bool:
        return bool(self._chain)
    
    @property
    def lock_owner(self) -> t.Optional[Signal]:
        """ return current owner of the lock. """
        return self._chain[0] if self._chain else None
    
    @contextmanager
    def locking(self, owner: Signal) -> t.Iterator[None]:
        self._lock(owner)
        yield
        self._unlock(owner)
    
    def _lock(self, signal: Signal) -> bool:
        if self._chain:
            if self._chain[0] is signal:
                raise StopSignalEmission
            else:
                self._chain.append(signal)
            return False
        # assert not self._chain
        self._chain.append(signal)
        return True
    
    def _unlock(self, signal: Signal) -> bool:
        # assert self._chain
        if signal is not self._chain[0]:
            return False
        self._chain.clear()
        return True
    
    def describe_call_chain(self) -> str:
        # chain = tuple(map(str, self._chain))
        chain = tuple(
            'Signal object at "{}:{}" ({})'.format(
                basename(x.id[0]), x.id[1], x.id[2]
            ) for x in self._chain
        )
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
        return '\n'.join(diagram)


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


prop_chain = _PropagationChain()

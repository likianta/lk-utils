import asyncio
import time
import typing as t
from functools import partial
from threading import Thread
from types import FunctionType
from types import GeneratorType

from ..time_utils import wait as sync_wait


class _Pause:
    pass


class _Unfinish:
    def __bool__(self) -> bool:
        return False


pause = _Pause()
_unfinish = _Unfinish()


class Task:
    def __init__(self, id: str, func: FunctionType, singleton: bool) -> None:
        self._cancelled_callbacks = {}
        self._crashed_callbacks = {}
        self._finished_callbacks = {}
        self._id = id
        self._over = None  # True, False, None
        self._partial_args = ()
        self._partial_kwargs = None
        self._result = _unfinish  # DELETE
        self._running = False
        self._singleton = singleton
        self._started_callbacks = {}
        self._target_func = func
        self._target_inst = None
        self._updated_callbacks = {}
    
    def __call__(self, *args, **kwargs) -> t.Self:
        self.run(*args, **kwargs)
        return self
    
    def __get__(self, instance, owner) -> t.Self:
        self._target_inst = instance
        return self
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def over(self) -> bool:
        return self._over
    
    @property
    def result(self) -> t.Any:
        return self._result
    
    @property
    def running(self) -> bool:
        return self._running
    
    # -------------------------------------------------------------------------
    # life cycle
    
    # decorators
    def started(self, callback: FunctionType) -> None:
        self._started_callbacks[_get_func_id(callback)] = callback
    
    def updated(self, callback: FunctionType) -> None:
        self._updated_callbacks[_get_func_id(callback)] = callback
    
    def finished(self, callback: FunctionType) -> None:
        self._finished_callbacks[_get_func_id(callback)] = callback
    
    def cancelled(self, callback: FunctionType) -> None:
        self._cancelled_callbacks[_get_func_id(callback)] = callback
    
    def crashed(self, callback: FunctionType) -> None:
        self._crashed_callbacks[_get_func_id(callback)] = callback
    
    # methods
    def start(self) -> None:
        self._over = False
        self._running = True
        for f in self._started_callbacks.values():
            f()
    
    def update(self, datum: t.Any) -> None:
        for f in self._updated_callbacks.values():
            f(datum)
    
    def finish(self) -> None:
        self._over = True
        self._running = False
        for f in self._finished_callbacks.values():
            f()
    
    def cancel(self) -> None:
        self._over = True
        self._running = False
        for f in self._cancelled_callbacks.values():
            f()
    
    def crash(self, error: Exception) -> None:
        self._over = True
        self._running = False
        if self._crashed_callbacks:
            for f in self._crashed_callbacks.values():
                f(error)
        else:
            print(':e', error)
            print(':v4', 'task broken!', self.id)
    
    # -------------------------------------------------------------------------
    
    def join(self, timeout: float = 60, interval: float = 10e-3) -> None:
        if self.over is None:
            for _ in sync_wait(1, 10e-3):
                if self.over is not None:
                    break
            else:
                raise Exception('task never starts')
        for _ in sync_wait(timeout, interval):
            if self.over:
                break
    
    def partial(self, *args, **kwargs) -> t.Self:
        """
        usage:
            @coro_mgr().partial(123)
            def foo(num: int, name: str):
                print(num, name)
            foo('alice')  # -> 123 alice
        """
        self._partial_args = args
        self._partial_kwargs = kwargs
        return self
    
    # def reset_status(self) -> None:
    #     self._over = False
    #     self._result = _unfinish
    #     self._running = False
    
    def run(self, *args, **kwargs) -> None:
        # self.reset_status()
        self.start()
        args, kwargs = self._finalize_arguments(*args, **kwargs)
        try:
            pending_result = self._target_func(*args, **kwargs)
        except Exception as e:
            self.crash(e)
            return
        if isinstance(pending_result, GeneratorType):
            coro_mgr.add_to_running_loop(self, pending_result)
        else:
            print(
                '[yellow dim]task is not awaitable, '
                'the result is returned immediately.[/]',
                ':pr'
            )
            final_result = pending_result
            self.update(final_result)
            self.finish()
        # return self
    
    def _finalize_arguments(self, *args, **kwargs) -> t.Tuple[tuple, dict]:
        if self._target_inst:
            final_args = (self._target_inst,) + self._partial_args + args
        else:
            final_args = self._partial_args + args
        if self._partial_kwargs:
            final_kwargs = {**self._partial_kwargs, **kwargs}
        else:
            final_kwargs = kwargs
        return final_args, final_kwargs


class CoroutineManager:
    _curr_task: t.Optional[Task]
    _mainloop_thread: Thread
    _running: bool
    _running_tasks: t.Dict[str, t.Tuple[Task, t.Iterator]]
    _tasks: t.Dict[str, Task]
    _timer: t.Dict[str, float]  # {task_id: time_point, ...}
    
    def __init__(self) -> None:
        self._tasks = {}
        self._running = False
        self._running_tasks = {}
        self._curr_task = None
        self._timer = {}
        self._mainloop_thread = Thread(
            target=asyncio.run, args=(self._mainloop(),), daemon=True
        )
        self._mainloop_thread.start()
    
    def __call__(
        self,
        name: str = None,
        singleton: bool = True,  # TODO
    ) -> t.Callable[[FunctionType], Task]:
        def decorator(func: FunctionType) -> Task:
            nonlocal name
            if name is None:
                name = _get_func_id(func)
            task = self._tasks[name] = Task(name, func, singleton)
            return task
        
        return decorator
    
    @property
    def pause(self) -> _Pause:
        return pause
    
    def add_to_running_loop(self, task: Task, iterator: t.Iterator) -> None:
        self._timer[task.id] = 0  # clear its timer
        self._running_tasks[task.id] = (task, iterator)
    
    def cancel(self, task_or_id: t.Union[Task, str]) -> bool:
        """
        returns:
            True: the task is running or run over, then be canceled.
            False: the task is not running.
        """
        if isinstance(task_or_id, Task):
            task = task_or_id
        else:
            task = self._tasks[task_or_id]
        if task.running:
            task.cancel()
            return True
        return False
    
    @staticmethod
    def join(task: Task) -> None:
        task.join()
        
    def join_all(self) -> None:
        self._running = False
        self._mainloop_thread.join()
        print(':tp', 'all tasks done')
    
    def sleep(self, sec: float) -> _Pause:
        """
        usage:
            def your_func():
                ...
                yield coro_mgr.sleep(1)
        """
        assert sec >= 1e-3, 'sleep time must be greater than 1ms'
        assert self._curr_task is not None
        assert not self._timer.get(self._curr_task.id)  # either 0 or None.
        #   if assertion error, you may not yield `coro_mgr.sleep` in your
        #   function.
        after_time = time.time() + sec
        self._timer[self._curr_task.id] = after_time
        return pause
    
    def wait(self, timeout: float, interval: float) -> t.Iterator[_Pause]:
        # mimic: `lk_utils.time_utils.time.wait`
        assert self._curr_task
        count = int(timeout / interval)
        for _ in range(count):
            yield self.sleep(interval)
        raise TimeoutError(f'timeout in {timeout} seconds (with {count} loops)')
    
    # -------------------------------------------------------------------------
    # delegate task life cycle (decorators)
    # fmt:off
    
    @staticmethod
    def on(
        task: Task, handle_crash: bool = False
    ) -> t.Callable[[FunctionType], FunctionType]:
        # noinspection PyTypeChecker
        def decorator(
            func: t.Callable[[str, t.Any], t.Any]
        ) -> t.Callable[[str, t.Any], t.Any]:
            """
            func:
                def <func>(state: str, value) -> any:
                    state: 'start' | 'update' | 'finish' | 'cancel' | 'crash'
                    value: depend on the state:
                        state   value
                        ------  ---------
                        start   None
                        update  any
                        finish  None
                        cancel  None
                        crash   Exception
            """
            task.started(partial(func, 'start', None))
            task.updated(partial(func, 'update'))
            task.finished(partial(func, 'finish', None))
            task.cancelled(partial(func, 'cancel', None))
            if handle_crash:
                task.crashed(partial(func, 'crash'))
            return func
        # noinspection PyTypeChecker
        return decorator
    
    @staticmethod
    def on_start(task: Task) -> t.Callable[[FunctionType], FunctionType]:
        def decorator(func: FunctionType) -> FunctionType:
            task.started(func)
            return func
        return decorator
    
    @staticmethod
    def on_update(task: Task) -> t.Callable[[FunctionType], FunctionType]:
        def decorator(func: FunctionType) -> FunctionType:
            task.updated(func)
            return func
        return decorator
    
    @staticmethod
    def on_finish(task: Task) -> t.Callable[[FunctionType], FunctionType]:
        def decorator(func: FunctionType) -> FunctionType:
            task.finished(func)
            return func
        return decorator
    
    @staticmethod
    def on_cancel(task: Task) -> t.Callable[[FunctionType], FunctionType]:
        def decorator(func: FunctionType) -> FunctionType:
            task.cancelled(func)
            return func
        return decorator
    
    @staticmethod
    def on_crash(task: Task) -> t.Callable[[FunctionType], FunctionType]:
        def decorator(func: FunctionType) -> FunctionType:
            task.crashed(func)
            return func
        return decorator
    
    # fmt:on
    # -------------------------------------------------------------------------
    
    async def _mainloop(self) -> None:
        finished_ids = []
        
        self._running = True
        while True:
            if not self._running_tasks:
                if self._running:
                    await asyncio.sleep(10e-3)
                    continue
                else:
                    break
            
            finished_ids.clear()
            self._curr_task = None
            
            for id, (task, iter) in self._running_tasks.items():
                # print(id, task, task.done, iter, id in self._timer, ':lv')
                if task.over:
                    finished_ids.append(id)
                    continue
                
                if s := self._timer.get(id):
                    await asyncio.sleep(1e-3)
                    # await asyncio.sleep(1)  # TEST
                    if time.time() < s:
                        continue
                    del self._timer[id]
                
                self._curr_task = task
                try:
                    for x in iter:
                        if x is pause:
                            break
                        else:
                            task.update(x)
                    else:
                        task.finish()
                except Exception as e:
                    task.crash(e)
                    finished_ids.append(id)
            
            for id in finished_ids:
                del self._running_tasks[id]


def _get_func_id(func: FunctionType) -> str:
    # mimic: `lk_utils.binding.signal._get_func_id`
    if isinstance(func, partial):
        func = func.func
    return '<{} at {}:{}>'.format(
        func.__qualname__,
        func.__code__.co_filename,
        func.__code__.co_firstlineno,
    )


coro_mgr = CoroutineManager()

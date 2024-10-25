import asyncio
import time
import typing as t
from collections import deque
from functools import partial
from threading import Thread
from types import FunctionType
from types import GeneratorType

from ..time_utils import wait as sync_wait


class _Pause:
    pass


# class _Unfinish:
#     def __bool__(self) -> bool:
#         return False


pause = _Pause()
# _unfinish = _Unfinish()


class Task:
    class Result:
        class _Unfinish:
            def __bool__(self) -> bool:
                return False
            
        unfinish = _Unfinish()
        
        def __init__(self) -> None:
            self._list = []
        
        def get(self) -> t.Any:
            if self._list:
                if len(self._list) == 1:
                    return self._list[0]
                return self._list
            # return None
            return self.unfinish
        
        def put(self, value: t.Any) -> None:
            self._list.append(value)
        
        # def set(self, value: t.Any) -> None:
        #     self._list.append(value)
        
        def reset(self) -> None:
            self._list.clear()
    
    def __init__(self, id: str, func: FunctionType, singleton: bool) -> None:
        self._cancelled_callbacks = {}
        self._crashed_callbacks = {}
        self._finished_callbacks = {}
        self._id = id
        self._over = None  # True, False, None
        self._partial_args = ()
        self._partial_kwargs = None
        self._result = Task.Result()
        self._rolls = deque()
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
        return self._result.get()
    
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
        self._result.reset()
        for k in tuple(self._started_callbacks.keys()):
            self._started_callbacks[k]()
    
    def update(self, datum: t.Any) -> None:
        self._result.put(datum)
        for k in tuple(self._updated_callbacks.keys()):
            self._updated_callbacks[k](datum)
    
    def finish(self) -> None:
        self._over = True
        self._running = False
        for k in tuple(self._finished_callbacks.keys()):
            self._finished_callbacks[k]()
    
    def cancel(self) -> None:
        self._over = True
        self._running = False
        for k in tuple(self._cancelled_callbacks.keys()):
            self._cancelled_callbacks[k]()
    
    def crash(self, error: Exception) -> None:
        self._over = True
        self._running = False
        if self._crashed_callbacks:
            for k in tuple(self._crashed_callbacks.keys()):
                self._crashed_callbacks[k](error)
        else:
            print(':e', error)
            print(':v4', 'task broken!', self.id)
    
    # -------------------------------------------------------------------------
    
    def join(self, timeout: float = 60, interval: float = 10e-3) -> t.Any:
        if self.over is None:
            for _ in sync_wait(100e-3, 1e-3):
                if self.over is not None:
                    break
            else:
                raise Exception('task never starts')
        for _ in sync_wait(timeout, interval):
            if self.over:
                break
        return self.result
    
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
    
    def run(self, *args, **kwargs) -> None:
        if self._running:
            # add fuel to self._rolls
            args, kwargs = self._finalize_arguments(*args, **kwargs)
            try:
                pending_result = self._target_func(*args, **kwargs)
            except Exception as e:
                self.crash(e)
            else:
                assert isinstance(pending_result, GeneratorType)
                self._rolls.append(pending_result)
            finally:
                return
        
        # self.reset_status()
        self.start()
        args, kwargs = self._finalize_arguments(*args, **kwargs)
        try:
            pending_result = self._target_func(*args, **kwargs)
        except Exception as e:
            self.crash(e)
            return
        if isinstance(pending_result, GeneratorType):
            self._rolls.append(pending_result)
            coro_mgr.add_to_running_loop(self, self._rollup())
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
    
    def _rollup(self) -> t.Iterator:
        while self._rolls:
            bucket = self._rolls.popleft()
            yield from bucket
    

class CoroutineManager:
    _curr_task: t.Optional[Task]
    _killed: bool
    # _mainloop_task: asyncio.Task
    _mainloop_thread: Thread
    # _mainloop_thread: t.Coroutine
    #   the main thread should be:
    #       1. run at once
    #       2. interruptible by ctrl-c
    #       3. access class attributes
    _running: bool
    _running_tasks: t.Dict[str, t.Tuple[Task, t.Iterator]]
    _tasks: t.Dict[str, Task]
    _timer: t.Dict[str, float]  # {task_id: time_point, ...}
    
    def __init__(self) -> None:
        self._curr_task = None
        self._killed = False
        self._running = False
        self._running_tasks = {}
        self._tasks = {}
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
    
    def cancel(self, task: Task) -> bool:
        """
        returns:
            True: the task is running or run over, then be canceled.
            False: the task is not running.
        """
        if task.running:
            task.cancel()
            return True
        return False
    
    @staticmethod
    def join(task: Task) -> t.Any:
        return task.join()
    
    def join_all(self) -> None:
        self._running = False
        # print(self._running)
        """
        how to use `ctrl+c` to stop a thread?
            ref: https://stackoverflow.com/a/3788243/9695911
            since thread cannot receive KeyboardInterrupt signal (by ctrl + c),
            we must listen to the signal in main thread.
            while `Thread.join()` blocks main thread, which prevent us to
            switch to main thread to listen, we need to tell thread to "sleep"
            so that main thread gets a breath.
            the simple way to tell thread to "sleep" is:
                while True:
                    <thread>.join(<timeout>)
            when timeout reaches, it briefly releases the lock.
        """
        while True:
            self._mainloop_thread.join(10e-3)
            if not self._mainloop_thread.is_alive():
                break
        print(':tp', 'all tasks done')
    
    def kill(self, *args) -> None:
        print(':v4s', 'force kill', args)
        self._killed = True
        self._mainloop_thread.join()
        # raise SystemExit
    
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
    
    def wait(self, timeout: float, interval: float) -> t.Iterator[float]:
        # mimic: `lk_utils.time_utils.time.wait`
        assert self._curr_task
        count = int(timeout / interval)
        for i in range(count):
            self.sleep(interval)
            # yield i
            yield (i + 1) / count
        raise TimeoutError(f'timeout in {timeout} seconds (with {count} loops)')
    
    # -------------------------------------------------------------------------
    # delegate task life cycle (decorators)
    # fmt:off
    
    @staticmethod
    def on(
        task: Task, handle_cancel: bool = True, handle_crash: bool = False
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
            if handle_cancel:
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
        # print(':dv')
        finished_ids = []
        
        self._running = True
        while True:
            if self._killed:
                break
            if not self._running_tasks:
                if self._running:
                    await asyncio.sleep(1e-3)
                    # await asyncio.sleep(10e-3)
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

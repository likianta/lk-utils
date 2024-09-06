import asyncio
import typing as t
from functools import partial
from threading import Thread
from time import time
from types import FunctionType
from types import GeneratorType

from ..binding import Signal


class _Pause:
    pass


class _Unfinish:
    def __bool__(self) -> bool:
        return False


pause = _Pause()
_unfinish = _Unfinish()


class Task:
    def __init__(self, id: str, func: FunctionType, singleton: bool) -> None:
        self.success = Signal()  # DELETE?
        self.error = Signal()
        self._id = id
        self._func = func
        self._singleton = singleton
        self._result = _unfinish
        self._running = False
        self._done = False
        self._partial_args = ()
        self._partial_kwargs = None
        self._final_args = ()
        self._final_kwargs = {}
    
    @property
    def done(self) -> bool:
        return self._done
    
    @property
    def id(self) -> str:
        return self._id
    
    # @cached_property
    # def interruptible(self) -> bool:
    #     return isinstance(self._func, GeneratorType)
    
    @property
    def result(self) -> t.Any:
        return self._result
    
    @property
    def running(self) -> bool:
        return self._running
    
    # -------------------------------------------------------------------------
    # life cycle
    
    # callbacks holder
    _started_callbacks: t.List[FunctionType]
    _updated_callbacks: t.List[FunctionType]
    _finished_callbacks: t.List[FunctionType]
    _cancelled_callbacks: t.List[FunctionType]
    _crashed_callbacks: t.List[FunctionType]
    
    # decorators
    def started(self, callback: FunctionType) -> None:
        pass
    
    def updated(self, callback: FunctionType) -> None:
        pass
    
    def finished(self, callback: FunctionType) -> None:
        pass
    
    def cancelled(self, callback: FunctionType) -> None:
        pass
    
    def crashed(self, callback: FunctionType) -> None:
        pass
    
    # methods
    def start(self) -> None:
        pass
    
    def update(self) -> None:
        pass
    
    def finish(self) -> None:
        pass
    
    def cancel(self) -> None:
        pass
    
    def crash(self) -> None:
        pass
    
    # -------------------------------------------------------------------------
    
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
    
    def finalize(self, *args, **kwargs) -> None:
        self._final_args = self._partial_args + args
        self._final_kwargs = kwargs if not self._partial_kwargs else \
            {**self._partial_kwargs, **kwargs}
        
    def call(self, *args, **kwargs):
        self.finalize(*args, **kwargs)
        pending_result = self._func(*self._final_args, **self._final_kwargs)
        if isinstance(pending_result, GeneratorType):
            pass
    
    def run(self) -> t.Iterator:
        # self.reset_status()
        pending_result = self._func(*self._final_args, **self._final_kwargs)
        if isinstance(pending_result, GeneratorType):
            result = []
            for x in pending_result:
                if x is not pause:
                    result.append(x)
                yield x
            self._result = result
        else:
            self._result = pending_result
        self._running = False
        self._done = True
        # print('task done')
    
    def force_stop(self) -> None:
        self.error.clear()
        self.success.clear()
        self._done = True
        self._running = False
    
    def reset_status(self) -> None:
        self.error.clear()
        self.success.clear()
        self._done = False
        self._result = _unfinish
        self._running = False


class CoroutineManager:
    _curr_task: t.Optional[Task]
    _running_tasks: t.Dict[str, t.Tuple[Task, t.Iterator]]
    _tasks: t.Dict[str, Task]
    _timer: t.Dict[str, float]  # {task_id: time_point, ...}
    
    def __init__(self) -> None:
        self._tasks = {}
        self._running_tasks = {}
        self._curr_task = None
        self._timer = {}
        Thread(
            target=asyncio.run, args=(self._mainloop(),), daemon=True
        ).start()
    
    def __call__(
        self,
        name: str = None,
        singleton: bool = True,
        #   TODO: should we use `singleton` or `run(..., reuse=True)`?
    ) -> t.Callable[[FunctionType], Task]:
        def decorator(func: FunctionType) -> Task:
            nonlocal name
            if name is None:
                name = self._get_func_id(func)
            task = self._tasks[name] = Task(name, func, singleton)
            return task
        
        return decorator
    
    @property
    def pause(self) -> _Pause:
        return pause
    
    def run(self, task: Task, *args, reuse: bool = False, **kwargs) -> None:
        if reuse and task.id in self._running_tasks:
            return
        print('run task', task, ':p')
        task.finalize(*args, **kwargs)
        task.reset_status()
        self._timer[task.id] = 0  # clear its timer
        self._running_tasks[task.id] = (task, task.run())
    
    def cancel(self, task_or_id: t.Union[Task, str]) -> bool:
        """
        returns:
            True: the task is running or run over, then be canceled.
            False: the task is not running.
        """
        if isinstance(task_or_id, Task):
            id = task_or_id.id
        else:
            id = task_or_id
        if id in self._running_tasks:
            del self._running_tasks[id]
            return True
        return self._tasks[id].done
    
    def wait(self, timeout: float, interval: float) -> t.Iterator[_Pause]:
        # mimic: `lk_utils.time_utils.time.wait`
        assert self._curr_task
        count = int(timeout / interval)
        for _ in range(count):
            yield self.sleep(interval)
        raise TimeoutError(f'timeout in {timeout} seconds (with {count} loops)')
    
    def sleep(self, sec: float) -> _Pause:
        """
        usage:
            def your_func():
                ...
                yield coro_mgr.sleep(1)
        """
        assert sec >= 1e-3, 'sleep time must be greater than 1ms'
        assert self._curr_task is not None
        assert self._curr_task.id not in self._timer
        #   if assertion error, you may not yield `coro_mgr.sleep` in your
        #   function.
        after_time = time() + sec
        self._timer[self._curr_task.id] = after_time
        return pause
    
    @staticmethod
    def _get_func_id(func: FunctionType) -> str:
        # mimic: `lk_utils.binding.signal._get_func_id`
        if isinstance(func, partial):
            func = func.func
        return '<{} at {}:{}>'.format(
            func.__qualname__,
            func.__code__.co_filename,
            func.__code__.co_firstlineno,
        )
    
    async def _mainloop(self) -> None:
        finished_ids = []
        
        while True:
            if not self._running_tasks:
                await asyncio.sleep(10e-3)
                continue
            
            finished_ids.clear()
            self._curr_task = None
            
            for id, (task, iter) in self._running_tasks.items():
                # print(id, task, task.done, iter, id in self._timer, ':lv')
                if task.done:
                    finished_ids.append(id)
                    continue
                
                if s := self._timer.get(id):
                    # await asyncio.sleep(1e-3)
                    await asyncio.sleep(1)  # TEST
                    if time() < s:
                        continue
                    del self._timer[id]
                
                self._curr_task = task
                try:
                    for x in iter:
                        if x is pause:
                            break
                
                except Exception as e:
                    print(':e', e)
                    print(':v4', 'task broken!', task.id)
                    task.force_stop()
                    finished_ids.append(id)
            
            for id in finished_ids:
                del self._running_tasks[id]


coro_mgr = CoroutineManager()

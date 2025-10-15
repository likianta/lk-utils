import typing as t
from contextlib import contextmanager
from dataclasses import dataclass
from time import sleep
from time import time
from types import GeneratorType
from .threading import new_thread


class Activity:
    state: t.Literal['idle', 'running', 'paused', 'stopped', 'cancelled']
    _remark: str
    _task: t.Generator
    
    @property
    def running(self) -> bool:
        return self.state == 'running'
    
    def __init__(self, task: t.Generator, remark: str = '') -> None:
        self.state = 'idle'
        self._remark = remark or str(task)
        self._task = task
    
    def __next__(self) -> t.Generator:
        assert self.state == 'running'
        return next(self._task)
    
    def __str__(self) -> str:
        return self._remark
    
    def start(self) -> t.Self:
        self.state = 'running'
        return self
    
    def pause(self) -> None:
        self.state = 'paused'
    
    def resume(self) -> None:
        # assert self.state == 'paused'
        # assert self.state not in ('stopped', 'cancelled')
        self.state = 'running'
    
    def stop(self) -> None:
        # currently this state is equal to "paused"
        self.state = 'stopped'
    
    def cancel(self) -> None:
        self.state = 'cancelled'
        # wait for background loop to recycle it.


class BackgroundActivities:
    busy: bool
    _activities: t.Dict[int, Activity]
    _timer: t.Dict[int, float]
    
    def __init__(self) -> None:
        self.busy = False
        self._activities = {}
        self._timer = {}
        self._mainloop()
    
    def close(self) -> None:
        self._activities.clear()
        self._timer.clear()
    
    @staticmethod
    def delay(sec: t.Union[int, float]) -> '_Delay':
        """
        usage:
            def mytask():
                while True:
                    ...
                    yield bg.delay(10)
            act = bg.register_activity(mytask()).start()

        suggestion:
            if your task needs long delay (e.g. >=1s), use this function; else -
            no need to use -- just follow the background loop's schedule.
        """
        return _Delay(sec)
    
    def register_activity(
        self, task: t.Generator, remark: str = ''
    ) -> Activity:
        assert isinstance(task, GeneratorType)
        act = self._activities[id(task)] = Activity(task, remark)
        return act
    
    @contextmanager
    def suspending(self) -> t.Iterator:
        """
        suspend all background activities.
        """
        self.busy = True
        yield
        self.busy = False
    
    # def unregister_activity(self, task_id: int) -> None:
    #     self._activities.pop(task_id)
    
    @new_thread()
    def _mainloop(self) -> None:
        while True:
            if self.busy or not self._activities:
                sleep(3)
                continue
            
            for id in tuple(self._activities.keys()):
                # print(id, ':iv')
                if self._timer.get(id):
                    if time() > self._timer[id]:
                        self._timer.pop(id)
                    else:
                        sleep(10e-3)
                        continue
                
                act = self._activities.get(id)
                if act.state == 'running':
                    try:
                        if self.busy:  # check busy again, in the key point.
                            break
                        x = next(act)
                    except StopIteration:
                        print(':v7', 'remove finished activity', act)
                        self._activities.pop(id)
                    except RuntimeError as e:
                        if str(e).lower() == 'signal source has been deleted':
                            print(':v8', 'entirely close backgroup loop')
                            self.close()
                            return
                    except Exception as e:
                        print(':e', e)
                        print(':v8', 'force remove broken activity', act)
                        self._activities.pop(id)
                    else:
                        if x and isinstance(x, _Delay):
                            self._timer[id] = time() + x.value
                    finally:
                        sleep(10e-3)
                elif act.state == 'cancelled':
                    print(':v7', 'recycle cancelled activity', act)
                    self._activities.pop(id)
            sleep(100e-3)


@dataclass
class _Delay:
    value: float


bg = BackgroundActivities()

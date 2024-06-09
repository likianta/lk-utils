"""
a wrapper for `rich.progress`.
"""
from contextlib import contextmanager
from typing import Iterator

import rich.progress

track = rich.progress.track


@contextmanager
def spinner(desc: str = 'working...') -> Iterator:
    # fix showing time elapsed for indeterminate progress
    # https://github.com/Textualize/rich/issues/1054
    cols = rich.progress.Progress.get_default_columns()
    cols[-1].elapsed_when_finished = True  # noqa
    with rich.progress.Progress(*cols) as prog:
        task = prog.add_task(desc, total=None)
        yield
        prog.update(task, total=1, completed=1)

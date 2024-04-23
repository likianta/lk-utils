if 1:
    import types  # noqa
    from types import *  # noqa
    from typing import *  # noqa
    from typing_extensions import *  # noqa

if 2:
    import sys
    import typing as _typing
    if sys.version_info[:2] < (3, 11):
        # fix the missing `Self` type in `typing` module
        setattr(_typing, 'Self', _typing.Any)

    if 'TextIO' not in globals():
        from typing.io import *  # noqa
    
    setattr(_typing, 'ContextHolder', _typing.Iterator)

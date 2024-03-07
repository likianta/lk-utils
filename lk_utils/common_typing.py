if 1:
    import types  # noqa
    from types import *  # noqa
    from typing import *  # noqa
    from typing_extensions import *  # noqa

if 2:
    import sys
    if sys.version_info[:2] < (3, 11):
        # fix the missing `Self` type in `typing` module
        import typing as _typing
        setattr(_typing, 'Self', _typing.Any)

if 3:
    if 'TextIO' not in globals():
        from typing.io import *

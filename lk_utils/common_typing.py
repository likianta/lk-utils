if 1:
    import types  # noqa
    from types import *  # noqa
    from typing import *  # noqa
    from typing_extensions import *  # noqa

if 2:
    if 'TextIO' not in globals():
        from typing.io import *

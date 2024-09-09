def compat_py38() -> None:
    fix_functools_cache()
    fix_typing_module()


# -----------------------------------------------------------------------------

def fix_functools_cache() -> None:
    """
    functools.cache is introduced since python 3.9. for 3.8 and earlier, we use
    functools.lru_cache instead.
    """
    import functools
    if not hasattr(functools, 'cache'):
        functools.cache = functools.lru_cache


def fix_typing_module() -> None:
    import sys
    from . import common_typing
    if sys.modules.get('typing') is not common_typing:
        sys.modules['typing'] = common_typing

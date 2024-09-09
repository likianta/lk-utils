import sys

_curr_version = sys.version_info[:2]

if _curr_version <= (3, 10):
    # python 3.8 ~ 3.10
    import types as _t0
    import typing as _t1
    import typing_extensions as _t2
    
    globals().update(_t0.__dict__)
    globals().update(_t1.__dict__)
    globals().update(_t2.__dict__)
    
    # if 'TextIO' not in globals():
    #     # noinspection PyUnresolvedReferences
    #     globals().update(_t1.io.__dict__)
    
    class _MildGenericType:
        def __init__(self, origin_type):
            self._origin = origin_type
        
        def __call__(self, *_, **__):
            return self
        
        def __getitem__(self, *args):
            try:
                return self._origin[args]
            except TypeError:
                # return self
                return self._origin[self]
    
    
    globals().update({
        'Optional': _MildGenericType(_t1.Optional),
        'Self'    : _t2.Self,
        'Union'   : _MildGenericType(_t1.Union),
    })

if _curr_version <= (3, 9):
    # python 3.8 ~ 3.9
    pass

if _curr_version <= (3, 8):
    # python 3.8 exclusive
    class _AnyType:
        pass
    
    
    globals()['_UnionGenericAlias'] = _AnyType

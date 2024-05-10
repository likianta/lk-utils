import importlib.util
import sys
from functools import partial
from os.path import basename
from os.path import exists
from os.path import isdir
from types import ModuleType


def _get_module(path: str, name: str = None) -> ModuleType:
    assert path.endswith('.py')
    if not name: name = basename(path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _get_package(path: str, name: str = None) -> ModuleType:
    """
    ref: https://stackoverflow.com/a/50395128
    """
    init_file = f'{path}/__init__.py'
    assert exists(init_file)
    if not name: name = basename(path)
    return _get_module(init_file, name)


def load(
    path: str,
    name: str = None,
    type: str = 'auto',  # 'auto', 'module', 'package'
    sync_sys_modules: bool = True,
) -> ModuleType:
    if not name: name = basename(path)
    if type == 'auto': type = 'package' if isdir(path) else 'module'
    out = _get_package(path) if type == 'package' else _get_module(path)
    if sync_sys_modules: sys.modules[name] = out
    return out


load_module = partial(load, type='module')
load_package = partial(load, type='package')

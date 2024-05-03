import importlib.util
import sys
from os.path import basename
from os.path import exists
from types import ModuleType


def get_module(path: str, name: str = None) -> ModuleType:
    assert path.endswith('.py')
    if not name: name = basename(path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def get_package(path: str, name: str = None) -> ModuleType:
    """
    ref: https://stackoverflow.com/a/50395128
    """
    init_file = f'{path}/__init__.py'
    assert exists(init_file)
    if not name: name = basename(path)
    return get_module(init_file, name)


def load_module(path: str, name: str = None) -> ModuleType:
    if not name: name = basename(path)
    out = sys.modules[name] = get_module(path, name)
    return out


def load_package(path: str, name: str = None) -> ModuleType:
    if not name: name = basename(path)
    out = sys.modules[name] = get_package(path)
    return out

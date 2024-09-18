from lk_utils import fs


def list_files() -> None:
    for f in fs.find_files('lk_utils'):
        print(
            f.path,
            f.relpath,
            f.name,
            f.stem,
            f.ext,
            f.dir,
        )
        #   for example:
        #       (
        #           'C:/Likianta/workspace/lk-utils/lk_utils/textwrap.csv',
        #           'textwrap.csv',
        #           'textwrap.csv',
        #           'textwrap',
        #           'csv',
        #           'C:/Likianta/workspace/lk-utils/lk_utils'
        #       )


def list_all_files() -> None:
    for f in fs.findall_files('lk_utils'):
        print(
            f.path,
            f.relpath,
            f.name,
            f.stem,
            f.ext,
            f.dir,
        )
        #   for example:
        #       (
        #           'C:/Likianta/workspace/lk-utils/lk_utils/textwrap.py',
        #           'textwrap.py',
        #           'textwrap.py',
        #           'textwrap',
        #           'py',
        #           'C:/Likianta/workspace/lk-utils/lk_utils'
        #       )
        #       ...
        #       (
        #           'C:/Likianta/workspace/lk-utils/lk_utils/binding/signal.py',
        #           'binding/signal.py',
        #           'signal.py',
        #           'signal',
        #           'py',
        #           'C:/Likianta/workspace/lk-utils/lk_utils/binding'
        #       )
        
        
def list_dirs() -> None:
    for d in fs.find_dirs('lk_utils'):
        print(
            d.path,
            d.relpath,
            d.name
        )
        #   for example:
        #       (
        #           'C:/Likianta/workspace/lk-utils/lk_utils/binding',
        #           'binding',
        #           'binding'
        #       )


def list_all_dirs() -> None:
    for d in fs.findall_dirs('lk_utils'):
        print(
            d.path,
            d.relpath,
            d.name
        )
        #   for example:
        #       (
        #           'C:/Likianta/workspace/lk-utils/lk_utils/binding',
        #           'binding',
        #           'binding'
        #       )
        #       ...
        #       (
        #           'C:/Likianta/workspace/lk-utils/lk_utils/filesniff',
        #           'filesniff',
        #           'filesniff'
        #       )


def list_python_files() -> None:
    for f in fs.find_files('lk_utils', '.py'):
        print(f.name)
        #   for example:
        #       '__init__.py'
        #       '__main__.py'
        #       'common_typing.py'
        #       'importer.py'
        #       ...


def get_parent_folder() -> None:
    print(fs.parent('lk_utils/filesniff/finder.py'))
    # -> 'lk_utils/filesniff'
    print(fs.parent('lk_utils/binding'))
    # -> 'lk_utils'

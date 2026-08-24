from neoprint import print

from lk_utils import fs
from lk_utils import manipulate_text
from lk_utils import slice_text

code = fs.load(fs.there('../lk_utils/__init__.py'))
# fmt: off
version = (
    slice_text(code)
    .find('__version__')
    .then_find(" = '").then_cut()
    .find("'").cut()
    .slice()
)
# fmt: on
print(version, ':ni3')
assert version == '3.8.0'

url = 'https://github.com/likianta/lk-utils'
project = slice_text(url).find('/likianta').end().move(1).slice()
print(project, ':ni3')
assert project == 'lk-utils'

file = fs.here('./semantic_slicer.py')
ext1 = slice_text(file).rfind('.').end().cut().slice()
ext2 = slice_text(file).rfind('.').end().slice()
print(ext1, ext2, ':ni3')
assert ext1 == ext2 == 'py'

link = '![](docs/images/151542.png)'
path = slice_text(link).find('(').then_cut().rfind(')').part()
print(path, ':ni3')
assert path == 'docs/images/151542.png'

time0 = '2026-07-24T08:11:00.908914Z'
time1 = manipulate_text(time0).cut().rfind('.').cut().inplace('T', ' ').part()
print(time1, ':ni3')
assert time1 == '2026-07-24 08:11:00'

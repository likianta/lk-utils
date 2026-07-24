from neoprint import print

from lk_utils import fs
from lk_utils import slice

code = fs.load(fs.there('../lk_utils/__init__.py'))
# fmt: off
version = (
    slice(code)
    .find('__version__').end()
    .find(" = '").end().cut()
    .find("'").cut()
    .slice()
)
# fmt: on
print(version, ':ni3')
assert version == '3.7.4'

url = 'https://github.com/likianta/lk-utils'
project = slice(url).find('/likianta').end().move(1).slice()
print(project, ':ni3')
assert project == 'lk-utils'

file = fs.here('./semantic_slicer.py')
ext1 = slice(file).rfind('.').end().cut().slice()
ext2 = slice(file).rfind('.').end().slice()
print(ext1, ext2, ':ni3')
assert ext1 == ext2 == 'py'

link = '![](docs/images/151542.png)'
path = slice(link).find('(').end().cut().rfind(')').out()
print(path, ':ni3')
assert path == 'docs/images/151542.png'

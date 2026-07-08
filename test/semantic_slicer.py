from lk_utils import fs
from lk_utils import regex as re
from neoprint import print

code = fs.load(fs.there('../lk_utils/__init__.py'))
# fmt: off
version = (
    re.SemanticSlicer(code)
    .find('__version__').end()
    .find(" = '").end().cut()
    .find("'").cut()
    .slice()
)
# fmt: on
print(version, ':ni')

url = 'https://github.com/likianta/lk-utils'
project = re.slice(url).find('/likianta').move(1).slice()
print(project, ':ni')

file = fs.here('./semantic_slicer.py')
ext1 = re.slice(file).rfind('.').end().cut().slice()
ext2 = re.slice(file).rfind('.').end().slice()
print(ext1, ext2, ':ni')

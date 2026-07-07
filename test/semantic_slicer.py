from lk_utils import fs
from lk_utils import regex as re
from neoprint import print

code = fs.load(fs.there('../lk_utils/__init__.py'))
version = (
    re.SemanticSlicer(code)
    .find('__version__').end()
    .find(" = '").end().cut()
    .find("'").cut()
    .slice()
)
print(version, ':n')

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
print(version, ':n')

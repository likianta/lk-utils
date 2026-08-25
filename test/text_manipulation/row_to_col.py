import difflib

from lk_utils import dump
from lk_utils import here
from lk_utils import load
from lk_utils import manipulate_text
from neoprint import print

text_i = load(here('row_in.qml'), 'plain')
# fmt: off
text_o = (
    manipulate_text(text_i)
    .prepend(
        '// This file was auto translated from ./Row.qml, please do not \n'
        '// modify it manuall.\n'
        '// Translator: sidework/translate_row_to_column.py\n\n'
    )
    .subx(r'\brow\.', r'column.')
    # update halign comment
    .find("halign: 'start'")
    .then_findx(r'// .+')
    .replace('// start, stretch, center')
    # update valign comment
    .then_find("valign: 'start'")
    .then_findx(r'// .+')
    .replace('// start, stretch')
    # translate `computeLayout` function
    .reset_index()
    .find('function computeLayout').then_find('return').end().cut()
    .find('V.Rectangle').cut()
    .swap('// horizontal', '// vertical')
    .swapx(r'root\.halign\b', r'root\.valign\b')
    .swap('.width', '.height')
    .swap('Width', 'Height')
    .swap('leftPadding', 'topPadding')
    .swap('rightPadding', 'bottomPadding')
    .replace('verticalCenter', 'horizontalCenter')
    # translate real container
    .find('V.Rectangle')
    .find('Row')
    .replace('Column')
    .then_find('id: row')
    .replace('id: column')
    # translate `onCompleted` stage
    .then_find('Component.onCompleted')
    .replace_all('row', 'column')
    .output()
)
# fmt: on

dump(text_o, here('col_out.qml'))

# diff = difflib.unified_diff(
#     text_i.splitlines(),
#     text_o.splitlines(),
#     fromfile='row_in.qml',
#     tofile='col_out.qml',
# )
# dump(diff, here('row_to_col_diff.txt'))

diff = difflib.HtmlDiff().make_file(text_i.splitlines(), text_o.splitlines())
dump(diff, here('row_to_col_diff.html'))
print('see "col_out.qml" and "row_to_col_diff.html"', ':v4')

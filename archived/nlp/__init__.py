print(':v3rp', '''
    [bold red]# Deprecation Warning[/]

    [magenta]lk_utils.nlp[/] package was deprecated since v2.2.0.
    It will be removed in v3.0.0.
''')

try:
    import pypinyin
except ImportError as e:
    print(':v4p', 'Make sure the following packages are installed: '
                  'pypinyin')
    print(':v4p', 'If not installed, `(module) chinese_name_processor > '
                  '(class) HanzProcessor > (method) chinese_name_to_pinyin` is '
                  'not available to use.')
    # raise e

from . import char_converter
from . import chinese_name_processor
from . import name_formatter
from . import tree_and_trie

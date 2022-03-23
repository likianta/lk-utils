print(':v3rp', '''
    [bold red]# Deprecation Warning[/]
    
    [magenta]lk_utils.excel[/] package was deprecated since v2.2.0.
    We recommend you to have a try with [!rainbow]pyexcel[/!rainbow]:
    
    [blue]https://github.com/pyexcel/pyexcel[/]
    
    [magenta]lk_utils.excel[/] will be removed in v3.0.0.
''')

try:
    import xlrd
    import xlsxwriter
except ImportError as e:
    print(':v4p', 'Make sure the following packages are installed: '
                  'xlrd (== 1.2.0), xlsxwriter')
    raise e

from .excel_reader import ExcelReader
from .excel_writer import ExcelWriter

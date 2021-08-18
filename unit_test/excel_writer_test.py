import unittest

from lk_utils import ExcelWriter


class TestExcelWriter(unittest.TestCase):
    
    def test_sheet_creation(self):
        w = ExcelWriter('output.xlsx', sheet_name=None)
        w.add_new_sheet('sheet 1')
    
    def test_sheet_duplicately_creating(self):
        w = ExcelWriter('output.xlsx', sheet_name=None)
        w.add_new_sheet('sheet 2')
        with self.assertRaises(AssertionError):
            w.add_new_sheet('sheet 2')


if __name__ == '__main__':
    unittest.main()

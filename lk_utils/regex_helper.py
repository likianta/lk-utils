"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : regex_helper.py
@Created : 2019-06-24
@Updated : 2019-11-12
@Version : 1.0.2
@Desc    :
"""
from re import compile

digit_pattern = compile(r'\d+')

hanz_pattern = compile(r'[\u4e00-\u9fa5]+')
hanz_pattern_one = compile(r'[\u4e00-\u9fa5]')

word_pattern = compile(r'\w+')
word_pattern_one = compile(r'\w')
word_in_brackets = compile(r'\(\w+\)')

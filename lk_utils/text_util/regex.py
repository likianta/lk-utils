import re

from . import finder

Match = re.Match
SureMatch = finder.SureMatch

compile = finder.compile
match = finder.match
fullmatch = finder.fullmatch
search = finder.search
sub = re.sub

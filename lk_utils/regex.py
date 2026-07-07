import re
import typing as tp
from collections import defaultdict

_cache = {}
_pattern_counter = defaultdict(int)


class Match:
    _match_obj: tp.Optional[re.Match]

    def __init__(self, match_obj: tp.Optional[re.Match]) -> None:
        self._match_obj = match_obj

    def group(self, group: int = 0) -> tp.Optional[str]:
        return self._match_obj.group(group)  # type: ignore

    def groups(self) -> tp.Tuple[tp.Optional[str], ...]:
        return self._match_obj.groups()  # type: ignore

    def sure(self) -> 'SureMatch':
        assert self._match_obj is not None
        return SureMatch(self._match_obj)


class SureMatch(Match):
    _match_obj: re.Match

    def group(self, group: int = 0) -> str:
        return self._match_obj.group(group) or ''

    def groups(self) -> tp.Tuple[str, ...]:
        return self._match_obj.groups()


class Pattern:
    def __init__(self, pattern: str) -> None:
        self._pattern_obj = re.compile(pattern)

    def fullmatch(self, string: str) -> Match:
        return Match(self._pattern_obj.fullmatch(string))

    def match(self, string: str) -> Match:
        return Match(self._pattern_obj.match(string))

    def search(self, string: str) -> Match:
        return Match(self._pattern_obj.search(string))


def compile(pattern: str) -> Pattern:
    return Pattern(pattern)


def _auto_cache(func):
    def wrapper(pattern: str, string: str):
        if pattern in _cache:
            return getattr(_cache[pattern], func.__name__)(string)
        else:
            _pattern_counter[pattern] += 1
            if _pattern_counter[pattern] > 3:
                _cache[pattern] = compile(pattern)
                return getattr(_cache[pattern], func.__name__)(string)
            else:
                return func(pattern, string)

    return wrapper


def fullmatch(pattern: str, string: str) -> Match:
    return Match(re.fullmatch(pattern, string))


def match(pattern: str, string: str) -> Match:
    return Match(re.match(pattern, string))


def search(pattern: str, string: str) -> Match:
    return Match(re.search(pattern, string))


# ------------------------------------------------------------------------------


class SemanticSlicer:
    """
    example:
        text = open('__init__.py', 'r').read()
        #   there was a `__version__ = '0.1.0'` in the file, we want to extract
        #   it.
        version = (
            SemanticSlicer(text)
            .find("__version__ = '").end().cut()
            .find("'").cut()
            .slice()
        )
        assert version == '0.1.0'
    """

    def __init__(self, text: str) -> None:
        assert text
        self.text = text
        self._start_index = 0
        self._end_index = len(text)
        self._start_index_alt = 0
        self._end_index_alt = len(text)
        self._finding_start = True
        self._finding_end = False

    @property
    def determined(self) -> bool:
        return not self._finding_start and not self._finding_end

    @property
    def _alt_index(self) -> int:
        return (
            self._start_index_alt
            if self._finding_start
            else self._end_index_alt
        )

    @_alt_index.setter
    def _alt_index(self, idx: int) -> None:
        if self._finding_start:
            self._start_index_alt = idx
        elif self._finding_end:
            self._end_index_alt = idx
        else:
            raise Exception('slicing is done')

    @property
    def _current_index(self) -> int:
        return self._start_index if self._finding_start else self._end_index

    @_current_index.setter
    def _current_index(self, idx: int) -> None:
        if self._finding_start:
            self._start_index = idx
        elif self._finding_end:
            self._end_index = idx
        else:
            raise Exception('slicing is done')

    # --------------------------------------------------------------------------

    def cut(self) -> 'SemanticSlicer':
        if self._finding_start and not self._finding_end:
            self._finding_start = False
            self._finding_end = True
            self._end_index = self._start_index
        elif not self._finding_start and self._finding_end:
            self._finding_end = False
        else:
            raise Exception('cannot call `cut` more than twice!')
        return self

    def end(self) -> 'SemanticSlicer':
        self._current_index = self._alt_index
        return self

    def find(self, substring: str) -> 'SemanticSlicer':
        self._current_index += self.text[self._start_index :].index(substring)
        self._alt_index = self._current_index + len(substring)
        return self

    def move(self, offset: int) -> 'SemanticSlicer':
        self._current_index += offset
        assert self._current_index >= 0
        return self

    def rfind(self, substring: str) -> 'SemanticSlicer':
        self._current_index = self.text[self._start_index :].rindex(substring)
        self._alt_index = self._current_index + len(substring)
        return self

    def slice(self) -> str:
        return self.text[self._start_index : self._end_index]


def slice(text: str) -> SemanticSlicer:
    return SemanticSlicer(text)

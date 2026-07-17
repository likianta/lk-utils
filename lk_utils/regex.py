import re
import typing as tp
from collections import defaultdict

_cache = {}
_pattern_counter = defaultdict(int)


class Match:
    _match_obj: tp.Optional[re.Match]
    _remark: str

    def __init__(
        self, match_obj: tp.Optional[re.Match], _remark: str = ''
    ) -> None:
        self._match_obj = match_obj
        self._remark = _remark

    def group(self, group: int = 0) -> tp.Optional[str]:
        return self._match_obj.group(group)  # type: ignore

    def groups(self) -> tp.Tuple[tp.Optional[str], ...]:
        return self._match_obj.groups()  # type: ignore

    def sure(self) -> 'SureMatch':
        assert self._match_obj is not None, self._remark
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
        return Match(
            self._pattern_obj.fullmatch(string),
            'apply fullmatch pattern `{}` to string "{}"'.format(
                self._pattern_obj.pattern, string
            ),
        )

    def match(self, string: str) -> Match:
        return Match(
            self._pattern_obj.match(string),
            'apply match pattern `{}` to string "{}"'.format(
                self._pattern_obj.pattern, string
            ),
        )

    def search(self, string: str) -> Match:
        return Match(
            self._pattern_obj.search(string),
            'apply search pattern `{}` to string "{}"'.format(
                self._pattern_obj.pattern, string
            ),
        )


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
    return Match(
        re.fullmatch(pattern, string),
        'apply fullmatch pattern `{}` to string "{}"'.format(pattern, string),
    )


def match(pattern: str, string: str) -> Match:
    return Match(
        re.match(pattern, string),
        'apply match pattern `{}` to string "{}"'.format(pattern, string),
    )


def search(pattern: str, string: str) -> Match:
    return Match(
        re.search(pattern, string),
        'apply search pattern `{}` to string "{}"'.format(pattern, string),
    )

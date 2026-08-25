import typing as tp
# from builtins import slice as Span

from .finder import search


class CutPoint:
    def __init__(self, start: int = -1, end: int = -1):
        self.start = start
        self.start_pinned = False
        self.end = end
        self.end_alt = -1

    @property
    def span(self) -> tp.Tuple[int, int]:
        return self.start, self.end

    @property
    def valid(self) -> bool:
        return self.start != -1 and self.end != -1

    @property
    def partial_valid(self) -> bool:
        return self.start != -1 and self.end == -1

    def reset(self, text_reference: str = '') -> None:
        if text_reference:
            self.start = 0
            self.end = len(text_reference)
        else:
            self.start = -1
            self.end = -1


class TextSlicer:
    """
    doc: docs/efficiency-of-semantic-slicing.zh.md
    example:
        text = open('__init__.py', 'r').read()
        #   there was a `__version__ = '0.1.0'` in the file, we want to extract
        #   it.
        version = (
            TextSlicer(text)
            .find("__version__ = '").end().cut()
            .find("'").cut()
            .slice()
        )
        assert version == '0.1.0'
    """

    text: str
    _cut_point: CutPoint
    _partial_cut: bool

    def __init__(self, origin_text: str) -> None:
        assert origin_text
        self.text = origin_text
        self._cut_point = CutPoint()
        self._reset_indexes()

    @property
    def _partial_text(self) -> str:
        return self.text[self._cut_point.start : self._cut_point.end]

    @property
    def _partial_text_2(self) -> str:
        return self.text[self._cut_point.start :]

    # @property
    # def _span(self) -> Span:
    #     return Span(self._cut_point.start, self._cut_point.end)

    # @property
    # def _long_span(self) -> Span:
    #     return Span(self._cut_point.start, len(self.text))

    @property
    def _start(self) -> int:
        return self._cut_point.start

    @_start.setter
    def _start(self, index: int) -> None:
        self._cut_point.start = index

    @property
    def _end(self) -> int:
        return self._cut_point.end

    @_end.setter
    def _end(self, index: int) -> None:
        self._cut_point.end = index

    @property
    def _end_alt(self) -> int:
        return self._cut_point.end_alt

    @_end_alt.setter
    def _end_alt(self, index: int) -> None:
        self._cut_point.end_alt = index

    def _reset_indexes(
        self, _start: int = -1, _end: int = -1, _end_alt: int = -1
    ) -> None:
        if _start != -1 and _end != -1:
            self._start = _start
            self._end = _end
            self._end_alt = _end_alt if _end_alt != -1 else len(self.text)
        else:
            self._start = 0
            self._end = len(self.text)
            self._end_alt = -1
        self._partial_cut = False

    # --------------------------------------------------------------------------

    def cut(self) -> tp.Self:
        self._partial_cut = not self._partial_cut
        if self._partial_cut:
            self._end_alt = self._end
            self._end = self._start
        return self

    def find(self, substring: str) -> tp.Self:
        i = self._partial_text_2.index(substring)
        if self._partial_cut:
            self._end = self._start + i
            self._end_alt = self._end + len(substring)
        else:
            self._start += i
            self._end = self._start + len(substring)
        return self

    def findx(self, pattern):
        m = search(pattern, self._partial_text_2).sure()
        self._start += m.start()
        self._end = self._start + len(m.group())
        return self

    def move(self, offset: int) -> tp.Self:
        self._start += offset
        if self._end < self._start:
            self._end = self._start
        return self

    def move_end(self) -> tp.Self:
        if self._partial_cut:
            assert self._end_alt != -1
            self._end = self._end_alt
        else:
            self._start = self._end
            self._end = len(self.text)
        return self

    def reset_index(self) -> tp.Self:
        self._reset_indexes()
        return self

    def rfind(self, substring: str) -> tp.Self:
        i = self._partial_text_2.rindex(substring)
        if self._partial_cut:
            self._end = self._start + i
            self._end_alt = self._end + len(substring)
        else:
            self._start += i
            self._end = self._start + len(substring)
        return self

    def slice(self) -> str:
        if self._partial_cut:
            if self._end == self._start:
                return self._partial_text_2
        return self._partial_text

    def then_cut(self) -> tp.Self:
        self.move_end()
        self.cut()
        return self

    def then_find(self, target: str) -> tp.Self:
        self.move_end()
        self.find(target)
        return self

    def then_findx(self, pattern: str) -> tp.Self:
        self.move_end()
        self.findx(pattern)
        return self

    end = move_end
    # out = str = slice
    part = slice
    continue_find = then_find
    continue_findx = then_findx


def slice(text: str) -> TextSlicer:
    return TextSlicer(text)

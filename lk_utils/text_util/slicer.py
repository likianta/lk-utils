import typing as tp

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

    _start_index: int
    _end_index: int
    _start_index_alt: int
    _end_index_alt: int
    _finding_start: bool
    _finding_end: bool

    def __init__(self, text: str) -> None:
        assert text
        self.text = text
        self._cut_point = CutPoint()
        self._reset_indexes()

    @property
    def determined(self) -> bool:
        return not self._finding_start and not self._finding_end

    @property
    def start_index(self) -> int:
        return self._start_index

    @property
    def end_index(self) -> int:
        return self._end_index

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

    @property
    def _hit_the_end(self) -> bool:
        return self._end_index == len(self.text)

    @property
    def _just_about_to_find_end(self) -> bool:
        return self._end_index == self._start_index and self._finding_end

    # def _has_cut_point(self) -> bool:
    #     return self._finding_start and not self._finding_end

    def _reset_indexes(self, _cuz_start: int = -1, _cuz_end: int = -1) -> None:
        # if offset:
        #     assert offset < len(self.text)
        # if alt_offset == -1:
        #     alt_offset = offset
        # self._start_index = offset
        # self._end_index = len(self.text)
        # self._start_index_alt = alt_offset
        # self._end_index_alt = len(self.text)
        # self._finding_start = True
        # self._finding_end = False

        if _cuz_start != -1 and _cuz_end != -1:
            self._cut_point.start = _cuz_start
            self._cut_point.end = _cuz_end
        else:
            self._cut_point.reset(self.text)
        self._partial_cut = False

    # --------------------------------------------------------------------------

    def continue_find(self, target: str) -> tp.Self:
        self.move_end()
        self.find(target)
        return self

    def continue_findx(self, pattern: str) -> tp.Self:
        self.move_end()
        self.findx(pattern)
        return self

    def cut(self) -> tp.Self:
        # if self._cut_point.valid:
        #     raise Exception
        # elif self._cut_point.partial_valid:
        #     self._cut_point.end = self._cut_point.start
        # else:
        #     self._cut_point.start = self._cut_point.start
        #     # self._cut_point.end = self._cut_point.end
        self._partial_cut = not self._partial_cut
        return self

    def find(self, substring: str) -> tp.Self:
        i = self.text[self._cut_point.start:].index(substring)
        if self._partial_cut:
            self._cut_point.end = self._cut_point.start + i
            self._cut_point.end_alt = self._cut_point.end + len(substring)
        else:
            self._cut_point.start += i
            self._cut_point.end = self._cut_point.start + len(substring)
        return self

    def findx(self, pattern):
        m = search(pattern, self.text[self._cut_point.start :]).sure()
        self._cut_point.start += m.start()
        self._cut_point.end = self._cut_point.start + len(m.group())
        return self

    def move(self, offset: int) -> tp.Self:
        self._current_index += offset
        assert self._current_index >= 0
        return self

    def move_end(self) -> tp.Self:
        if self._partial_cut:
            assert self._cut_point.end_alt != -1
            self._cut_point.end = self._cut_point.end_alt
        else:
            self._cut_point.start = self._cut_point.end
        return self

    def reset_index(self) -> tp.Self:
        self._reset_indexes()
        return self

    def rfind(self, substring: str) -> tp.Self:
        self._current_index = self._start_index + self.text[
            self._start_index :
        ].rindex(substring)
        self._alt_index = self._current_index + len(substring)
        return self

    def slice(self) -> str:
        if self._just_about_to_find_end:
            return self.text[self._start_index :]
        return self.text[self._start_index : self._end_index]

    end = move_end
    out = str = slice
    then_find = continue_find
    then_findx = continue_findx


def slice(text: str) -> TextSlicer:
    return TextSlicer(text)

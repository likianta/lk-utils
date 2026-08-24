import re
import typing as tp

from .slicer import TextSlicer


class TextManipulator(TextSlicer):
    # @property
    # def _part_a(self) -> str:
    #     return self.text[: self._start]

    # @property
    # def _part_b(self) -> str:
    #     return self.text[self._start : self._end]

    # @property
    # def _part_c(self) -> str:
    #     return self.text[self._end :]

    # @property
    # def _part_d(self) -> str:
    #     return self.text[self._start :]

    def append(self, suffix: str) -> tp.Self:
        self.text += suffix
        return self

    def output(self) -> str:
        return self.text

    def prepend(self, prefix: str) -> tp.Self:
        self.text = prefix + self.text
        self._reset_indexes()
        return self

    def replace(
        self,
        x: str,
        _new: tp.Optional[str] = None,
        count: tp.Optional[int] = None,
    ) -> tp.Self:
        text_a, text_b, text_c = self._split(*self._cut_point.span)
        if _new is None:
            self.text = text_a + x + text_c
            self._end = self._start + len(x)
        else:
            text_d = text_b.replace(x, _new, count or -1)
            self.text = text_a + text_d + text_c
            self._end = self._start + len(text_d)
        return self

    def replace_all(
        self,
        x: str,
        _new: tp.Optional[str] = None,
        count: tp.Optional[int] = None,
    ) -> tp.Self:
        if _new is None:
            old, new = '...', x
        else:
            old, new = x, _new
        self.text = self.text[: self._start] + self.text[self._start :].replace(
            old, new, count or -1
        )
        return self

    def replacex(
        self,
        pattern: str,
        replacement: tp.Union[str, tp.Callable],
        count: tp.Optional[int] = None,
    ) -> tp.Self:
        text_a, text_b, text_c = self._split(*self._cut_point.span)
        text_b = re.sub(pattern, replacement, text_b, count=count or -1)
        self.text = text_a + text_b + text_c
        self._end = self._start + len(text_b)
        return self

    def replacex_all(
        self,
        pattern: str,
        replacement: tp.Union[str, tp.Callable],
        count: tp.Optional[int] = None,
    ) -> tp.Self:
        self.text = self.text[: self._start] + re.sub(
            pattern, replacement, self.text[self._start :], count=count or 0
        )
        return self

    def swap(self, a: str, b: str) -> tp.Self:
        text_a, text_b, text_c = self._split(*self._cut_point.span)
        text_b = text_b.replace(a, '◆◇◇◆').replace(b, a).replace('◆◇◇◆', b)
        self.text = text_a + text_b + text_c
        self._end = self._start + len(text_b)
        return self

    def swap_all(self, a: str, b: str) -> tp.Self:
        text_a = self.text[: self._start]
        text_b = self.text[self._start :]
        assert a in text_b and b in text_b, (text_b, a, b)
        text_c = text_b.replace(a, '◆◇◇◆').replace(b, a).replace('◆◇◇◆', b)
        self.text = text_a + text_c
        return self

    def swapx(self, pattern_a: str, pattern_b: str) -> tp.Self:
        text_a, text_b, text_c = self._swapx(
            *self._cut_point.span, pattern_a, pattern_b
        )
        self.text = text_a + text_b + text_c
        self._end = self._start + len(text_b)
        return self

    def swapx_all(self, pattern_a: str, pattern_b: str) -> tp.Self:
        result = self._swapx(self._start, len(self.text), pattern_a, pattern_b)
        self.text = ''.join(result)
        return self

    def _split(
        self, start: tp.Optional[int] = None, end: tp.Optional[int] = None
    ) -> tp.Tuple[str, str, str]:
        if start is None and end is None:
            start, end = self._start, self._end
        assert start <= end  # type: ignore
        return (self.text[:start], self.text[start:end], self.text[end:])

    def _swapx(
        self, start: int, end: int, pattern_a: str, pattern_b: str
    ) -> tp.Tuple[str, str, str]:
        text_a, text_b, text_c = self._split(start, end)

        def group_1_or_0(m: re.Match) -> str:
            try:
                return m.group(1)
            except IndexError:
                return m.group(0)

        typical_a = group_1_or_0(
            tp.cast(re.Match, re.search(pattern_a, text_b))
        )
        typical_b = group_1_or_0(
            tp.cast(re.Match, re.search(pattern_b, text_b))
        )

        text_b = re.sub(pattern_a, '◆◇◇◆', text_b)
        text_b = re.sub(pattern_b, typical_a, text_b)
        text_b = text_b.replace('◆◇◇◆', typical_b)
        return text_a, text_b, text_c

    inplace = replace
    inplace_all = replace_all
    inplacex = replacex
    inplacex_all = replacex_all
    sub = replace
    sub_all = replace_all
    subx = replacex
    subx_all = replacex_all


def manipulate(origin_text: str) -> TextManipulator:
    return TextManipulator(origin_text)


substitute = re.sub

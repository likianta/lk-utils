import re
import typing as tp

from .slicer import TextSlicer


class TextManipulator(TextSlicer):
    def __init__(self, origin_text: str) -> None:
        super().__init__(origin_text)

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
        text_a = self.text[: self._cut_point.start]
        text_b = self.text[self._cut_point.start : self._cut_point.end]
        text_c = self.text[self._cut_point.end :]

        if _new is None:
            self.text = text_a + x + text_c
            self._cut_point.end = self._cut_point.start + len(x)
        else:
            text_d = text_b.replace(x, _new, count or -1)
            self.text = text_a + text_d + text_c
            self._cut_point.end = self._cut_point.start + len(text_d)
        return self

        if len(args) == 1:
            new_str = args[0]  # type: ignore
            assert self._cut_point.valid
            self.text = (
                self.text[: self._cut_point.start]
                + new_str
                + self.text[self._cut_point.end :]
            )
            self._cut_point.end = self._cut_point.start + len(new_str)

        elif len(args) == 2:
            if isinstance(args[1], str):
                old_str, new_str = args  # type: ignore
                if self._has_cut_point():
                    if self._finding_end:
                        if self._just_about_to_find_end:
                            self.text = self.text[
                                : self._start_index
                            ] + self.text[self._end_index :].replace(
                                old_str, new_str
                            )
                        else:
                            self.text = (
                                self.text[: self._start_index]
                                + self.text[
                                    self._start_index : self._end_index
                                ].replace(old_str, new_str)
                                + self.text[self._end_index :]
                            )
                        self._reset_indexes(
                            # 0 if self._hit_the_end else self._end_index
                            alt_offset=self._end_index
                        )
                    else:
                        assert self._finding_start and self._start_index == 0
                        self.text = self.text.replace(old_str, new_str)
            else:  # isinstance(args[1], int)
                raise Exception(args)

        else:  # len(args) == 3
            old_str, new_str, cnt = args  # type: ignore
            if self._finding_end:
                if self._just_about_to_find_end:
                    self.text = self.text[: self._start_index] + self.text[
                        self._end_index :
                    ].replace(old_str, new_str, cnt)
                else:
                    self.text = (
                        self.text[: self._start_index]
                        + self.text[
                            self._start_index : self._end_index
                        ].replace(old_str, new_str, cnt)
                        + self.text[self._end_index :]
                    )
                self._reset_indexes(
                    # 0 if self._hit_the_end else self._end_index
                    alt_offset=self._end_index
                )
            else:
                assert self._finding_start and self._start_index == 0
                self.text = self.text.replace(old_str, new_str, cnt)

        return self

    def replace_all(
        self,
        x: str,
        _new: tp.Optional[str] = None,
        count: tp.Optional[int] = None,
    ):
        if _new is None:
            old, new = '...', x
        else:
            old, new = x, _new

        self.text = self.text[: self._cut_point.start] + self.text[
            self._cut_point.start :
        ].replace(old, new, count or -1)
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
        self._cut_point.end = self._cut_point.start + len(text_b)
        return self

    def replacex_all(
        self,
        pattern: str,
        replacement: tp.Union[str, tp.Callable],
        count: tp.Optional[int] = None,
    ) -> tp.Self:
        self.text = self.text[: self._cut_point.start] + re.sub(
            pattern,
            replacement,
            self.text[self._cut_point.start :],
            count=count or 0,
        )
        return self

    def swap(self, a: str, b: str) -> tp.Self:
        text_a, text_b, text_c = self._split(*self._cut_point.span)
        text_b = text_b.replace(a, '◆◇◇◆').replace(b, a).replace('◆◇◇◆', b)
        self.text = text_a + text_b + text_c
        self._cut_point.end = self._cut_point.start + len(text_b)
        return self

    def swap_all(self, a: str, b: str) -> tp.Self:
        text_a = self.text[: self._cut_point.start]
        text_b = self.text[self._cut_point.start :]
        assert a in text_b and b in text_b, (text_b, a, b)
        text_c = text_b.replace(a, '◆◇◇◆').replace(b, a).replace('◆◇◇◆', b)
        self.text = text_a + text_c
        return self

    def swapx(self, pattern_a: str, pattern_b: str) -> tp.Self:
        text_a, text_b, text_c = self._swapx(
            *self._cut_point.span, pattern_a, pattern_b
        )
        self.text = text_a + text_b + text_c
        self._cut_point.end = self._cut_point.start + len(text_b)
        return self

    def swapx_all(self, pattern_a: str, pattern_b: str) -> tp.Self:
        result = self._swapx(
            self._cut_point.start, len(self.text), pattern_a, pattern_b
        )
        self.text = ''.join(result)
        return self

    def _split(self, start: int, end: int) -> tp.Tuple[str, str, str]:
        assert start <= end
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
    sub = replace
    suball = replace_all
    subx = replacex
    subxall = replacex_all


def manipulate(origin_text: str) -> TextManipulator:
    return TextManipulator(origin_text)


substitute = re.sub

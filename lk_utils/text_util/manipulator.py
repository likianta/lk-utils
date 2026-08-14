import re
import typing as tp


class TextManipulator:
    def __init__(self, origin_text: str) -> None:
        self.text = origin_text

    def substitute(
        self, old: str, new: str, count: int = -1
    ) -> 'TextManipulator':
        self.text = self.text.replace(old, new, count)
        return self

    def substitutex(
        self,
        pattern: str,
        replacement: tp.Union[str, tp.Callable[[re.Match], str]],
    ) -> 'TextManipulator':
        self.text = re.sub(pattern, replacement, self.text)
        return self


def manipulate(origin_text: str) -> TextManipulator:
    return TextManipulator(origin_text)


substitute = re.sub

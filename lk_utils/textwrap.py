import textwrap
import typing as t


def dedent(text: str, lstrip: bool = True) -> str:
    out = textwrap.dedent(text).rstrip()
    if lstrip:
        out = out.lstrip()
    return out


def indent(text: str, spaces: int = 4) -> str:
    return textwrap.indent(text, ' ' * spaces).strip()


def reindent(text: str, spaces: int = 4) -> str:
    return indent(dedent(text), spaces)


def join(parts: t.Iterable[str], indent_: int = 0, sep: str = '\n') -> str:
    if indent_:
        return indent(sep.join(parts), indent_)
    return sep.join(parts)

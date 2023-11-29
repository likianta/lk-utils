import re
import textwrap

from . import common_typing as t


def dedent(text: str, lstrip: bool = True, join_sep: str = None) -> str:
    """
    params:
        join_sep: suggest '-' or '|'.
            notice for joiniing '\\', you should pass '\\\\' to `join_sep`. -
            for example:
                dedent(
                    '''
                        aaa \\
                        bbb
                    ''',
                    join_sep='\\\\'
                )
    """
    out = textwrap.dedent(text).rstrip()
    if join_sep:
        out = re.sub(rf' +{join_sep} *\n', ' ', out)
    return out.lstrip() if lstrip else out


def indent(text: str, spaces: int = 4, rstrip: bool = True) -> str:
    out = textwrap.indent(text, ' ' * spaces)
    return out.rstrip() if rstrip else out


def reindent(text: str, spaces: int = 4) -> str:
    return indent(dedent(text), spaces)


def join(
    parts: t.Iterable[str],
    indent_: int = 0,
    sep: str = '\n',
    lstrip: bool = True
) -> str:
    if indent_:
        out = indent(sep.join(parts), indent_)
        if lstrip:
            return out.lstrip()
        return out
    return sep.join(parts)

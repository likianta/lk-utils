import re
import textwrap as _tw
import typing as t


def wrap(
    text: str,
    indent: int = 0,
    lstrip: bool = True,
    rstrip: bool = True,
    join_sep: str = None,
    _dedent: bool = True,
) -> str:
    """
    params:
        join_sep: suggest '-', '|' or '\\'.
    """
    if _dedent:
        text = _tw.dedent(text)
    if lstrip:
        text = text.lstrip()
    if rstrip:
        text = text.rstrip()
    if join_sep:
        if '\\' in join_sep:
            # escape for regular expression
            join_sep = join_sep.replace('\\', '\\\\')
        text = re.sub(rf' +{join_sep} *\n *', ' ', text)
    if indent:
        text = _tw.indent(text, ' ' * indent)
    return text


dedent = wrap  # DELETE?


def join(
    parts: t.Iterable[str],
    indent: int = 0,
    sep: str = '\n',
    **kwargs
) -> str:
    text = sep.join(parts)
    if indent:
        text = wrap(text, indent, **kwargs).lstrip()
    return text

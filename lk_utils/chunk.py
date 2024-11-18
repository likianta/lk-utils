import typing as t


def chunkwise(
    seq: t.Union[list, tuple],
    n: int,
    prepad: int = 0,
    continous: bool = True,
) -> t.Iterator[tuple]:
    """
    split a sequence into chunks.
    example:
        seq = [1, 2, 3, 4]
        
        chunkwise(seq, 2, 0, True)
            -> (1, 2), (2, 3), (3, 4), (4, None)
        chunkwise(seq, 2, 1, True)
            -> (None, 1), (1, 2), (2, 3), (3, 4), (4, None)
        
        chunkwise(seq, 3, 0, True)
            -> (1, 2, 3), (2, 3, 4), (3, 4, None), (4, None, None)
        chunkwise(seq, 3, 1, True)
            -> (None, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, None), (4, None, None)
        
        chunkwise(seq, 2, 0, False)
            -> (1, 2), (3, 4)
        chunkwise(seq, 2, 1, False)
            -> (None, 1), (2, 3), (4, None)
        
        chunkwise(seq, 3, 0, False)
            -> (1, 2, 3), (4, None, None)
        chunkwise(seq, 3, 1, False)
            -> (None, 1, 2), (3, 4, None)
    """
    assert 0 <= prepad < n <= len(seq), (len(seq), n, prepad)
    seq_filled = (
        *((_placeholder,) * prepad),
        *seq,
        *((_placeholder,) * n)
    )
    for i in range(0, len(seq_filled), 1 if continous else n):
        chunk = seq_filled[i: i + n]
        if all(x is _placeholder for x in chunk):
            break
        yield (None if x is _placeholder else x for x in chunk)


class _Placeholder:
    pass


_placeholder = _Placeholder()

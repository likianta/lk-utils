class SemanticSlicer:
    """
    doc: docs/efficiency-of-semantic-slicing.zh.md
    example:
        text = open('__init__.py', 'r').read()
        #   there was a `__version__ = '0.1.0'` in the file, we want to extract
        #   it.
        version = (
            SemanticSlicer(text)
            .find("__version__ = '").end().cut()
            .find("'").cut()
            .slice()
        )
        assert version == '0.1.0'
    """

    text: str
    _start_index: int
    _end_index: int
    _start_index_alt: int
    _end_index_alt: int
    _finding_start: bool
    _finding_end: bool

    def __init__(self, text: str) -> None:
        assert text
        self.text = text
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

    def _reset_indexes(self) -> None:
        self._start_index = 0
        self._end_index = len(self.text)
        self._start_index_alt = 0
        self._end_index_alt = len(self.text)
        self._finding_start = True
        self._finding_end = False

    # --------------------------------------------------------------------------

    def cut(self) -> 'SemanticSlicer':
        if self._finding_start and not self._finding_end:
            self._finding_start = False
            self._finding_end = True
            self._end_index = self._start_index
        elif not self._finding_start and self._finding_end:
            self._finding_end = False
        else:
            raise Exception('cannot call `cut` more than twice!')
        return self

    def end(self) -> 'SemanticSlicer':
        self._current_index = self._alt_index
        return self

    def find(self, substring: str) -> 'SemanticSlicer':
        self._current_index += self.text[self._start_index :].index(substring)
        self._alt_index = self._current_index + len(substring)
        return self

    def inplace(self, substring: str) -> 'SemanticSlicer':
        if self._end_index == self._start_index and self._finding_end:
            self.text = self.text[: self._start_index] + substring
        else:
            self.text = (
                self.text[: self._start_index]
                + substring
                + self.text[self._end_index :]
            )
        self._reset_indexes()
        return self

    def move(self, offset: int) -> 'SemanticSlicer':
        self._current_index += offset
        assert self._current_index >= 0
        return self

    def rfind(self, substring: str) -> 'SemanticSlicer':
        self._current_index = self._start_index + self.text[
            self._start_index :
        ].rindex(substring)
        self._alt_index = self._current_index + len(substring)
        return self

    def slice(self) -> str:
        if self._end_index == self._start_index and self._finding_end:
            return self.text[self._start_index :]
        return self.text[self._start_index : self._end_index]

    out = str = slice  # alias


def slice(text: str) -> SemanticSlicer:
    return SemanticSlicer(text)

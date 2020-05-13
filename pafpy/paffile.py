"""TODO"""
import os
from pathlib import Path
from typing import Optional, TextIO, Union

from pafpy.pafrecord import PafRecord

PathLike = Union[Path, str, os.PathLike]


class PafFile:
    """TODO"""

    def __init__(self, path: PathLike):
        self.path = Path(path)
        """The path to the PAF file."""
        self._stream: Optional[TextIO] = None

    def __del__(self):
        self.close()

    def __enter__(self) -> "PafFile":
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        return self

    def __next__(self) -> PafRecord:
        if self.closed:
            raise IOError("PAF file is closed - cannot get next element.")
        return PafRecord.from_str(next(self._stream))

    def open(self) -> "PafFile":
        """Opens the PAF file to allow iterating over the records. Returns a `PafFile`
        object.

        Where possible, try and use the `with` contenxt manager instead of explicitly
        calling `open` and `close`.

        ## Example
        ```py
        from pafpy import PafFile

        path = __file__
        paf = PafFile(path)
        assert paf.closed
        paf.open()
        assert not paf.closed
        paf.close()
        assert paf.closed
        ```

        ## Errors
        - If the file is already open, an `IOError` exception is raised.
        - If `path` does not exist, an `OSError` exception is raised.
        """
        if not self.closed:
            raise IOError("PafFile is already open.")
        self._stream = self.path.open()
        return self

    @property
    def closed(self) -> bool:
        """Is the PAF file closed?"""
        return self._stream is None or self._stream.closed

    def close(self):
        """Close the `PafFile`."""
        if not self.closed:
            self._stream.close()
            self._stream = None

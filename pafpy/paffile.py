"""This module contains objects for working with PAF files.

The main class of interest here is `pafpy.paffile.PafFile`. It provides an interface to open/close
a PAF file and to iterate over the alignment records within the file.

To use `PafFile` within your code, import it like so

```py
from pafpy import PafFile
```
"""
import gzip
import io
import os
import sys
from pathlib import Path
from typing import IO, Optional, TextIO, Union

from pafpy.pafrecord import PafRecord
from pafpy.utils import is_compressed

PathLike = Union[Path, str, os.PathLike]


class PafFile:
    """Stream access to a PAF file.

    `fileobj` is an object to read the PAF file from. Can be a `str`, `pathlib.Path`,
    or an opened file ([file object](https://docs.python.org/3/glossary.html#term-file-object)).

    > *Note: to use stdin, pass `fileobj="-"`*. See the usage docs for more details.

    The file is *not* automatically opened - unless already open. After construction,
    it can be opened in one of two ways:

    1. Manually, with `PafFile.open`. Remember to close the file when finished.
    2. Via a context manager (`with`) block.

    If an already-open `fileobj` is given, the `PafFile` can be iterated without the
    need to open it.

    ## Example
    ```py
    from pafpy import PafFile, PafRecord
    from pathlib import Path
    import tempfile

    # create a dummy PAF file
    with tempfile.TemporaryDirectory() as tmpdirname:
        # make two unmapped records
        record1 = PafRecord(qname="record1")
        record2 = PafRecord(qname="record2")
        # write records to temporary file
        path = Path(f"{tmpdirname}/test.paf")
        with path.open("w") as stream:
            print(str(record1), file=stream)
            print(str(record2), file=stream)

        # open the PAF file with the context manager
        with PafFile(path) as paf:
            actual_records = [record for record in paf]

    assert paf.closed

    expected_records = [record1, record2]
    assert actual_records == expected_records
    ```

    The records returned when iterating over the open `PafFile` are
    `pafpy.pafrecord.PafRecord` objects.
    """

    def __init__(self, fileobj: Union[PathLike, IO]):
        if isinstance(fileobj, io.IOBase):
            self._stream = fileobj
            self.path = None
            self._is_stdin = False
        else:
            self._stream: Optional[TextIO] = None
            self.path = Path(fileobj) if not str(fileobj) == "-" else None
            self._is_stdin = self.path is None
            """Path to the PAF file. If `fileobj` is an open file object, then `path` will be `None` ."""

    def __del__(self):
        self.close()

    def __enter__(self) -> "PafFile":
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        return self

    def __next__(self) -> PafRecord:
        if self.closed and self._is_stdin:
            self.open()
        elif self.closed:
            raise IOError("PAF file is closed - cannot get next element.")
        line = next(self._stream)
        if isinstance(line, bytes):
            line = line.decode()
        return PafRecord.from_str(line)

    def _open(self) -> IO:
        if self.path is not None:
            with open(self.path, mode="rb") as fileobj:
                file_is_compressed = is_compressed(fileobj)

            if file_is_compressed:
                return gzip.open(self.path)
            else:
                return open(self.path)
        elif self._is_stdin:
            return (
                sys.stdin.buffer
                if not is_compressed(sys.stdin.buffer)
                else gzip.open(sys.stdin.buffer)
            )
        else:
            return self._stream

    def open(self) -> "PafFile":
        """Opens the PAF file to allow iterating over the records. Returns a `PafFile`
        object.

        Where possible, try and use the `with` context manager instead of explicitly
        calling `PafFile.open` and `PafFile.close`.

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

        > *Note: If the file is already open, the file position will be reset to the
        beginning.*

        ## Errors
        - If `path` does not exist, an `OSError` exception is raised.
        """
        if not self.closed:
            self._stream.seek(0)
        else:
            self._stream = self._open()
        return self

    @property
    def closed(self) -> bool:
        """Is the PAF file closed?"""
        return self._stream is None

    def close(self):
        """Close the `PafFile`."""
        if not self.closed:
            try:
                self._stream.close()
            except AttributeError:  # happens if stream is stdin
                pass
            finally:
                self._stream = None

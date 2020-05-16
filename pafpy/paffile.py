"""This module contains objects for working with PAF files.

The main class of interest here is `pafpy.paffile.PafFile`. It provides an interface to open/close
a PAF file and to iterate over the alignment records within the file.

To use `PafFile` within your code, import it like so

```py
from pafpy import PafFile
```
"""
import os
from pathlib import Path
from typing import Optional, TextIO, Union

from pafpy.pafrecord import PafRecord

PathLike = Union[Path, str, os.PathLike]


class PafFile:
    """Stream access to a PAF file.

    The file is *not* automatically opened. After construction, it can be opened in
    one of two ways:

    1. Manually, with `PafFile.open`. Remember to close the file when finished.
    2. Via a context manager (`with`) block.

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

    def __init__(self, path: PathLike):
        self.path = Path(path)
        """Path to the PAF file. Can be a `str` or a `pathlib.Path` object."""
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

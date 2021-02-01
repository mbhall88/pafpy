"""This module contains utility functions unlikely to be of use to anyone else.

```py
from pafpy.utils import first_n_bytes, is_compressed
```
"""
from typing import IO

GZIP_MAGIC = b"\x1f\x8b"


def first_n_bytes(fileobj: IO, n: int = 2) -> bytes:
    """Reads the first *n* bytes of an open file.

    ## Example
    ```py
    from tempfile import TemporaryFile
    from pafpy.utils import first_n_bytes
    contents = b"12345"
    n = 2

    with TemporaryFile() as fileobj:
        fileobj.write(contents)
        fileobj.seek(0)
        actual = first_n_bytes(fileobj, n=n)
    expected = contents[:n]

    assert actual == expected
    ```
    """
    n_bytes = fileobj.read(n)
    fileobj.seek(0)
    return n_bytes if isinstance(n_bytes, bytes) else n_bytes.encode()


def is_compressed(fileobj: IO) -> bool:
    """Reads the first two bytes of an open file to check for the `gzip` magic number.

    ```py
    from tempfile import TemporaryFile
    from pafpy.utils import is_compressed, GZIP_MAGIC

    contents = GZIP_MAGIC + b" is compressed"
    with TemporaryFile() as fileobj:
        fileobj.write(contents)
        fileobj.seek(0)
        assert is_compressed(fileobj)
    ```
    """
    n_bytes = first_n_bytes(fileobj, n=2)
    return n_bytes == GZIP_MAGIC

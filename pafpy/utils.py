from typing import IO

GZIP_MAGIC = b"\x1f\x8b"


def first_n_bytes(fileobj: IO, n: int = 2) -> bytes:
    n_bytes = fileobj.read(n)
    fileobj.seek(0)
    return n_bytes if isinstance(n_bytes, bytes) else n_bytes.encode()


def is_compressed(fileobj: IO) -> bool:
    n_bytes = first_n_bytes(fileobj)
    return n_bytes == GZIP_MAGIC

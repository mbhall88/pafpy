from tempfile import TemporaryFile

import pytest

from pafpy.utils import GZIP_MAGIC, first_n_bytes, is_compressed


class TestFirstNBytes:
    def test_empty_file_returns_empty(self):
        contents = b""
        with TemporaryFile() as fileobj:
            fileobj.write(contents)
            fileobj.seek(0)
            actual = first_n_bytes(fileobj)
        expected = contents

        assert actual == expected

    def test_one_byte_returns_one_byte(self):
        contents = b"1"
        n = 2
        with TemporaryFile() as fileobj:
            fileobj.write(contents)
            fileobj.seek(0)
            actual = first_n_bytes(fileobj, n=n)
        expected = contents

        assert actual == expected

    def test_two_bytes_returns_two_bytes(self):
        contents = b"12"
        n = 2

        with TemporaryFile() as fileobj:
            fileobj.write(contents)
            fileobj.seek(0)
            actual = first_n_bytes(fileobj, n=n)
        expected = contents

        assert actual == expected

    def test_more_bytes_returns_two_bytes(self):
        contents = b"12345"
        n = 2

        with TemporaryFile() as fileobj:
            fileobj.write(contents)
            fileobj.seek(0)
            actual = first_n_bytes(fileobj, n=n)
        expected = contents[:n]

        assert actual == expected

    def test_text_stream_returns_bytes(self):
        contents = "12345"
        n = 3

        with TemporaryFile("w+") as fileobj:
            fileobj.write(contents)
            fileobj.seek(0)
            actual = first_n_bytes(fileobj, n=n)
        expected = contents[:n].encode()

        assert actual == expected

    def test_nonreadable_object_raises_error(self):
        fileobj = b"12345"
        n = 3

        with pytest.raises(AttributeError) as err:
            first_n_bytes(fileobj, n=n)
            assert err.match("has no attribute 'read'")


class TestIsCompressed:
    def test_empty_file(self):
        contents = b""
        with TemporaryFile() as fileobj:
            fileobj.write(contents)
            fileobj.seek(0)
            assert not is_compressed(fileobj)

    def test_non_compressed(self):
        contents = b"not compressed"
        with TemporaryFile() as fileobj:
            fileobj.write(contents)
            fileobj.seek(0)
            assert not is_compressed(fileobj)

    def test_compressed(self):
        contents = GZIP_MAGIC + b" is compressed"
        with TemporaryFile() as fileobj:
            fileobj.write(contents)
            fileobj.seek(0)
            assert is_compressed(fileobj)

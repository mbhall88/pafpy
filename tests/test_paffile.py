import io
import tempfile
from pathlib import Path

import pytest

from pafpy.paffile import PafFile
from pafpy.pafrecord import PafRecord

TEST_DIR = Path(__file__).parent


class TestConstructor:
    def test_fileobj_is_dash_uses_stdin(self):
        fileobj = "-"
        paf = PafFile(fileobj)

        assert paf._stream is None
        assert paf.path is None
        assert paf._is_stdin

    def test_fileobj_is_path(self):
        fileobj = "path/to/file"
        paf = PafFile(fileobj)

        assert paf.path == Path(fileobj)
        assert paf.closed

    def test_file_object_given(self):
        with tempfile.TemporaryFile() as fileobj:
            paf = PafFile(fileobj)

            assert paf.path is None
            assert not paf.closed


class TestClosed:
    def test_file_is_closed_returns_true(self):
        path = __file__
        paf = PafFile(path)

        assert paf.closed

    def test_file_is_not_closed_returns_false(self):
        path = __file__
        paf = PafFile(path).open()

        assert not paf.closed

    def test_file_is_closed_after_opened_returns_true(self):
        path = __file__
        paf = PafFile(path).open()

        paf.close()

        assert paf.closed


class TestOpen:
    def test_file_does_not_exist_raises_error(self):
        path = "foo.bar"
        paf = PafFile(path)

        with pytest.raises(OSError):
            paf.open()

    def test_file_object_already_open_returns_itself(self):
        fileobj = open(__file__, mode="rb")
        paf = PafFile(fileobj)
        assert paf.open()._stream == paf._stream


class TestContextManager:
    def test_file_already_open_resets_position(self):
        path = __file__
        paf = PafFile(path).open()

        with paf:
            assert paf._stream.tell() == 0

    def test_file_not_open_opens_file_in_context_and_closes_afterwards(self):
        path = __file__

        with PafFile(path) as paf:
            assert not paf.closed

        assert paf.closed


class TestIterateFile:
    def test_next_returns_pafrecord(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            record = PafRecord()
            path = Path(f"{tmpdirname}/test.paf")
            path.write_text(str(record))
            with PafFile(path) as paf:
                actual = next(paf)

            expected = record

            assert actual == expected

    def test_next_after_end_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            record = PafRecord()
            path = Path(f"{tmpdirname}/test.paf")
            path.write_text(str(record))
            with PafFile(path) as paf:
                next(paf)
                with pytest.raises(StopIteration):
                    next(paf)

    def test_for_loop_returns_pafrecords(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            record1 = PafRecord()
            record2 = PafRecord(qname="record2")
            path = Path(f"{tmpdirname}/test.paf")
            path.write_text(f"{str(record1)}\n{str(record2)}")
            with PafFile(path) as paf:
                actual = [record for record in paf]

            expected = [record1, record2]

            assert actual == expected

    def test_call_next_on_closed_file_raises_error(self):
        paf = PafFile(fileobj="foo")
        with pytest.raises(IOError):
            next(paf)


class TestIO:
    def test_read_gzip_compressed(self):
        path = TEST_DIR / "demo.paf.gz"
        with PafFile(path) as paf:
            record = next(paf)

        assert record.qname == "11737-1"

    def test_read_normal_file(self):
        path = TEST_DIR / "demo.paf"
        with PafFile(path) as paf:
            record = next(paf)

        assert record.qname == "11737-1"

    def test_read_from_fileobj(self):
        path = TEST_DIR / "demo.paf"
        with open(path) as fileobj:
            paf = PafFile(fileobj)
            record = next(paf)

        assert record.qname == "11737-1"

    def test_read_from_stdin(self, monkeypatch):
        fields = [
            "query_name",
            "1239",
            "65",
            "1239",
            "+",
            "target_name",
            "4378340",
            "2555250",
            "2556472",
            "1139",
            "1228",
            "60",
        ]
        line = "\t".join(fields).encode()
        fileobj = io.TextIOWrapper(io.BytesIO(line))
        monkeypatch.setattr("sys.stdin", fileobj)
        path = "-"
        paf = PafFile(path)
        record = next(paf)

        assert record.qname == fields[0]

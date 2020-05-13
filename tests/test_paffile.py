import tempfile
from pathlib import Path

import pytest

from pafpy.paffile import PafFile
from pafpy.pafrecord import PafRecord


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


class TestContextManager:
    def test_file_already_open_raises_error(self):
        path = __file__
        paf = PafFile(path).open()

        with pytest.raises(IOError):
            with paf:
                pass

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

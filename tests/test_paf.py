import pytest
from pafpy.paf import PafRecord, Strand, MalformattedRecord


class TestFromStr:
    def test_empty_str_raises_error(self):
        line = ""

        with pytest.raises(MalformattedRecord):
            PafRecord.from_str(line)

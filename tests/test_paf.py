from pafpy.paf import PafRecord, Strand


class TestFromStr:
    def test_empty_str_returns_empty_record(self):
        row = ""

        actual = PafRecord.from_str(row)
        expected = PafRecord()

        assert actual == expected

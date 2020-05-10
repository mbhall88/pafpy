import pytest
from pafpy.paf import PafRecord, Strand, MalformattedRecord


class TestFromStr:
    def test_empty_str_raises_error(self):
        line = ""

        with pytest.raises(MalformattedRecord):
            PafRecord.from_str(line)

    def test_line_has_too_few_fields_raises_error(self):
        line = "qname\t1\t3"

        with pytest.raises(MalformattedRecord):
            PafRecord.from_str(line)

    def test_line_with_no_tags(self):
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
        line = "\t".join(fields)

        actual = PafRecord.from_str(line)
        expected = PafRecord(
            "query_name",
            1239,
            65,
            1239,
            Strand.Forward,
            "target_name",
            4378340,
            2555250,
            2556472,
            1139,
            1228,
            60,
            [],
        )

        assert actual == expected

    def test_line_with_tags(self):
        fields = [
            "query_name",
            "1239",
            "65",
            "1239",
            "-",
            "target_name",
            "4378340",
            "2555250",
            "2556472",
            "1139",
            "1228",
            "60",
            "NM:i:89",
            "ms:i:1906",
        ]
        line = "\t".join(fields)

        actual = PafRecord.from_str(line)
        expected = PafRecord(
            "query_name",
            1239,
            65,
            1239,
            Strand.Reverse,
            "target_name",
            4378340,
            2555250,
            2556472,
            1139,
            1228,
            60,
            ["NM:i:89", "ms:i:1906"],
        )

        assert actual == expected

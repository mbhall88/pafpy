from unittest.mock import patch, PropertyMock

import pytest

from pafpy.pafrecord import PafRecord, MalformattedRecord, DELIM
from pafpy.strand import Strand


class TestStr:
    def test_no_tags(self):
        record = PafRecord()

        actual = str(record)
        expected = DELIM.join(
            str(x) for x in PafRecord._field_defaults.values() if x is not None
        )

        assert actual == expected

    def test_with_tags(self):
        tags = ["NM:i:1", "ms:i:1906"]
        record = PafRecord(tags=tags)

        actual = str(record)
        expected = (
            DELIM.join(
                str(x) for x in PafRecord._field_defaults.values() if x is not None
            )
            + DELIM
            + DELIM.join(tags)
        )

        assert actual == expected


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


class TestQueryAlignedLength:
    def test_unmapped_record_returns_zero(self):
        record = PafRecord()

        actual = record.query_aligned_length
        expected = 0

        assert actual == expected

    def test_qend_greater_than_qstart(self):
        record = PafRecord(qstart=2, qend=5)

        actual = record.query_aligned_length
        expected = 3

        assert actual == expected

    def test_qend_less_than_qstart(self):
        record = PafRecord(qstart=5, qend=2)

        actual = record.query_aligned_length
        expected = 3

        assert actual == expected


class TestTargetAlignedLength:
    def test_unmapped_record_returns_zero(self):
        record = PafRecord()

        actual = record.target_aligned_length
        expected = 0

        assert actual == expected

    def test_tend_greater_than_tstart(self):
        record = PafRecord(tstart=2, tend=5)

        actual = record.target_aligned_length
        expected = 3

        assert actual == expected

    def test_tend_less_than_tstart(self):
        record = PafRecord(tstart=5, tend=2)

        actual = record.target_aligned_length
        expected = 3

        assert actual == expected


class TestQueryCoverage:
    def test_unmapped_record_returns_zero(self):
        record = PafRecord(qlen=0)

        actual = record.query_coverage
        expected = 0.0

        assert actual == expected

    def test_part_of_query_aligned(self):
        qlen = 10
        qalen = 4
        patch_target = "pafpy.pafrecord.PafRecord.query_aligned_length"
        with patch(patch_target, new_callable=PropertyMock) as mocked_qalen:
            mocked_qalen.return_value = qalen
            record = PafRecord(qlen=qlen)
            actual = record.query_coverage
            mocked_qalen.assert_called_once()

        expected = 0.4

        assert actual == expected

    def test_all_of_query_aligned(self):
        qlen = 10
        qalen = 10
        patch_target = "pafpy.pafrecord.PafRecord.query_aligned_length"
        with patch(patch_target, new_callable=PropertyMock) as mocked_qalen:
            mocked_qalen.return_value = qalen
            record = PafRecord(qlen=qlen)
            actual = record.query_coverage
            mocked_qalen.assert_called_once()

        expected = 1.0

        assert actual == expected


class TestTargetCoverage:
    def test_unmapped_record_returns_zero(self):
        record = PafRecord(tlen=0)

        actual = record.target_coverage
        expected = 0.0

        assert actual == expected

    def test_part_of_target_aligned(self):
        tlen = 10
        talen = 4
        patch_target = "pafpy.pafrecord.PafRecord.target_aligned_length"
        with patch(patch_target, new_callable=PropertyMock) as mocked_talen:
            mocked_talen.return_value = talen
            record = PafRecord(tlen=tlen)
            actual = record.target_coverage
            mocked_talen.assert_called_once()

        expected = 0.4

        assert actual == expected

    def test_all_of_target_aligned(self):
        tlen = 10
        talen = 10
        patch_target = "pafpy.pafrecord.PafRecord.target_aligned_length"
        with patch(patch_target, new_callable=PropertyMock) as mocked_talen:
            mocked_talen.return_value = talen
            record = PafRecord(tlen=tlen)
            actual = record.target_coverage
            mocked_talen.assert_called_once()

        expected = 1.0

        assert actual == expected

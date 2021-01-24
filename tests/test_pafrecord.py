from contextlib import ExitStack
from unittest.mock import PropertyMock, patch

import pytest

from pafpy.pafrecord import DELIM, MalformattedRecord, PafRecord
from pafpy.strand import Strand
from pafpy.tag import InvalidTagFormat, Tag


class TestStr:
    def test_no_tags(self):
        record = PafRecord()

        actual = str(record)
        expected = DELIM.join(
            str(x) for x in PafRecord._field_defaults.values() if x is not None
        )

        assert actual == expected

    def test_with_tags(self):
        tags = {"NM": Tag.from_str("NM:i:1"), "ms": Tag.from_str("ms:i:1906")}
        record = PafRecord(tags=tags)

        actual = str(record)
        expected = (
            DELIM.join(
                str(x) for x in PafRecord._field_defaults.values() if x is not None
            )
            + DELIM
            + DELIM.join(map(str, tags.values()))
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
        )

        assert actual == expected

    def test_line_with_invalid_tag_raises_error(self):
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
            "NMX:i:89",
        ]
        line = "\t".join(fields)

        with pytest.raises(InvalidTagFormat):
            PafRecord.from_str(line)

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
        tags = {"NM": Tag.from_str("NM:i:89"), "ms": Tag.from_str("ms:i:1906")}
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
            tags,
        )

        assert actual == expected

    def test_line_with_dupliacte_tag_returns_last_one(self):
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
            "NM:i:2",
        ]
        line = "\t".join(fields)

        actual = PafRecord.from_str(line)
        expected_tags = {"NM": Tag.from_str("NM:i:2")}
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
            expected_tags,
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


class TestRelativeLength:
    def test_unmapped_record_returns_zero(self):
        record = PafRecord()

        actual = record.relative_length
        expected = 0.0

        assert actual == expected

    def test_query_shorter_than_target(self):
        talen = 10
        qalen = 9
        patch_talen = "pafpy.pafrecord.PafRecord.target_aligned_length"
        patch_qalen = "pafpy.pafrecord.PafRecord.query_aligned_length"
        with ExitStack() as stack:
            mocked_talen = stack.enter_context(
                patch(patch_talen, new_callable=PropertyMock)
            )
            mocked_qalen = stack.enter_context(
                patch(patch_qalen, new_callable=PropertyMock)
            )
            mocked_talen.return_value = talen
            mocked_qalen.return_value = qalen
            record = PafRecord()
            actual = record.relative_length

            mocked_talen.assert_called_once()
            mocked_qalen.assert_called_once()

        expected = 0.9

        assert actual == expected

    def test_query_longer_than_target(self):
        talen = 10
        qalen = 11
        patch_talen = "pafpy.pafrecord.PafRecord.target_aligned_length"
        patch_qalen = "pafpy.pafrecord.PafRecord.query_aligned_length"
        with ExitStack() as stack:
            mocked_talen = stack.enter_context(
                patch(patch_talen, new_callable=PropertyMock)
            )
            mocked_qalen = stack.enter_context(
                patch(patch_qalen, new_callable=PropertyMock)
            )
            mocked_talen.return_value = talen
            mocked_qalen.return_value = qalen
            record = PafRecord()
            actual = record.relative_length

            mocked_talen.assert_called_once()
            mocked_qalen.assert_called_once()

        expected = 1.1

        assert actual == expected

    def test_query_and_target_same_length(self):
        talen = 10
        qalen = 10
        patch_talen = "pafpy.pafrecord.PafRecord.target_aligned_length"
        patch_qalen = "pafpy.pafrecord.PafRecord.query_aligned_length"
        with ExitStack() as stack:
            mocked_talen = stack.enter_context(
                patch(patch_talen, new_callable=PropertyMock)
            )
            mocked_qalen = stack.enter_context(
                patch(patch_qalen, new_callable=PropertyMock)
            )
            mocked_talen.return_value = talen
            mocked_qalen.return_value = qalen
            record = PafRecord()
            actual = record.relative_length

            mocked_talen.assert_called_once()
            mocked_qalen.assert_called_once()

        expected = 1.0

        assert actual == expected


class TestBlastIdentity:
    def test_unmapped_record_returns_zero(self):
        record = PafRecord()

        actual = record.blast_identity()
        expected = 0.0

        assert actual == expected

    def test_no_matches_returns_zero(self):
        record = PafRecord(mlen=0, blen=5)

        actual = record.blast_identity()
        expected = 0.0

        assert actual == expected

    def test_alignment_block_longer_than_matches(self):
        record = PafRecord(mlen=4, blen=5)

        actual = record.blast_identity()
        expected = 0.8

        assert actual == expected

    def test_alignment_block_same_length_as_matches(self):
        record = PafRecord(mlen=5, blen=5)

        actual = record.blast_identity()
        expected = 1.0

        assert actual == expected


class TestIsUnmapped:
    def test_unmapped_record(self):
        record = PafRecord()

        assert record.is_unmapped()

    def test_mapped_record(self):
        record = PafRecord(
            qname="05f868dc-6760-47ec-b7e7-ab4054b0e4fe",
            qlen=4641,
            qstart=5,
            qend=4640,
            strand=Strand.Reverse,
            tname="NODE_1_length_4378477_cov_60.093643",
            tlen=4378340,
            tstart=1069649,
            tend=1074329,
            mlen=4499,
            blen=4740,
            mapq=60,
            tags={"tp": Tag.from_str("tp:A:P")},
        )

        assert not record.is_unmapped()


class TestGetTag:
    def test_no_tags_returns_default(self):
        record = PafRecord()
        tag = "NM"

        actual = record.get_tag(tag)

        assert actual is None

    def test_tag_not_present_returns_default(self):
        tags = {"de": Tag.from_str("de:f:0.1")}
        record = PafRecord(tags=tags)
        tag = "NM"
        default = Tag.from_str("NM:i:0")

        actual = record.get_tag(tag, default=default)
        expected = default

        assert actual == expected

    def test_tag_present(self):
        expected = Tag.from_str("de:f:0.1")
        tags = {"de": expected}
        record = PafRecord(tags=tags)
        tag = "de"

        actual = record.get_tag(tag)

        assert actual == expected


class TestIsPrimary:
    def test_unmapped_record(self):
        record = PafRecord()

        assert not record.is_primary()

    def test_primary_record_returns_true(self):
        tag = Tag.from_str("tp:A:P")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})

        assert record.is_primary()

    def test_lower_case_primary_returns_true(self):
        tag = Tag.from_str("tp:A:p")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})

        assert record.is_primary()

    def test_unknown_char_raises_error(self):
        tag = Tag.from_str("tp:A:?")
        with pytest.raises(ValueError):
            PafRecord(strand=Strand.Forward, tags={tag.tag: tag}).is_primary()

    def test_tp_tag_not_present_in_mapped_record_raises_error(self):
        with pytest.raises(ValueError):
            PafRecord(strand=Strand.Reverse).is_primary()


class TestIsSecondary:
    def test_unmapped_record(self):
        record = PafRecord()

        assert not record.is_secondary()

    def test_primary_record_returns_false(self):
        tag = Tag.from_str("tp:A:P")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})

        assert not record.is_secondary()

    def test_secondary_returns_true(self):
        tag = Tag.from_str("tp:A:S")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})

        assert record.is_secondary()

    def test_lower_case_secondary_returns_true(self):
        tag = Tag.from_str("tp:A:s")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})

        assert record.is_secondary()

    def test_unknown_char_raises_error(self):
        tag = Tag.from_str("tp:A:?")
        with pytest.raises(ValueError):
            PafRecord(strand=Strand.Forward, tags={tag.tag: tag}).is_secondary()

    def test_tp_tag_not_present_in_mapped_record_raises_error(self):
        with pytest.raises(ValueError):
            PafRecord(strand=Strand.Reverse).is_secondary()


class TestIsInversion:
    def test_unmapped_record(self):
        record = PafRecord()

        assert not record.is_inversion()

    def test_primary_record_returns_false(self):
        tag = Tag.from_str("tp:A:P")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})

        assert not record.is_inversion()

    def test_inversion_returns_true(self):
        tag = Tag.from_str("tp:A:I")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})

        assert record.is_inversion()

    def test_lower_case_inversion_returns_true(self):
        tag = Tag.from_str("tp:A:i")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})

        assert record.is_inversion()

    def test_unknown_char_raises_error(self):
        tag = Tag.from_str("tp:A:?")
        with pytest.raises(ValueError):
            PafRecord(strand=Strand.Forward, tags={tag.tag: tag}).is_inversion()

    def test_tp_tag_not_present_in_mapped_record_raises_error(self):
        with pytest.raises(ValueError):
            PafRecord(strand=Strand.Reverse).is_inversion()

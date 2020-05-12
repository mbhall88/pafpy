from enum import Enum
from typing import NamedTuple, Optional, Dict

from pafpy.strand import Strand
from pafpy.tag import Tag

Tags = Dict[str, Tag]

DELIM = "\t"
MIN_FIELDS = 12


class MalformattedRecord(Exception):
    """An exception indicating that a `PafRecord` is not in the expected format."""

    pass


class AlignmentType(Enum):
    """An enum for storing mappings between the value in the tp tag and the type of
    alignment this value indicates.
    """

    Primary = "P"
    Secondary = "S"
    Inversion = "I"
    Unknown = "*"


class PafRecord(NamedTuple):
    """A single entry (row) in a [PAF][paf] file.

    TODO add examples

    [paf]: https://github.com/lh3/miniasm/blob/master/PAF.md
    """

    qname: str = "*"
    """Query sequence name."""
    qlen: int = 0
    """Query sequence length."""
    qstart: int = 0
    """Query start (0-based; BED-like; closed)."""
    qend: int = 0
    """Query end (0-based; BED-like; open)."""
    strand: Strand = Strand.Unmapped
    """‘+’ if query/target on the same strand; ‘-’ if opposite; '*' if unmapped."""
    tname: str = "*"
    """Target sequence name."""
    tlen: int = 0
    """Target sequence length."""
    tstart: int = 0
    """Target start on original strand (0-based)."""
    tend: int = 0
    """Target end on original strand (0-based)."""
    mlen: int = 0
    """Number of matching bases in the mapping."""
    blen: int = 0
    """Alignment block length. Number of bases, including gaps, in the mapping."""
    mapq: int = 0
    """Mapping quality (0-255; 255 for missing)."""
    tags: Optional[Tags] = None
    """[SAM-like optional fields (tags)](https://samtools.github.io/hts-specs/SAMtags.pdf)."""

    def __str__(self) -> str:
        tag_str = "" if self.tags is None else DELIM.join(self.tags)
        fields = [
            self.qname,
            self.qlen,
            self.qstart,
            self.qend,
            self.strand,
            self.tname,
            self.tlen,
            self.tstart,
            self.tend,
            self.mlen,
            self.blen,
            self.mapq,
            tag_str,
        ]
        return DELIM.join(map(str, fields)).rstrip()

    @staticmethod
    def from_str(line: str) -> "PafRecord":
        """Construct a `PafRecord` from a string.

        Note: If there are duplicate SAM-like tags, only the last one will be retained.

        ## Example
        ```py
        from pafpy.pafrecord import PafRecord

        line = "query_name\t1239\t65\t1239\t+\ttarget_name\t4378340\t2555250\t2556472\t1139\t1228\t60"
        record = PafRecord.from_str(line)

        assert record.qname == "query_name"
        assert record.mapq == 60
        ```

        ## Errors
        - If there are less than the expected number of fields (12), this function will
        raise a `MalformattedRecord` exception.
        - If there is an invalid tag, an `InvalidTagFormat` exception will be raised.
        """
        fields = line.rstrip().split(DELIM)
        if len(fields) < MIN_FIELDS:
            raise MalformattedRecord(
                f"Expected {MIN_FIELDS} fields, but got {len(fields)}\n{line}"
            )
        tags: Tags = dict()
        for tag_str in fields[12:]:
            tag = Tag.from_str(tag_str)
            tags[tag.tag] = tag

        return PafRecord(
            qname=fields[0],
            qlen=int(fields[1]),
            qstart=int(fields[2]),
            qend=int(fields[3]),
            strand=Strand(fields[4]),
            tname=fields[5],
            tlen=int(fields[6]),
            tstart=int(fields[7]),
            tend=int(fields[8]),
            mlen=int(fields[9]),
            blen=int(fields[10]),
            mapq=int(fields[11]),
            tags=tags,
        )

    @property
    def query_aligned_length(self) -> int:
        """Length of the aligned query sequence.

        This is equal to the absolute value of `qend` - `qstart`.
        """
        return abs(self.qend - self.qstart)

    @property
    def query_coverage(self) -> float:
        """Proportion of the query sequence involved in the alignment.

        This is equal to `query_aligned_length` - `qlen`

        ## Example
        ```py
        from pafpy.pafrecord import PafRecord

        record = PafRecord(qlen=10, qstart=5, qend=9)
        assert record.query_coverage == 0.4
        ```
        """
        try:
            return self.query_aligned_length / self.qlen
        except ZeroDivisionError:
            return 0.0

    @property
    def target_coverage(self) -> float:
        """Proportion of the target sequence involved in the alignment.

        This is equal to `target_aligned_length` - `tlen`

        ## Example
        ```py
        from pafpy.pafrecord import PafRecord

        record = PafRecord(tlen=10, tstart=5, tend=9)
        assert record.target_coverage == 0.4
        ```
        """
        try:
            return self.target_aligned_length / self.tlen
        except ZeroDivisionError:
            return 0.0

    @property
    def target_aligned_length(self) -> int:
        """Length of the aligned target sequence.

        This is equal to the absolute value of `tend` - `tstart`.
        """
        return abs(self.tend - self.tstart)

    @property
    def relative_length(self) -> float:
        """Relative (aligned) length of the query sequence to the target.

        This is equal to `query_aligned_length` - `target_aligned_length`.

        ## Example
        ```py
        from pafpy.pafrecord import PafRecord

        record = PafRecord(qlen=50, qstart=10, qend=20, tlen=100, tstart=50, tend=90)
        assert record.relative_length == 0.25
        ```
        """
        try:
            return self.query_aligned_length / self.target_aligned_length
        except ZeroDivisionError:
            return 0.0

    def blast_identity(self) -> float:
        """Calculates the [BLAST identity][blast] for the record.

        BLAST identity is defined as the number of matching bases over the number of
        alignment columns.

        ## Example
        ```py
        from pafpy.pafrecord import PafRecord

        record = PafRecord(
            mlen=43,  # number of matches
            blen=50,  # number of alignment columns
        )
        assert record.blast_identity() == 0.86
        ```
        [blast]: https://lh3.github.io/2018/11/25/on-the-definition-of-sequence-identity#blast-identity
        """
        try:
            return self.mlen / self.blen
        except ZeroDivisionError:
            return 0.0

    def is_unmapped(self) -> bool:
        """Is the record unmapped?

        A record is considered unmapped if the strand is '*' - as per the minimap2
        [`--paf-no-hit`][io-opts] parameter behaviour.

        ## Example
        ```py
        from pafpy.strand import Strand
        from pafpy.pafrecord import PafRecord

        record = PafRecord(strand=Strand("*"))
        assert record.is_unmapped()
        ```

        [io-opts]: https://lh3.github.io/minimap2/minimap2.html#7
        """
        return self.strand is Strand.Unmapped

    def is_primary(self) -> bool:
        """Is the record a primary alignment?

        This is determined from the ['tp' tag][mm2-tags].

        *Note: Supplementary alignments will also return `True`.*

        ## Example
        ```py
        from pafpy.pafrecord import PafRecord
        from pafpy.tag import Tag
        from pafpy.strand import Strand

        tag = Tag.from_str("tp:A:P")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})
        assert record.is_primary()
        ```

        ## Errors
        If the value in the 'tp' tag is unknown, a `ValueError` exception will be
        raised.

        [mm2-tags]: https://lh3.github.io/minimap2/minimap2.html#10
        """
        if self.is_unmapped():
            return False

        aln_tag = self.get_tag("tp", default=Tag.from_str("tp:A:*"))
        aln_type = AlignmentType(aln_tag.value[0].upper())

        return aln_type is AlignmentType.Primary

    def is_secondary(self) -> bool:
        """Is the record a secondary alignment?

        This is determined from the ['tp' tag][mm2-tags].

        *Note: Supplementary alignments will return `False` as they are considered
        primary.*

        ## Example
        ```py
        from pafpy.pafrecord import PafRecord
        from pafpy.tag import Tag
        from pafpy.strand import Strand

        tag = Tag.from_str("tp:A:S")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})
        assert record.is_secondary()
        ```

        ## Errors
        If the value in the 'tp' tag is unknown, a `ValueError` exception will be
        raised.

        [mm2-tags]: https://lh3.github.io/minimap2/minimap2.html#10
        """
        if self.is_unmapped():
            return False

        aln_tag = self.get_tag("tp", default=Tag.from_str("tp:A:*"))
        aln_type = AlignmentType(aln_tag.value[0].upper())

        return aln_type is AlignmentType.Secondary

    def is_inversion(self) -> bool:
        """Is the alignment an inversion?

        This is determined from the ['tp' tag][mm2-tags]. For more information about
        inversions (from minimap2) refer to the [minimap2 alignment options][aln-opts].

        ## Example
        ```py
        from pafpy.pafrecord import PafRecord
        from pafpy.tag import Tag
        from pafpy.strand import Strand

        tag = Tag.from_str("tp:A:I")
        record = PafRecord(strand=Strand.Forward, tags={tag.tag: tag})
        assert record.is_inversion()
        ```

        ## Errors
        If the value in the 'tp' tag is unknown, a `ValueError` exception will be
        raised.

        [mm2-tags]: https://lh3.github.io/minimap2/minimap2.html#10
        [aln-opts]: https://lh3.github.io/minimap2/minimap2.html#6
        """
        if self.is_unmapped():
            return False

        aln_tag = self.get_tag("tp", default=Tag.from_str("tp:A:*"))
        aln_type = AlignmentType(aln_tag.value[0].upper())

        return aln_type is AlignmentType.Inversion

    def get_tag(self, tag: str, default: Optional[Tag] = None) -> Optional[Tag]:
        """Retreive a tag from the record if it is present. Otherwise, return `default`.

        If `default` is not specified, `None` will be used as the default.

        ## Example
        ```py
        from pafpy.tag import Tag
        from pafpy.pafrecord import PafRecord

        # tag is present
        expected = Tag.from_str("de:f:0.1")
        tags = {"de": expected}
        record = PafRecord(tags=tags)
        tag = "de"

        actual = record.get_tag(tag)

        assert actual == expected

        # tag is not present, returns default
        tag = "NM"
        default = Tag.from_str("NM:i:0")

        actual = record.get_tag(tag, default=default)

        assert actual == default
        ```
        """
        return default if self.tags is None else self.tags.get(tag, default)

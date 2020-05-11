from typing import NamedTuple, List, Optional

from pafpy.strand import Strand

DELIM = "\t"
MIN_FIELDS = 12


class MalformattedRecord(Exception):
    pass


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
    tags: Optional[List[str]] = None
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

        ## Example
        ```py
        from pafpy.pafrecord import PafRecord

        line = "query_name\t1239\t65\t1239\t+\ttarget_name\t4378340\t2555250\t2556472\t1139\t1228\t60"
        record = PafRecord.from_str(line)

        assert record.qname == "query_name"
        assert record.mapq == 60
        ```

        ## Errors
        If there are less than the expected number of fields (12), this function will
        raise a `MalformattedRecord` exception.
        """
        fields = line.rstrip().split(DELIM)
        if len(fields) < MIN_FIELDS:
            raise MalformattedRecord(
                f"Expected {MIN_FIELDS} fields, but got {len(fields)}\n{line}"
            )

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
            tags=fields[12::],
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

    # methods to implement
    # TODO: is_unmapped
    # TODO: is_primary
    # TODO: is_secondary
    # TODO: is_inversion

from enum import Enum
from typing import NamedTuple, List, Optional

DELIM = "\t"
MIN_FIELDS = 12


class MalformattedRecord(Exception):
    pass


class Strand(Enum):
    Forward = "+"
    Reverse = "-"

    def __str__(self) -> str:
        return str(self.value)


class PafRecord(NamedTuple):
    """A single entry (row) in a [PAF][paf] file.

    TODO add examples

    [paf]: https://github.com/lh3/miniasm/blob/master/PAF.md
    """

    qname: str = ""
    """Query sequence name."""
    qlen: int = -1
    """Query sequence length."""
    qstart: int = -1
    """Query start (0-based; BED-like; closed)."""
    qend: int = -1
    """Query end (0-based; BED-like; open)."""
    strand: Strand = Strand.Forward
    """Relative strand: "+" or "-"."""
    tname: str = ""
    """Target sequence name."""
    tlen: int = -1
    """Target sequence length."""
    tstart: int = -1
    """Target start on original strand (0-based)."""
    tend: int = -1
    """Target end on original strand (0-based)."""
    mlen: int = -1
    """Number of residue matches."""
    blen: int = -1
    """Alignment block length, including both alignment matches and gaps but excluding 
    ambiguous bases."""
    mapq: int = -1
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
        from pafpy.paf import PafRecord

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

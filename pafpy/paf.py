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
    """A single entry (row) in a PAF file."""

    qname: str = ""
    """Query sequence name."""
    qlen: int = -1
    qstart: int = -1
    qend: int = -1
    strand: Strand = Strand.Forward
    tname: str = ""
    tlen: int = -1
    tstart: int = -1
    tend: int = -1
    mlen: int = -1
    blen: int = -1
    mapq: int = -1
    tags: Optional[List[str]] = None

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
        line = "qname\t4"
        record = PafRecord.from_str(line)
        ```

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

from enum import Enum
from typing import NamedTuple, List, Optional


class Strand(Enum):
    Forward = "+"
    Reverse = "-"


class PafRecord(NamedTuple):
    qname: str = ""
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

    @staticmethod
    def from_str(row: str) -> "PafRecord":
        if not row:
            return PafRecord()

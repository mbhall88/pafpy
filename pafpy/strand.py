"""A module containing objects relating to the strand field within a PAF file.

The main class of interest here is `pafpy.strand.Strand`. To use it within your code, import it like so

```py
from pafpy import Strand
```
"""
from enum import Enum


class Strand(Enum):
    """An enum listing the possible values in the strand field of a PAF file.

    ## Example
    ```py
    from pafpy import Strand

    strand = Strand("-")
    assert strand == Strand.Reverse
    assert str(strand) == "-"
    ```
    """

    Forward = "+"
    Reverse = "-"
    Unmapped = "*"

    def __str__(self) -> str:
        return str(self.value)

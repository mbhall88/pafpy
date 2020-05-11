from enum import Enum


class Strand(Enum):
    Forward = "+"
    Reverse = "-"
    Unmapped = "*"

    def __str__(self) -> str:
        return str(self.value)

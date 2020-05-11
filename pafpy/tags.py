"""A module for wrapping SAM-like optional fields (tags) generally used in PAF files.

The full specifications can he found [here][specs].

[specs]: https://samtools.github.io/hts-specs/SAMtags.pdf
"""
import re
from typing import NamedTuple, Union

DELIM = ":"
TYPES = {"A": str, "f": float, "i": int, "Z": str}
TAG_REGEX = re.compile(
    (
        rf"\b(?P<tag>\w{{2}}){DELIM}"
        rf"(?P<type>[{''.join(TYPES.keys())}]){DELIM}"
        rf"(?P<value>\S+)\b"
    )
)


class InvalidTagFormat(Exception):
    """An exception used to indicate the format of a tag string is invalid."""

    pass


class Tag(NamedTuple):
    """Class representing a single SAM-like optional field (tag).

    ## Example
    ```py
    from pafpy.tags import Tag

    tag = Tag(tag="NM", type="i", value=50)
    assert str(tag) == "NM:i:50"
    ```
    """

    tag: str
    """The two character key identifying the tag. e.g. "NM" or "cg"."""
    type: str
    """A single character indicating the type of `value`. e.g. "A" or "i"."""
    value: Union[str, float, int]
    """The value of the tag."""

    def __str__(self) -> str:
        return DELIM.join([self.tag, self.type, str(self.value)])

    @staticmethod
    def from_str(string: str) -> "Tag":
        """Construct a `Tag` from a string.

        ## Example
        ```py
        from pafpy.tags import Tag

        string = "NM:i:50"
        tag = Tag.from_str(string)

        assert tag.tag == "NM"
        assert tag.type == "i"
        assert tag.value == 50
        ```

        ## Errors
        If `string` is not formatted according to the [specs][specs], an
        `InvalidTagFormat` exception will be raised.

        [specs]: https://samtools.github.io/hts-specs/SAMtags.pdf
        """
        match = TAG_REGEX.search(string)
        if not match:
            raise InvalidTagFormat(f"{string} is not in the correct tag format.")

        tag = match.group("tag")
        tag_type = match.group("type")
        value = TYPES[tag_type](match.group("value"))

        return Tag(tag, tag_type, value)

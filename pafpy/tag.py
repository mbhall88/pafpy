"""A module for wrapping SAM-like optional fields (tags) generally used in PAF files.

The full specifications can be found [here][specs].

The main class of interest in this module is `pafpy.tag.Tag`. It can be imported into your
project like so

```py
from pafpy import Tag
```
[specs]: https://samtools.github.io/hts-specs/SAMtags.pdf
"""
import re
from typing import NamedTuple, Pattern, Type, Union

DELIM = ":"


class InvalidTagFormat(Exception):
    """An exception used to indicate the format of a tag string is invalid."""

    pass


class UnknownTagTypeChar(Exception):
    """An exception used to indicate that the passed TYPE character from a `Tag` is not
    known.
    """

    pass


class TagType(NamedTuple):
    """A tuple holding information relating to a `Tag`'s type."""

    char: str
    """The single character representing the tag type."""
    python_type: Type
    """The python type used to encode the associated `Tag` value."""
    value_regex: Pattern
    """A regular expression that the `Tag` value must conform to for this type."""


TagTypes = {
    "A": TagType(
        char="A", python_type=str, value_regex=re.compile(r"(?P<value>[!-~])")
    ),
    "i": TagType(
        char="i", python_type=int, value_regex=re.compile(r"(?P<value>[-+]?\d+)"),
    ),
    "f": TagType(
        char="f",
        python_type=float,
        value_regex=re.compile(r"(?P<value>[-+]?(\d*\.?\d+([eE][-+]?\d+)?)|inf)"),
    ),
    "Z": TagType(
        char="Z", python_type=str, value_regex=re.compile(r"(?P<value>[ !-~]*)"),
    ),
}


TAG_REGEX = re.compile(
    rf"^(?P<tag>\w{{2}}){DELIM}(?P<type>[{''.join(TagTypes)}]){DELIM}(?P<value>.*)$"
)


class Tag(NamedTuple):
    """Class representing a single SAM-like optional field (tag).

    There are two ways to construct a `Tag`:

    1. The default constructor, where you specify each member variable manually.
    2. Using the `Tag.from_str` factory constructor method.

    > *Note: It is recommended that you construct tags using the `Tag.from_str`
    constructor as it has some additional logic to ensure the type of the value is
    inferred correctly.*

    ## Example
    ```py
    from pafpy import Tag

    # default constructor
    tag = Tag(tag="NM", type="i", value=50)
    assert str(tag) == "NM:i:50"
    assert tag.value == 50

    # from_str factory constructor
    tag_from_str = Tag.from_str("NM:i:50")
    assert tag_from_str == tag
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
        from pafpy import Tag

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
            raise InvalidTagFormat(f"{string} is not in valid TAG:TYPE:VALUE format.")

        tag = match.group("tag")
        # this dict access should not fail as we would not have got a regex match if
        # there was an invalid tag type
        tag_type = TagTypes[match.group("type")]

        value_string = match.group("value")
        value_match = tag_type.value_regex.match(value_string)
        if not value_match:
            raise InvalidTagFormat(f"VALUE of tag {string} is not the expected TYPE")

        value = tag_type.python_type(value_string)

        return Tag(tag, tag_type.char, value)

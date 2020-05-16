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
from enum import Enum
from typing import NamedTuple, Pattern, Set, Type, Union

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


class TagTypes(Enum):
    """An `Enum` used to collate all possible `Tag` types.

    The value of each variant is a `TagType`.
    The recommended way of initialising a `TagTypes` object is via the factory
    constructor `TagTypes.from_char`.

    For further information, refer to the [optional fields][tags] section of the SAM
    specifications.
    [tags]: https://samtools.github.io/hts-specs/SAMv1.pdf#subsection.1.5

    ## Example
    ```py
    from pafpy import TagType, TagTypes

    tag_type = TagTypes.from_char("i")
    assert tag_type == TagTypes.Integer
    ```

    ## Errors
    If `char` is not in the set of known characters, an `UnknownTagTypeChar`
    exception will be raised.
    """

    Character = TagType(
        char="A", python_type=str, value_regex=re.compile(r"(?P<value>[!-~])")
    )
    Integer = TagType(
        char="i", python_type=int, value_regex=re.compile(r"(?P<value>[-+]?\d+)"),
    )
    RealNumber = TagType(
        char="f",
        python_type=float,
        value_regex=re.compile(r"(?P<value>[-+]?\d*\.?\d+([eE][-+]?\d+)?)"),
    )
    String = TagType(
        char="Z", python_type=str, value_regex=re.compile(rf"(?P<value>[ !-~]*)"),
    )

    @staticmethod
    def chars() -> Set[str]:
        """Returns a set of all the characters supported by this enum."""
        return {tag_type.value.char for tag_type in TagTypes}

    @staticmethod
    def from_char(char: str) -> "TagTypes":
        """Initialise a `TagTypes` from a character (`str`).

        ## Example
        ```py
        from pafpy import TagType, TagTypes

        tag_type = TagTypes.from_char("i")
        assert tag_type == TagTypes.Integer
        ```

        ## Errors
        If `char` is not in the set of known characters, an `UnknownTagTypeChar`
        exception will be raised.
        """
        for tag_type in TagTypes:
            if char == tag_type.value.char:
                return tag_type
        raise UnknownTagTypeChar(
            f"{char} is not in the set of known tag types {TagTypes.chars()}"
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
        tag_regex = re.compile(
            rf"^(?P<tag>\w{{2}}){DELIM}(?P<type>[{''.join(TagTypes.chars())}]){DELIM}(?P<value>.*)$"
        )
        match = tag_regex.search(string)
        if not match:
            raise InvalidTagFormat(f"{string} is not in the correct tag format.")

        tag = match.group("tag")
        tag_type = TagTypes.from_char(match.group("type")).value
        value_string = match.group("value")
        value_match = tag_type.value_regex.search(value_string)
        if not value_match:
            raise InvalidTagFormat(f"{string} is not in the correct tag format.")

        value = tag_type.python_type(value_match.group("value"))

        return Tag(tag, tag_type.char, value)

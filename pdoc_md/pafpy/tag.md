Module pafpy.tag
================
A module for wrapping SAM-like optional fields (tags) generally used in PAF files.

The full specifications can he found [here][specs].

The main class of interest in this module is `Tag`. It can be imported into your
project like so

```py
from pafpy import Tag
```
[specs]: https://samtools.github.io/hts-specs/SAMtags.pdf

Classes
-------

`InvalidTagFormat(...)`
:   An exception used to indicate the format of a tag string is invalid.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`Tag(tag: str, type: str, value: Union[str, float, int])`
:   Class representing a single SAM-like optional field (tag).
    
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

    ### Ancestors (in MRO)

    * builtins.tuple

    ### Static methods

    `from_str(string: str) -> pafpy.tag.Tag`
    :   Construct a `Tag` from a string.
        
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

    ### Instance variables

    `tag`
    :   The two character key identifying the tag. e.g. "NM" or "cg".

    `type`
    :   A single character indicating the type of `value`. e.g. "A" or "i".

    `value`
    :   The value of the tag.

`TagType(char: str, python_type: Type, value_regex: Pattern[~AnyStr])`
:   A tuple holding information relating to a `Tag`'s type.

    ### Ancestors (in MRO)

    * builtins.tuple

    ### Instance variables

    `char`
    :   The single character representing the tag type.

    `python_type`
    :   The python type used to encode the associated `Tag` value.

    `value_regex`
    :   A regular expression that the `Tag` value must conform to for this type.

`TagTypes(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   An `Enum` used to collate all possible `Tag` types.
    
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

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `Character`
    :

    `Integer`
    :

    `RealNumber`
    :

    `String`
    :

`UnknownTagTypeChar(...)`
:   An exception used to indicate that the passed TYPE character from a `Tag` is not
    known.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException
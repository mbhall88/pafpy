import pytest

from pafpy.tag import InvalidTagFormat, Tag, TagTypes, UnknownTagTypeChar


class TestStr:
    def test_str_value(self):
        tag = Tag(tag="tg", type="A", value="P")

        actual = str(tag)
        expected = "tg:A:P"

        assert actual == expected

    def test_int_value(self):
        tag = Tag(tag="NM", type="i", value=50)

        actual = str(tag)
        expected = "NM:i:50"

        assert actual == expected

    def test_float_value(self):
        tag = Tag(tag="de", type="f", value=0.5)

        actual = str(tag)
        expected = "de:f:0.5"

        assert actual == expected


class TestFromStr:
    def test_invalid_string_raises_error(self):
        string = "foo"

        with pytest.raises(InvalidTagFormat):
            Tag.from_str(string)

    def test_tag_missing_field(self):
        string = "NM:i:"

        with pytest.raises(InvalidTagFormat):
            Tag.from_str(string)

    def test_unknown_tag_type_raises_error(self):
        string = "NM:x:5"

        with pytest.raises(InvalidTagFormat):
            Tag.from_str(string)

    def test_tag_too_long_raises_error(self):
        string = "NMP:i:5"

        with pytest.raises(InvalidTagFormat):
            Tag.from_str(string)

    def test_tag_type_too_long_raises_error(self):
        string = "NM:ii:5"

        with pytest.raises(InvalidTagFormat):
            Tag.from_str(string)

    def test_tag_with_string_value_parsed(self):
        tag = "cg"
        tag_type = "Z"
        value = "97M1I13M"
        string = ":".join([tag, tag_type, value])

        actual = Tag.from_str(string)
        expected = Tag(tag, tag_type, value)

        assert actual == expected

    def test_tag_with_char_value_parsed(self):
        tag = "tg"
        tag_type = "A"
        value = "P"
        string = ":".join([tag, tag_type, value])

        actual = Tag.from_str(string)
        expected = Tag(tag, tag_type, value)

        assert actual == expected

    def test_tag_with_non_letter_char_value_parsed(self):
        tag = "tg"
        tag_type = "A"
        value = "*"
        string = ":".join([tag, tag_type, value])

        actual = Tag.from_str(string)
        expected = Tag(tag, tag_type, value)

        assert actual == expected

    def test_tag_with_int_value_parsed(self):
        tag = "NM"
        tag_type = "i"
        value = 50
        string = ":".join([tag, tag_type, str(value)])

        actual = Tag.from_str(string)
        expected = Tag(tag, tag_type, value)

        assert actual == expected

    def test_tag_with_float_value_parsed(self):
        tag = "de"
        tag_type = "f"
        value = 0.0391
        string = ":".join([tag, tag_type, str(value)])

        actual = Tag.from_str(string)
        expected = Tag(tag, tag_type, value)

        assert actual == expected


class TestTagTypesFromChar:
    def test_empty_string_raises_error(self):
        char = ""

        with pytest.raises(UnknownTagTypeChar):
            TagTypes.from_char(char)

    def test_unknown_char_raises_error(self):
        char = "?"

        with pytest.raises(UnknownTagTypeChar):
            TagTypes.from_char(char)

    def test_too_many_characters_raises_error(self):
        char = "AZ"

        with pytest.raises(UnknownTagTypeChar):
            TagTypes.from_char(char)

    def test_character_returns_expected(self):
        char = "A"

        actual = TagTypes.from_char(char)
        expected = TagTypes.Character

        assert actual == expected

    def test_integer_returns_expected(self):
        char = "i"

        actual = TagTypes.from_char(char)
        expected = TagTypes.Integer

        assert actual == expected

    def test_float_returns_expected(self):
        char = "f"

        actual = TagTypes.from_char(char)
        expected = TagTypes.RealNumber

        assert actual == expected

    def test_string_returns_expected(self):
        char = "Z"

        actual = TagTypes.from_char(char)
        expected = TagTypes.String

        assert actual == expected

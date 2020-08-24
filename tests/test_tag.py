import pytest

from pafpy.tag import InvalidTagFormat, Tag


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

    def test_tag_with_inf_float_value_parsed(self):
        tag = "de"
        tag_type = "f"
        value = "inf"
        string = ":".join([tag, tag_type, str(value)])

        actual = Tag.from_str(string)
        expected = Tag(tag, tag_type, float(value))

        assert actual == expected

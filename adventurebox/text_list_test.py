import pytest
from adventurebox.text_list import TextList
from adventurebox.text import Text


@pytest.fixture
def text_list():
    return TextList()


def test_insert(text_list: TextList):
    text_list.insert("Hello")
    assert len(text_list) == 5
    assert text_list.current_text.text == "Hello"
    assert text_list._text_ptr == 1


def test_len(text_list):
    text_list.insert("Hello")
    text_list.insert("World")
    assert len(text_list) == 10
    assert text_list.line_count == 2


def test_text_line_spans(text_list: TextList):
    text_list.insert("Hello")
    text_list.insert("World")
    assert text_list._text_line_spans == [(0, 1), (1, 2)]

    text_list.insert("foo\nbar")
    assert text_list._text_line_spans == [(0, 1), (1, 2), (2, 4)]
    text_list.insert("fizbuz")
    assert text_list._text_line_spans == [(0, 1), (1, 2), (2, 4), (4, 5)]


def test_getitem_single(text_list):
    text_list.insert("Hello")
    text_list.insert("World")
    assert text_list[0] == "Hello"
    assert text_list[1] == "World"

    text_list.insert("foo\nbar")
    assert text_list[0] == "Hello"
    assert text_list[1] == "World"
    assert text_list[2] == "foo"
    assert text_list[3] == "bar"

    text_list.insert("fizbuz")
    assert text_list[4] == "fizbuz"


def test_getitem_slice(text_list):
    text_list.insert("Hello")
    text_list.insert("World")
    assert text_list[0:2] == ["Hello", "World"]

    text_list.insert("foo\nbar")
    assert text_list[0:2] == ["Hello", "World"]
    assert text_list[1:3] == ["World", "foo"]
    assert text_list[0:3] == ["Hello", "World", "foo"]
    assert text_list[1:4] == ["World", "foo", "bar"]
    assert text_list[2:4] == ["foo", "bar"]
    assert text_list[0:4] == ["Hello", "World", "foo", "bar"]

    text_list.insert("fizbuz")
    assert text_list[0:4] == ["Hello", "World", "foo", "bar"]


def test_getitem_negative_index(text_list):
    text_list.insert("Hello")
    text_list.insert("World")
    assert text_list[-1] == "World"


def test_getitem_negative_slice(text_list):
    text_list.insert("Hello")
    text_list.insert("World")
    assert text_list[-2:] == ["Hello", "World"]


def test_getitem_negative_slice(text_list):
    text_list.insert("Hello")
    text_list.insert("World")
    with pytest.raises(IndexError):
        text_list[::-1]
    with pytest.raises(IndexError):
        text_list[::2]


def test_getitem_out_of_range(text_list):
    text_list.insert("Hello")
    text_list.insert("World")
    with pytest.raises(IndexError):
        text_list[2]


def test_getitem_invalid_type(text_list):
    text_list.insert("Hello")
    text_list.insert("World")
    with pytest.raises(TypeError):
        text_list["invalid"]


def test_getitem_max_line_length(text_list):
    text_list.max_line_width = 3
    text_list.insert("Hello")
    text_list.insert("World")
    assert text_list.line_count == 4
    assert text_list._text_line_spans == [(0, 2), (2, 4)]
    assert text_list._texts[0].lines == ["Hel", "lo"]
    assert text_list[0] == "Hel"
    assert text_list[1] == "lo"
    assert text_list[2] == "Wor"
    assert text_list[3] == "ld"
    assert text_list[0:2] == ["Hel", "lo"]
    assert text_list[0:3] == ["Hel", "lo", "Wor"]
    assert text_list[0:4] == ["Hel", "lo", "Wor", "ld"]
    assert text_list[1:4] == ["lo", "Wor", "ld"]
    assert text_list[2:4] == ["Wor", "ld"]
    assert text_list[1:3] == ["lo", "Wor"]


# def test_get_item_max_line_length_after_items_added(text_list):
#     text_list.insert("Hello")
#     text_list.insert("World")
#     text_list.max_line_width = 3
#     assert text_list[0:2] == ["Hel", "lo", "Wor", "ld"]

# text_list.insert("foo\nbar")
# assert text_list[0:2] == ["Hello", "World"]
# assert text_list[1:3] == ["World", "foo"]
# assert text_list[0:3] == ["Hello", "World", "foo"]
# assert text_list[1:4] == ["World", "foo", "bar"]
# assert text_list[2:4] == ["foo", "bar"]
# assert text_list[0:4] == ["Hello", "World", "foo", "bar"]

# text_list.insert("fizbuz")
# assert text_list[0:4] == ["Hello", "World", "foo", "bar"]
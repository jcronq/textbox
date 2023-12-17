import pytest
from textbox.text_list import TextList
from textbox.text import Text


@pytest.fixture
def text_list():
    return TextList()


def test_insert(text_list: TextList):
    text_list.insert("Hello")
    assert len(text_list) == 5
    assert text_list.current_text.text == "Hello"
    assert text_list._text_ptr == 1


def test_len(text_list: TextList):
    text_list.insert("Hello")
    text_list.increment_text_ptr()
    text_list.insert("World")
    assert len(text_list) == 10
    assert text_list.line_count == 2


def test_text_line_spans(text_list: TextList):
    text_list.insert("Hello")
    text_list.increment_text_ptr()
    text_list.insert("World")
    text_list.increment_text_ptr()
    assert text_list._text_line_spans == [(0, 1), (1, 2)]

    text_list.insert("foo\nbar")
    text_list.increment_text_ptr()
    assert text_list._text_line_spans == [(0, 1), (1, 2), (2, 4)]
    text_list.insert("fizbuz")
    assert text_list._text_line_spans == [(0, 1), (1, 2), (2, 4), (4, 5)]


def test_getitem_single(text_list: TextList):
    text_list.insert("Hello")
    text_list.increment_text_ptr()
    text_list.insert("World")
    text_list.increment_text_ptr()
    assert text_list[0] == "Hello"
    assert text_list[1] == "World"

    text_list.insert("foo\nbar")
    text_list.increment_text_ptr()
    assert text_list[0] == "Hello"
    assert text_list[1] == "World"
    assert text_list[2] == "foo"
    assert text_list[3] == "bar"

    text_list.insert("fizbuz")
    assert text_list[4] == "fizbuz"


def test_getitem_slice(text_list: TextList):
    text_list.insert("Hello")
    text_list.increment_text_ptr()
    text_list.insert("World")
    text_list.increment_text_ptr()
    assert text_list[0:2] == ["Hello", "World"]

    text_list.insert("foo\nbar")
    text_list.increment_text_ptr()
    assert text_list[0:2] == ["Hello", "World"]
    assert text_list[1:3] == ["World", "foo"]
    assert text_list[0:3] == ["Hello", "World", "foo"]
    assert text_list[1:4] == ["World", "foo", "bar"]
    assert text_list[2:4] == ["foo", "bar"]
    assert text_list[0:4] == ["Hello", "World", "foo", "bar"]

    text_list.insert("fizbuz")
    text_list.increment_text_ptr()
    assert text_list[0:4] == ["Hello", "World", "foo", "bar"]


def test_getitem_negative_index(text_list: TextList):
    text_list.insert("Hello")
    text_list.increment_text_ptr()
    text_list.insert("World")
    text_list.increment_text_ptr()
    assert text_list[-1] == "World"


def test_getitem_negative_slice(text_list: TextList):
    text_list.insert("Hello")
    text_list.increment_text_ptr()
    text_list.insert("World")
    text_list.increment_text_ptr()
    assert text_list[-2:] == ["Hello", "World"]


def test_getitem_negative_slice(text_list: TextList):
    text_list.insert("Hello")
    text_list.increment_text_ptr()
    text_list.insert("World")
    text_list.increment_text_ptr()
    with pytest.raises(IndexError):
        text_list[::-1]
    with pytest.raises(IndexError):
        text_list[::2]


def test_getitem_out_of_range(text_list: TextList):
    text_list.insert("Hello")
    text_list.increment_text_ptr()
    text_list.insert("World")
    text_list.increment_text_ptr()
    with pytest.raises(IndexError):
        text_list[2]


def test_getitem_invalid_type(text_list: TextList):
    text_list.insert("Hello")
    text_list.increment_text_ptr()
    text_list.insert("World")
    text_list.increment_text_ptr()
    with pytest.raises(TypeError):
        text_list["invalid"]


def test_getitem_max_line_length(text_list: TextList):
    text_list.max_line_width = 3
    text_list.insert("Hello")
    text_list.increment_text_ptr()
    text_list.insert("World")
    text_list.increment_text_ptr()
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


def test_cursor_position_empty_str(text_list: TextList):
    text_list.insert("")
    assert text_list.cursor_position == (0, 0)


def test_cursor_position_insert_str(text_list: TextList):
    text_list.insert("Hello")
    assert text_list.cursor_position == (0, 4)
    text_list.increment_text_ptr()
    assert text_list.cursor_position == (1, 0)
    text_list.insert("World")
    assert text_list.cursor_position == (1, 4)
    text_list.increment_text_ptr()
    assert text_list.cursor_position == (2, 0)
    text_list.insert("hohoh")
    assert text_list.cursor_position == (2, 4)
    text_list.max_line_width = 3
    assert text_list.cursor_position == (5, 1)


def test_cursor_position_add_text(text_list: TextList):
    text_list.add_text(Text("Hello"))
    assert text_list.cursor_position == (0, 4)
    text_list.add_text(Text("World"))
    assert text_list.cursor_position == (1, 4)
    text_list.add_text(Text("hohoh"))
    assert text_list.cursor_position == (2, 4)
    text_list.max_line_width = 3
    assert text_list.cursor_position == (6, 1)
    text_list.add_text(Text("huoo\nrah"))
    assert text_list.cursor_position == (8, 2)
    assert text_list[0] == "Hel"
    assert text_list[:2] == ["Hel", "lo"]


def test_cursor_position_add_text(text_list: TextList):
    text_list.add_text(Text("Hello"))
    text_list.add_text(Text("World"))
    long_list = "\n".join((str(idx) for idx in range(1, 11)))
    text_list.add_text(Text(long_list))
    assert text_list.cursor_position == (11, 1)


def test_insert(text_list: TextList):
    text_list.insert("Hello")
    text_list.insert(" World!")
    assert text_list[0] == "Hello World!"
    assert text_list.cursor_position == (0, 11)
    text_list.increment_text_ptr()
    assert text_list.cursor_position == (1, 0)
    assert text_list[0] == "Hello World!"
    assert text_list.as_string == "Hello World!"

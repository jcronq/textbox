import pytest
from textbox.text import Text
from textbox.text_line import TextLine
from textbox.box_types import Position


def test_init():
    assert Text().text == ""
    assert len(Text()._text_lines) == 0
    assert Text("").text == ""
    assert len(Text("")._text_lines) == 0
    assert Text("hello").text == "hello"
    assert len(Text("hello")._text_lines) == 1
    assert Text("hello\nworld").text == "hello\nworld"
    assert len(Text("hello\nworld")._text_lines) == 2
    assert Text("hello\nworld\n").text == "hello\nworld\n"
    assert len(Text("hello\nworld\n")._text_lines) == 3
    assert Text("hello\n\nworld\n").text == "hello\n\nworld\n"
    assert len(Text("hello\n\nworld\n")._text_lines) == 4
    assert Text("hello\n\nworld\n\n").text == "hello\n\nworld\n\n"
    assert len(Text("hello\n\nworld\n\n")._text_lines) == 5
    assert Text("\nhello\n\nworld\n\n").text == "\nhello\n\nworld\n\n"
    assert len(Text("\nhello\n\nworld\n\n")._text_lines) == 6
    assert Text("\n\nhello\n\nworld\n\n").text == "\n\nhello\n\nworld\n\n"
    assert len(Text("\n\nhello\n\nworld\n\n")._text_lines) == 7


def test_text_setting():
    test = Text()
    test.text = "hello"
    assert test.text == "hello"
    test.text = [TextLine("hello")]
    assert test.text == "hello"


def test_init_pointers():
    text = Text("hello\nworld")
    assert text.cursor_position == (1, 4)

    # text = Text("hello\nworld\n")
    # assert text.cursor_position == (2, 0)
    # assert text.insert("!")
    # assert text.cursor_position == (2, 0)

    # text = Text("hello\n\nworld")
    # assert text.cursor_position == (2, 4)


def test_current_line():
    text = Text("hello\nworld")
    assert text.current_line == TextLine("world")

    text = Text("hello\nworld\n")
    assert text.current_line == TextLine("")

    text = Text("hello\n\n\nbye")
    assert text.current_line == TextLine("bye")
    assert text.previous_line == TextLine("")


def test_previous_line():
    text = Text()
    assert text.previous_line == None
    assert text.current_line == TextLine("")
    assert str(text.current_line) == ""

    text = Text("hello\nworld")
    assert text.previous_line == TextLine("hello")

    text = Text("hello\nworld\n")
    assert text.previous_line == TextLine("world")

    text = Text("hello\n\nworld\nbye")
    assert text.previous_line == TextLine("world")

    text = Text("hello\n\nworld\nbye\n\n")
    assert text.previous_line == TextLine("")


def test_increment_decrement_line_ptr():
    text = Text("hello\nworld")
    text.increment_line_ptr()
    assert text.cursor_position == (1, 4)
    assert text.current_line == TextLine("world")
    assert text.previous_line == TextLine("hello")

    text = Text("hello\nworld\n")
    text.increment_line_ptr()
    assert text.cursor_position == (2, 0)
    assert text.current_line == TextLine("")
    assert text.previous_line == TextLine("world")

    text = Text("hello\nwo")
    text.decrement_line_ptr()
    assert text.cursor_position == (0, 1)
    assert text.current_line == TextLine("hello")
    assert text.previous_line == None

    text = Text("hello\nwo")
    text.decrement_line_ptr()
    text.decrement_line_ptr()
    assert text.cursor_position == (0, 1)
    assert text.current_line == TextLine("hello")
    assert text.previous_line == None


def test_increment_decrement_column_ptr():
    text = Text("hello\nworld")
    text.increment_column_ptr()
    assert text.cursor_position == (1, 4)
    assert text.current_line == TextLine("world")
    assert text.previous_line == TextLine("hello")

    text = Text("hello\nworld\n")
    text.increment_column_ptr()
    assert text.cursor_position == (2, 0)
    assert text.current_line == TextLine("")
    assert text.previous_line == TextLine("world")

    text = Text("hello\nwo")
    text.decrement_column_ptr()
    assert text.cursor_position == (1, 0)
    assert text.current_line == TextLine("wo")
    assert text.previous_line == TextLine("hello")

    text.decrement_column_ptr()
    assert text.cursor_position == (0, 4)
    assert text.current_line == TextLine("hello")
    assert text.previous_line == None
    text.decrement_column_ptr()
    assert text.cursor_position == (0, 3)
    text.increment_column_ptr()
    assert text.cursor_position == (0, 4)
    text.increment_column_ptr()
    assert text.cursor_position == (1, 0)
    assert text.current_line == TextLine("wo")
    text.decrement_column_ptr()
    assert text.cursor_position == (0, 4)
    text.decrement_column_ptr()
    text.decrement_column_ptr()
    text.decrement_column_ptr()
    assert text.cursor_position == (0, 1)
    text.decrement_column_ptr()
    assert text.cursor_position == (0, 0)
    assert text.current_line == TextLine("hello")
    assert text.previous_line == None

    text = Text("hello\n\n1234567890")
    assert text.cursor_position == (2, 9)
    for _ in range(9):
        text.decrement_column_ptr()
    assert text.cursor_position == (2, 0)
    assert text.current_line == TextLine("1234567890")
    assert text.previous_line == TextLine("")
    text.decrement_column_ptr()
    assert text.cursor_position == (1, 0)
    assert text.current_line == TextLine("")
    assert text.previous_line == TextLine("hello")


def test_to_end_of_line():
    test = Text("hello\nworld")
    test.to_end_of_line()
    assert test.cursor_position == (1, 4)

    test = Text("hello\nwo")
    test.decrement_line_ptr()
    assert test.cursor_position == (0, 1)

    test.to_end_of_line()
    assert test.cursor_position == (0, 4)

    test = Text("hello\n\n1234567890")
    test.decrement_line_ptr()
    test.increment_line_ptr()
    test.to_end_of_line()
    assert test.cursor_position == (2, 9)


def test_to_start_of_line():
    test = Text("hello\nworld")
    test.to_start_of_line()
    assert test.cursor_position == (1, 0)

    test = Text("hello\nwo")
    test.decrement_line_ptr()
    assert test.cursor_position == (0, 1)
    test.to_start_of_line()
    assert test.cursor_position == (0, 0)

    test = Text("hello\n\n1234567890")
    test.decrement_line_ptr()
    test.increment_line_ptr()
    test.to_start_of_line()
    assert test.cursor_position == (2, 0)


def test_edit_mode_navigation():
    test = Text("hello\nworld")
    test.edit_mode = True
    test.to_end_of_line()
    assert test.cursor_position == (1, 5)
    test.to_start_of_line()
    assert test.cursor_position == (1, 0)
    test.decrement_column_ptr()
    assert test.cursor_position == (0, 5)
    test.decrement_column_ptr()
    assert test.cursor_position == (0, 4)
    test.to_start_of_line()
    assert test.cursor_position == (0, 0)
    test.to_end_of_line()
    assert test.cursor_position == (0, 5)
    test.increment_column_ptr()
    assert test.cursor_position == (1, 0)
    test.to_end_of_line()
    assert test.cursor_position == (1, 5)
    test.edit_mode = False
    assert test.cursor_position == (1, 4)


def test_insert():
    test = Text("hello\nworld")
    test.edit_mode = True
    test.increment_column_ptr()
    test.insert("!")
    assert test.text == "hello\nworld!"
    assert test.cursor_position == (1, 6)
    assert test.current_line == TextLine("world!")
    assert test.previous_line == TextLine("hello")

    test = Text("hello\nworld")
    test.edit_mode = True
    test.increment_column_ptr()
    test.decrement_line_ptr()
    test.insert("!")
    assert test.text == "hello!\nworld"
    assert test.cursor_position == (0, 6)
    assert test.current_line == TextLine("hello!")
    assert test.previous_line == None

    test = Text("world")
    test.edit_mode = True
    test.to_start_of_line()
    test.insert("\n")
    assert test.text == "\nworld"
    assert test.cursor_position == (1, 0)


def test_delete_line():
    test = Text("")
    test.delete_line()
    assert test.text == ""
    assert test.current_line == TextLine("")
    assert test.previous_line == None
    assert test.cursor_position == (0, 0)

    test = Text("hello")
    test.delete_line()
    assert test.text == ""
    assert test.current_line == TextLine("")
    assert test.previous_line == None
    assert test.cursor_position == (0, 0)

    test = Text("hello\nworld")
    assert test.current_line == TextLine("world")
    assert test.previous_line == TextLine("hello")
    test.delete_line()
    assert test.current_line == TextLine("hello")
    assert test.previous_line == None
    assert test.cursor_position == (0, 4)

    test = Text("hello\nworld\n")
    test.delete_line()
    assert test.text == "hello\nworld"
    assert test.current_line == TextLine("world")
    assert test.previous_line == TextLine("hello")

    test = Text("hello\n\nworld")
    test.decrement_line_ptr()
    test.delete_line()
    assert test.text == "hello\nworld"
    assert test.text == "hello\nworld"
    assert test.current_line == TextLine("world")
    assert test.previous_line == TextLine("hello")
    assert test.cursor_position == (1, 0)

    test = Text("hello\n\nworld\n")
    assert test.line_count == 4
    test.delete_line()
    assert test.text == "hello\n\nworld"
    assert test.line_count == 3
    assert test.current_line == TextLine("world")
    test.delete_line()
    assert test.line_count == 2
    assert test.text == "hello\n"
    assert test.current_line == TextLine("")
    test.delete_line()
    assert test.line_count == 1
    assert test.text == "hello"
    assert test.current_line == TextLine("hello")
    test.delete_line()
    assert test.line_count == 0
    assert test.text == ""
    assert test.current_line == TextLine("")
    assert test.cursor_position == (0, 0)


def test_backspace():
    test = Text("hello\nworld")
    test.backspace()
    assert test.text == "hello\nword"
    assert test.cursor_position == (1, 3)

    test = Text("hello\nworld")
    test.edit_mode = True
    test.increment_column_ptr()
    test.backspace()
    assert test.text == "hello\nworl"
    assert test.cursor_position == (1, 4)

    test = Text("hello\nworld")
    test.edit_mode = True
    test.increment_column_ptr()
    test.decrement_line_ptr()
    test.backspace()
    assert test.text == "hell\nworld"

    test = Text("hello\nworld")
    test.to_start_of_line()
    test.backspace()
    assert test.text == "helloworld"
    assert test.cursor_position == (0, 5)

    test = Text("hello\nworld")
    test.edit_mode = True
    test.to_start_of_line()
    test.backspace()
    assert test.text == "helloworld"
    assert test.cursor_position == (0, 5)

    test = Text("\nworld")
    test.edit_mode = True
    test.to_start_of_line()
    test.backspace()
    assert test.text == "world"
    assert test.cursor_position == (0, 0)


def test_insert_from_empty():
    test = Text()
    test.edit_mode = True
    test.edit_mode = False
    test.edit_mode = True
    test.insert("h")
    test.insert("e")
    assert test.text == "he"


def test_for_insert_bug():
    test = Text()
    test.edit_mode = True
    test.insert("h")
    test.insert("i")
    test.decrement_column_ptr()
    test.insert("\n")
    assert test.cursor_position == (1, 0)


def test_start_of_next_word():
    test = Text("hello world")
    test.to_start_of_line()
    assert test.start_of_next_word() == Position(0, 6)


def test_start_of_next_word():
    test = Text("hello world")
    test.to_start_of_line()
    assert test.start_of_next_word() == Position(0, 6)
    for _ in range(6):
        test.increment_column_ptr()
    assert test.start_of_next_word() == None
    test.edit_mode = True
    test.to_end_of_text()
    test.insert("\nnospace")
    test.to_start_of_text()
    test.to_end_of_line()
    test.decrement_column_ptr()
    test.decrement_column_ptr()
    assert test.start_of_next_word() == Position(1, 0)


def test_start_of_previous_word():
    test = Text("hello world")
    assert test.start_of_previous_word() == Position(0, 6)
    for _ in range(4):
        test.decrement_column_ptr()
    assert test.start_of_previous_word() == Position(0, 0)
    test.decrement_column_ptr()
    assert test.start_of_previous_word() == Position(0, 0)
    test.decrement_column_ptr()
    assert test.start_of_previous_word() == Position(0, 0)
    test.to_start_of_text()
    assert test.start_of_previous_word() == None


def test_insert_from_empty():
    test = Text()
    test.edit_mode = False
    with pytest.raises(RuntimeError):
        test.insert("h")

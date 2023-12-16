import pytest
from adventurebox.text import Text
from adventurebox.text_line import TextLine


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
    text.insert("!")
    assert text.cursor_position == (0, 2)
    assert text.current_line == TextLine("h!ello")
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
    # breakpoint()
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

    # test = Text("hello\nworld\n")
    # test.edit_mode = True
    # test.increment_line_ptr()
    # test.backspace()
    # assert test.text == "hello\nworld"


def test_insert_from_empty():
    test = Text()
    test.edit_mode = True
    test.insert("h")
    test.insert("e")
    assert test.text == "he"


# def test_break_line():
#     test = Text("hello\nworld")
#     test.break_line()
#     assert test.text == "hello\nworld\n"
#     assert test.line_ptr == 2
#     assert test.column_ptr == 0

#     test = Text("hello world")
#     test._line_ptr = 0
#     test._column_ptr = 5
#     test.break_line()
#     assert test.text == "hello\n world"
#     assert test._line_ptr == 1
#     assert test._column_ptr == 0

#     test = Text("hello world")
#     test._line_ptr = 0
#     test._column_ptr = 5
#     test.break_line()
#     test.break_line()
#     assert test.text == "hello\n\n world"
#     assert test._line_ptr == 2
#     assert test._column_ptr == 0


# def test_replace_character():
#     test = Text("hello\nworld")
#     test._line_ptr = 0
#     test._column_ptr = 0
#     test.replace_character("!")
#     assert test.text == "!ello\nworld"
#     assert test._line_ptr == 0
#     assert test._column_ptr == 1

#     test = Text("hello\nworld")
#     test._line_ptr = 1
#     test._column_ptr = 5
#     test.replace_character("!")
#     assert test.text == "hello\nworld!"
#     assert test._line_ptr == 1
#     assert test._column_ptr == 6

#     test = Text("hello\nworld")
#     test.decrement_column_ptr()
#     test.replace_character("!")
#     assert test.text == "hello\nworl!"
#     assert test._line_ptr == 1
#     assert test._column_ptr == 5

#     test = Text("hello\nworld")
#     test._line_ptr = 0
#     test._column_ptr = 5
#     test.replace_character("!")
#     assert test.text == "hello!\nworld"
#     assert test._line_ptr == 0
#     assert test._column_ptr == 6

#     test = Text("hello\nworld")
#     test._line_ptr = 0
#     test._column_ptr = 3
#     test.replace_character("!")
#     assert test.text == "hel!o\nworld"
#     assert test._line_ptr == 0
#     assert test._column_ptr == 4

#     test = Text("hello\nworld")
#     test._line_ptr = 0
#     test._column_ptr = 3
#     test.replace_character("!")
#     test.replace_character("!")
#     test.replace_character("!")
#     assert test.text == "hel!!!\nworld"
#     assert test._line_ptr == 0
#     assert test._column_ptr == 6

#     test = Text("hello\nworld")
#     test._line_ptr = 0
#     test._column_ptr = 0
#     test.replace_character("!")
#     assert test.text == "!ello\nworld"
#     assert test._line_ptr == 0
#     assert test._column_ptr == 1

#     test = Text("hello\nworld")
#     test._line_ptr = 0
#     test._column_ptr = 0
#     test.replace_character("!")
#     test.replace_character("!")
#     assert test.text == "!!llo\nworld"
#     assert test._line_ptr == 0
#     assert test._column_ptr == 2

#     test = Text("hello\nworld")
#     test._line_ptr = 1
#     test._column_ptr = 0
#     test.replace_character("!")
#     assert test.text == "hello\n!orld"
#     assert test._line_ptr == 1
#     assert test._column_ptr == 1

#     test = Text("hello world")
#     test._line_ptr = 0
#     test._column_ptr = 5
#     test.replace_character("\n")
#     assert test.text == "hello\nworld"
#     assert test._line_ptr == 1
#     assert test._column_ptr == 0

#     test = Text("hello world")
#     test._line_ptr = 0
#     test._column_ptr = 10
#     test.replace_character("\n")
#     assert test.text == "hello worl\n"
#     assert test._line_ptr == 1
#     assert test._column_ptr == 0

#     test = Text("hello\nworld\n")
#     test.replace_character("!")
#     assert test.text == "hello\nworld\n!"
#     assert test._line_ptr == 2
#     assert test._column_ptr == 1

#     with pytest.raises(ValueError):
#         test._column_ptr = -1
#         test.replace_character("d")

#     with pytest.raises(ValueError):
#         test._column_ptr = 7
#         test.replace_character("h")

#     with pytest.raises(ValueError):
#         test._column_ptr = 0
#         test.replace_character("he")

#     test = Text("hello world")
#     test._line_ptr = 0
#     test._column_ptr = 11
#     test.replace_character("\n")
#     assert test.text == "hello world\n"


# def test_dunders():
#     test = Text("hello\nworld")
#     assert 0 in test
#     assert 1 in test
#     assert 2 not in test
#     assert -1 not in test

#     assert str(test[0]) == "hello"
#     assert str(test[1]) == "world"


# def test_with_max_line_width():
#     test = Text("hello world", max_line_width=5)
#     assert test.line_count == 3
#     assert test.text == "hello\n worl\nd"
#     assert test.cursor_position == (2, 1)
#     test.increment_line_ptr()
#     assert test.cursor_position == (2, 1)
#     test.increment_column_ptr()
#     assert test.cursor_position == (2, 1)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (2, 0)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (1, 4)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (1, 3)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (1, 2)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (1, 1)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (1, 0)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (0, 4)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (0, 3)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (0, 2)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (0, 1)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (0, 0)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (0, 0)
#     test.decrement_line_ptr()
#     assert test.cursor_position == (0, 0)
#     test = Text("helloworld", max_line_width=5)
#     assert test.line_count == 2
#     assert test.text == "hello\nworld"
#     test = Text("hello world", max_line_width=6)
#     assert test.line_count == 2
#     assert test.text == "hello \nworld"


# def test_multi_lined_max_widthed_positions():
#     test = Text("hello\nworld", max_line_width=5)
#     # breakpoint()
#     assert test.cursor_position == (2, 0)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (1, 4)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (1, 3)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (1, 2)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (1, 1)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (1, 0)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (0, 4)
#     test.decrement_column_ptr()
#     test.decrement_column_ptr()
#     test.decrement_column_ptr()
#     assert test.cursor_position == (0, 1)
#     test.decrement_column_ptr()
#     assert test.cursor_position == (0, 0)

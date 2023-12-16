import pytest
from adventurebox.text_line import TextLine


def test_text_line_init():
    text_line = TextLine()
    assert text_line.text == ""

    text_line = TextLine("hello")
    assert text_line.text == "hello"


def test_newline_errors():
    with pytest.raises(ValueError):
        TextLine("hello\nworld")

    test_text = TextLine("hello")
    with pytest.raises(ValueError):
        test_text.text = "hello\nworld"

    with pytest.raises(ValueError):
        test_text.insert("hello\nworld")

    with pytest.raises(ValueError):
        test_text.replace_character("helloworld", 0)

    with pytest.raises(ValueError):
        test_text.replace_character("\n", 1)


def test_dunders():
    text_line = TextLine("hello")
    assert text_line[0] == "h"
    assert text_line[1] == "e"
    assert text_line[:3] == "hel"
    assert len(text_line) == 5
    assert hash(text_line) == hash("hello")
    assert "ell" in text_line
    assert "world" not in text_line
    assert str(text_line) == "hello"
    assert repr(text_line) == "TextLine(text=hello)"
    assert text_line != "hello"
    assert text_line.text == "hello"
    assert text_line == TextLine("hello")


def test_backspace():
    text_line = TextLine("hello")
    text_line.backspace()
    assert text_line.text == "hell"
    text_line.backspace(1)
    assert text_line.text == "ell"
    with pytest.raises(ValueError):
        text_line.backspace(0)
    with pytest.raises(ValueError):
        text_line.backspace(4)
    with pytest.raises(ValueError):
        text_line.backspace(5)


def test_delete():
    text_line = TextLine("hello")
    text_line.delete(0)
    assert text_line.text == "ello"
    text_line.delete(1)
    assert text_line.text == "elo"
    text_line.delete(3)
    assert text_line.text == "elo"
    with pytest.raises(ValueError):
        text_line.delete(4)
    with pytest.raises(ValueError):
        text_line.delete(5)
    with pytest.raises(ValueError):
        text_line.delete(-1)


def test_delete_to_end():
    text_line = TextLine("hello")
    assert text_line.delete_to_end(0) == "hello"
    assert text_line.text == ""
    text_line = TextLine("hello")
    assert text_line.delete_to_end(1) == "ello"
    assert text_line.text == "h"
    text_line = TextLine("hello")
    assert text_line.delete_to_end(5) == ""
    assert text_line.text == "hello"
    with pytest.raises(ValueError):
        text_line.delete_to_end(6)
    with pytest.raises(ValueError):
        text_line.delete_to_end(7)


def test_replace_character():
    text_line = TextLine("hello")
    text_line.replace_character("a", 0)
    assert text_line.text == "aello"
    text_line.replace_character("b", 1)
    assert text_line.text == "abllo"
    text_line.replace_character("c", 5)
    assert text_line.text == "ablloc"
    with pytest.raises(ValueError):
        text_line.replace_character("dd", 7)
    with pytest.raises(ValueError):
        text_line.replace_character("d", 7)
    with pytest.raises(ValueError):
        text_line.replace_character("d", -1)
    with pytest.raises(ValueError):
        text_line.replace_character("d", 8)
    with pytest.raises(ValueError):
        text_line.replace_character("\n", 1)


def test_line_count():
    text_line = TextLine("hello")
    assert text_line.line_count(6) == 1
    text_line = TextLine("hello")
    assert text_line.line_count(5) == 1
    text_line.insert("world")
    assert text_line.line_count(5) == 2
    text_line = TextLine("1112131415")
    assert text_line.line_count(2) == 5
    assert TextLine("1112131415").line_count(None) == 1


def test_cursor_position():
    test = TextLine("hello")
    for idx in range(5):
        assert test.cursor_position(idx) == (0, idx)
    for idx in range(5):
        assert test.cursor_position(idx, 1) == (idx, 0)

    assert test.cursor_position(1, 2) == (0, 1)

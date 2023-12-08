import pytest

from .rich_text import RichText
from .line_text import LineText


def test_text_line_append():
    rt1 = RichText(text="Hello, ")
    rt2 = RichText(text="world!")
    rt3 = RichText(text="This is a test.")
    tl = LineText(rich_texts=[rt1])
    tl.append(rt2)
    tl += rt3
    assert tl.rich_texts == [rt1, rt2, rt3]


def test_text_line_prepend():
    rt1 = RichText(text="Hello, ")
    rt2 = RichText(text="world!")
    rt3 = RichText(text="This is a test.")
    tl = LineText(rich_texts=[rt1])
    tl.prepend(rt2)
    tl.prepend(rt3)
    assert tl.rich_texts == [rt3, rt2, rt1]


def test_text_line_len():
    rt1 = RichText(text="Hello, ")
    rt2 = RichText(text="world!")
    rt3 = RichText(text="This is a test.")
    tl = LineText(rich_texts=[rt1, rt2, rt3])
    assert len(tl) == 28


def test_equality():
    rt1 = RichText(text="Hello, ")
    rt2 = RichText(text="World ")
    rt3 = RichText(text="Hello, ")
    rt4 = RichText(text="World ")
    tl1 = LineText(rich_texts=[rt1, rt2])
    tl2 = LineText(rich_texts=[rt3, rt4])

    assert tl1 == tl2
    tl3 = LineText(rich_texts=[rt2, rt1])
    assert tl1 != tl3

    tl1.background_color = "blue"
    assert tl1 != tl2
    tl2.background_color = "blue"
    assert tl1 == tl2
    rt1.background_color = "red"
    assert tl1 != tl2

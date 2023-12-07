import pytest

from .rich_text import RichText
from .line_text import LineText


def test_text_line_append():
    rt1 = RichText(text="Hello, ")
    rt2 = RichText(text="world!")
    rt3 = RichText(text="This is a test.")
    tl = LineText([rt1])
    tl.append(rt2)
    tl += rt3
    assert tl.rich_text_list == [rt1, rt2, rt3]


def test_text_line_prepend():
    rt1 = RichText(text="Hello, ")
    rt2 = RichText(text="world!")
    rt3 = RichText(text="This is a test.")
    tl = LineText([rt1])
    tl.prepend(rt2)
    tl.prepend(rt3)
    assert tl.rich_text_list == [rt3, rt2, rt1]


def test_text_line_len():
    rt1 = RichText(text="Hello, ")
    rt2 = RichText(text="world!")
    rt3 = RichText(text="This is a test.")
    tl = LineText([rt1, rt2, rt3])
    assert len(tl) == 28


def test_error_richtext():
    with pytest.raises(AssertionError):
        LineText(RichText(text="Hello, "))

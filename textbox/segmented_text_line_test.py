import pytest

from textbox.text_segment import TextSegment
from textbox.segmented_text_line import SegmentedTextLine


def test_init():
    with pytest.raises(ValueError):
        SegmentedTextLine("test")

    test = SegmentedTextLine(TextSegment("test"))
    assert str(test) == "test"

    test = SegmentedTextLine([TextSegment("test"), TextSegment(" 2")])
    assert str(test) == "test 2"


def test_getitem_int_singleentry():
    test = SegmentedTextLine(TextSegment("test"))
    assert test[0] == TextSegment("t")
    assert test[1] == TextSegment("e")
    assert test[2] == TextSegment("s")
    assert test[3] == TextSegment("t")
    assert test[-1] == TextSegment("t")
    assert test[-2] == TextSegment("s")
    assert test[-3] == TextSegment("e")
    assert test[-4] == TextSegment("t")

    with pytest.raises(IndexError):
        test[4]

    with pytest.raises(IndexError):
        test[-5]


def test_getitem_slices_singleentry():
    test = SegmentedTextLine(TextSegment("test"))
    result = test[0:2]
    assert result == SegmentedTextLine(TextSegment("te"))

    result = test[1:3]
    assert result == SegmentedTextLine(TextSegment("es"))

    result = test[2:4]
    assert result == SegmentedTextLine(TextSegment("st"))

    assert test[0:5] == SegmentedTextLine(TextSegment("test"))
    assert test[5:5] == SegmentedTextLine(TextSegment())
    assert test[6:7] == SegmentedTextLine(TextSegment())


def test_getitem_int_multientry():
    test = SegmentedTextLine([TextSegment("test", color_pair=0), TextSegment(" 2", color_pair=1)])
    assert test[0] == TextSegment("t", color_pair=0)
    assert test[1] == TextSegment("e", color_pair=0)
    assert test[2] == TextSegment("s", color_pair=0)
    assert test[3] == TextSegment("t", color_pair=0)
    assert test[4] == TextSegment(" ", color_pair=1)
    assert test[5] == TextSegment("2", color_pair=1)
    assert test[-1] == TextSegment("2", color_pair=1)
    assert test[-2] == TextSegment(" ", color_pair=1)
    assert test[-3] == TextSegment("t", color_pair=0)
    assert test[-4] == TextSegment("s", color_pair=0)
    assert test[-5] == TextSegment("e", color_pair=0)
    assert test[-6] == TextSegment("t", color_pair=0)

    with pytest.raises(IndexError):
        test[6]

    with pytest.raises(IndexError):
        test[-7]


def test_getitem_slices_multientry():
    test = SegmentedTextLine([TextSegment("test"), TextSegment(" 2")])
    result = test[0:2]
    assert result == SegmentedTextLine(TextSegment("te"))

    result = test[1:3]
    assert result == SegmentedTextLine(TextSegment("es"))

    result = test[2:4]
    assert result == SegmentedTextLine(TextSegment("st"))

    result = test[3:5]
    assert result == SegmentedTextLine(TextSegment("t "))

    result = test[4:6]
    assert result == SegmentedTextLine(TextSegment(" 2"))

    assert test[0:7] == SegmentedTextLine([TextSegment("test"), TextSegment(" 2")])

    test = SegmentedTextLine([TextSegment("test", color_pair=0), TextSegment(" 2", color_pair=1)])
    result = test[0:2]
    assert result == SegmentedTextLine(TextSegment("te", color_pair=0))
    result = test[1:3]
    assert result == SegmentedTextLine(TextSegment("es", color_pair=0))
    result = test[2:4]
    assert result == SegmentedTextLine(TextSegment("st", color_pair=0))
    result = test[3:5]
    assert result == SegmentedTextLine([TextSegment("t", color_pair=0), TextSegment(" ", color_pair=1)])
    result = test[4:6]
    assert result == SegmentedTextLine([TextSegment(" 2", color_pair=1)])


def test_edge_cases_singleentry_slice():
    test = SegmentedTextLine(TextSegment("test"))
    result = test[4:]
    assert result == SegmentedTextLine()
    result = test[5:]
    assert result == SegmentedTextLine()

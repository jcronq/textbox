import pytest
from .rich_text import RichText
from .line_text import LineText
from .block_text import BlockText


def test_wrap_text():
    rt = RichText(text="Hello, world!")
    tb = BlockText(width=9)
    expected_wrapped_text = [LineText([RichText(text="Hello, ")]), LineText([RichText(text="world!")])]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_wrap_text_shortest_word_match():
    rt = RichText(text="Hello, world!")
    tb = BlockText(width=6)
    expected_wrapped_text = [LineText([RichText(text="Hello,")]), LineText([RichText(text="world!")])]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text

    rt = RichText(text="Hello  \nworld!")
    expected_wrapped_text = [LineText([RichText(text="Hello")]), LineText([RichText(text="world!")])]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_wrap_text_mid_whitespace_newline():
    rt = RichText(text="Hello \n world")
    tb = BlockText(width=6)

    result = list(tb.wrapped_text([rt]))
    expected_wrapped_text = [LineText([RichText(text="Hello")]), LineText([RichText(text=" world")])]
    assert result == expected_wrapped_text

    rt = RichText(text="Hello \n world!")
    result = list(tb.wrapped_text([rt]))
    expected_wrapped_text = [
        LineText([RichText(text="Hello")]),
        LineText([RichText(text=" ")]),
        LineText([RichText(text="world!")]),
    ]
    assert result == expected_wrapped_text


def test_mid_word_break():
    rt = RichText(text="replicate")
    tb = BlockText(width=5)
    expected_wrapped_text = [LineText([RichText(text="repli")]), LineText([RichText(text="cate")])]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_multi_mid_word_break():
    rt = RichText(text="replicate")
    tb = BlockText(width=2)
    expected_wrapped_text = [
        LineText([RichText(text="re")]),
        LineText([RichText(text="pl")]),
        LineText([RichText(text="ic")]),
        LineText([RichText(text="at")]),
        LineText([RichText(text="e")]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_multi_mid_word_break_with_space():
    rt = RichText(text="repl icate")
    tb = BlockText(width=2)
    expected_wrapped_text = [
        LineText([RichText(text="re")]),
        LineText([RichText(text="pl")]),
        LineText([RichText(text=" ")]),
        LineText([RichText(text="ic")]),
        LineText([RichText(text="at")]),
        LineText([RichText(text="e")]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_multi_mid_word_start_with_space():
    rt = RichText(text=" repl icate")
    tb = BlockText(width=2)
    expected_wrapped_text = [
        LineText([RichText(text=" ")]),
        LineText([RichText(text="re")]),
        LineText([RichText(text="pl")]),
        LineText([RichText(text=" ")]),
        LineText([RichText(text="ic")]),
        LineText([RichText(text="at")]),
        LineText([RichText(text="e")]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_multi_mid_word_start_with_space_edge_case_0():
    rt = RichText(text=" rep licate")
    tb = BlockText(width=3)
    expected_wrapped_text = [
        LineText([RichText(text=" ")]),
        LineText([RichText(text="rep")]),
        LineText([RichText(text=" ")]),
        LineText([RichText(text="lic")]),
        LineText([RichText(text="ate")]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_border():
    text_width = 5
    border_width = 1
    padding_width = 1

    rt = RichText(text="Hello")
    tb = BlockText(
        width=text_width,
        border_thickness=border_width,
        padding_thickness=padding_width,
        border_color="red",
        padding_color="white",
        border_char="*",
        padding_char=" ",
    )
    border = [RichText(text="*", color="red"), RichText(text="*", color="red")]
    open_padding = [RichText(text="*", color="red"), RichText(text=" ", color="white")]
    close_padding = open_padding[::-1]
    expected = [
        LineText([*border, RichText(text="*****", color="red"), *border]),
        LineText([*open_padding, RichText(text="     ", color="white"), *close_padding]),
        LineText([*open_padding, RichText(text="Hello"), *close_padding]),
        LineText([*open_padding, RichText(text="     ", color="white"), *close_padding]),
        LineText([*border, RichText(text="*****", color="red"), *border]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected
    for line in result:
        assert len(line) == text_width + border_width * 2 + padding_width * 2


def test_even_line_width_case():
    text_width = 40
    border_width = 1
    padding_width = 1
    text_str = "I cannot provide a specific time without additional context. Time varies depending on the location and the context, such as whether it is daytime or nighttime, whether it is standard time or daylight saving time, etc. Could you please provide more information so I can provide an accurate answer?"
    rt = RichText(text=text_str)
    tb = BlockText(
        width=text_width,
        border_thickness=border_width,
        padding_thickness=padding_width,
        border_color="red",
        padding_color="white",
        border_char="*",
        padding_char=" ",
    )
    expected = [
        LineText([RichText(text="I cannot provide a specific time without")]),
        LineText([RichText(text="additional context. Time varies ")]),
        LineText([RichText(text="depending on the location and the ")]),
        LineText([RichText(text="context, such as whether it is daytime ")]),
        LineText([RichText(text="or nighttime, whether it is standard ")]),
        LineText([RichText(text="time or daylight saving time, etc. Could")]),
        LineText([RichText(text="you please provide more information so I")]),
        LineText([RichText(text="can provide an accurate answer?")]),
    ]
    result = list(tb.wrapped_text([rt]))

    for line in result:
        assert len(line) == text_width + border_width * 2 + padding_width * 2

    for idx, line in enumerate(result[2:-2]):
        text_of_interest = line.rich_text_list[2]
        assert text_of_interest == expected[idx].rich_text_list[0]

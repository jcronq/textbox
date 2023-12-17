import pytest
from .rich_text import RichText
from .line_text import LineText
from .block_text import BlockText


def test_wrap_text():
    rt = RichText(text="Hello, world!")
    tb = BlockText(width=9)
    expected_wrapped_text = [
        LineText(rich_texts=[RichText(text="Hello, ")]),
        LineText(rich_texts=[RichText(text="world!")]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_wrap_text_shortest_word_match():
    rt = RichText(text="Hello, world!")
    tb = BlockText(width=6)
    expected_wrapped_text = [
        LineText(rich_texts=[RichText(text="Hello,")]),
        LineText(rich_texts=[RichText(text="world!")]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text

    rt = RichText(text="Hello  \nworld!")
    expected_wrapped_text = [
        LineText(rich_texts=[RichText(text="Hello")]),
        LineText(rich_texts=[RichText(text="world!")]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_wrap_text_mid_whitespace_newline():
    rt = RichText(text="Hello \n world")
    tb = BlockText(width=6)

    result = list(tb.wrapped_text([rt]))
    expected_wrapped_text = [
        LineText(rich_texts=[RichText(text="Hello")]),
        LineText(rich_texts=[RichText(text=" world")]),
    ]
    assert result == expected_wrapped_text

    rt = RichText(text="Hello \n world!")
    result = list(tb.wrapped_text([rt]))
    expected_wrapped_text = [
        LineText(rich_texts=[RichText(text="Hello")]),
        LineText(rich_texts=[RichText(text=" ")]),
        LineText(rich_texts=[RichText(text="world!")]),
    ]
    assert result == expected_wrapped_text


def test_mid_word_break():
    rt = RichText(text="replicate")
    tb = BlockText(width=5)
    expected_wrapped_text = [
        LineText(rich_texts=[RichText(text="repli")]),
        LineText(rich_texts=[RichText(text="cate")]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_multi_mid_word_break():
    rt = RichText(text="replicate")
    tb = BlockText(width=2)
    expected_wrapped_text = [
        LineText(rich_texts=[RichText(text="re")]),
        LineText(rich_texts=[RichText(text="pl")]),
        LineText(rich_texts=[RichText(text="ic")]),
        LineText(rich_texts=[RichText(text="at")]),
        LineText(rich_texts=[RichText(text="e")]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_multi_mid_word_break_with_space():
    rt = RichText(text="repl icate")
    tb = BlockText(width=2)
    expected_wrapped_text = [
        LineText(rich_texts=[RichText(text="re")]),
        LineText(rich_texts=[RichText(text="pl")]),
        LineText(rich_texts=[RichText(text=" ")]),
        LineText(rich_texts=[RichText(text="ic")]),
        LineText(rich_texts=[RichText(text="at")]),
        LineText(rich_texts=[RichText(text="e")]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_multi_mid_word_start_with_space():
    rt = RichText(text=" repl icate")
    tb = BlockText(width=2)
    expected_wrapped_text = [
        LineText(rich_texts=[RichText(text=" ")]),
        LineText(rich_texts=[RichText(text="re")]),
        LineText(rich_texts=[RichText(text="pl")]),
        LineText(rich_texts=[RichText(text=" ")]),
        LineText(rich_texts=[RichText(text="ic")]),
        LineText(rich_texts=[RichText(text="at")]),
        LineText(rich_texts=[RichText(text="e")]),
    ]
    result = list(tb.wrapped_text([rt]))
    assert result == expected_wrapped_text


def test_multi_mid_word_start_with_space_edge_case_0():
    rt = RichText(text=" rep licate")
    tb = BlockText(width=3)
    expected_wrapped_text = [
        LineText(rich_texts=[RichText(text=" ")]),
        LineText(rich_texts=[RichText(text="rep")]),
        LineText(rich_texts=[RichText(text=" ")]),
        LineText(rich_texts=[RichText(text="lic")]),
        LineText(rich_texts=[RichText(text="ate")]),
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
        border_color="red",
        border_char="*",
        padding_char=" ",
    )
    tb.border_width = border_width
    tb.padding_width = padding_width
    border = [RichText(text="*", foreground_color="red"), RichText(text="*", foreground_color="red")]
    open_padding = [RichText(text="*", foreground_color="red"), RichText(text=" ")]
    close_padding = open_padding[::-1]
    expected = [
        LineText(rich_texts=[*border, RichText(text="*****", foreground_color="red"), *border]),
        LineText(rich_texts=[*open_padding, RichText(text="     "), *close_padding]),
        LineText(rich_texts=[*open_padding, RichText(text="Hello"), *close_padding]),
        LineText(rich_texts=[*open_padding, RichText(text="     "), *close_padding]),
        LineText(rich_texts=[*border, RichText(text="*****", foreground_color="red"), *border]),
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
        border_color="red",
        background_color="white",
        border_char="*",
        padding_char=" ",
    )
    tb.border_width = border_width
    tb.padding_width = padding_width
    expected = [
        LineText(rich_texts=[RichText(text="I cannot provide a specific time without")]),
        LineText(rich_texts=[RichText(text="additional context. Time varies ")]),
        LineText(rich_texts=[RichText(text="depending on the location and the ")]),
        LineText(rich_texts=[RichText(text="context, such as whether it is daytime ")]),
        LineText(rich_texts=[RichText(text="or nighttime, whether it is standard ")]),
        LineText(rich_texts=[RichText(text="time or daylight saving time, etc. Could")]),
        LineText(rich_texts=[RichText(text="you please provide more information so I")]),
        LineText(rich_texts=[RichText(text="can provide an accurate answer?")]),
    ]
    result = list(tb.wrapped_text([rt]))

    for line in result:
        assert len(line) == text_width + border_width * 2 + padding_width * 2

    for idx, line in enumerate(result[2:-2]):
        text_of_interest = line.rich_texts[2]
        assert text_of_interest == expected[idx].rich_texts[0]

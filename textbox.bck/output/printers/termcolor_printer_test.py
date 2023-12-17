from .termcolor_printer import TermcolorPrinter
from textbox.output.rich_text import RichText


def test_print_rich_text():
    rt = RichText(text="Hello, world!")
    expected_output = "Hello, world!"
    result = TermcolorPrinter.sprint(rt)
    assert result == expected_output

    rt.background_color = "red"
    expected_output = "\x1b[41mHello, world!\x1b[0m"
    result = TermcolorPrinter.sprint(rt)
    assert result == expected_output


def test_print_rich_text_with_color():
    rt = RichText(text="Hello, world!", foreground_color="red")
    expected_output = "\x1b[31mHello, world!\x1b[0m"
    result = TermcolorPrinter.sprint(rt)
    assert result == expected_output

    rt = RichText(text="Hello, world!", foreground_color="red", background_color="blue")
    expected_symbols = ["\x1b[31m", "\x1b[44m", "Hello, world!", "\x1b[0m"]
    result = TermcolorPrinter.sprint(rt)
    for symbol in expected_symbols:
        assert symbol in result

    rt = RichText(text="Hello, world!", foreground_color="red", background_color="blue", bold=True)
    expected_symbols += ["\x1b[1m"]
    result = TermcolorPrinter.sprint(rt)
    for symbol in expected_symbols:
        assert symbol in result

    rt = RichText(text="Hello, world!", foreground_color="red", background_color="blue", bold=True, underline=True)
    expected_symbols += ["\x1b[4m"]
    result = TermcolorPrinter.sprint(rt)
    for symbol in expected_symbols:
        assert symbol in result

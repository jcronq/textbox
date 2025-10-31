from textbox.color_code import ColorCode
from textbox.text_segment import TextSegment


def dark_blue(text: str):
    if not isinstance(text, str):
        raise TypeError(f"dark_blue() takes a string, not a {type(text)}")
    return TextSegment(text, ColorCode.DARK_BLUE)


def light_blue(text: str):
    if not isinstance(text, str):
        raise TypeError(f"light_blue() takes a string, not a {type(text)}")
    return TextSegment(text, ColorCode.LIGHT_BLUE)


def dark_purple(text: str):
    if not isinstance(text, str):
        raise TypeError(f"dark_purple() takes a string, not a {type(text)}")
    return TextSegment(text, ColorCode.DARK_PURPLE)


def light_purple(text: str):
    if not isinstance(text, str):
        raise TypeError(f"light_purple() takes a string, not a {type(text)}")
    return TextSegment(text, ColorCode.LIGHT_PURPLE)

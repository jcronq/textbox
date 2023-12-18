from typing import Union, List
from textbox.color_code import ColorCode


class TextSegment:
    def __init__(self, text: str = None, color_pair: int = ColorCode.DEFAULT):
        if text is None:
            self._text = ""
        else:
            self._text = text
        self.color_pair = color_pair

    def copy(self):
        return TextSegment(self._text, self.color_pair)

    def isalnum(self):
        return self._text.isalnum()

    def split(self, split_str: str):
        return [TextSegment(split_i, self.color_pair) for split_i in self._text.split(split_str)]

    def __len__(self):
        return len(self._text)

    def __repr__(self):
        return f"TextSegment(text={self._text}, color_pair={self.color_pair})"

    def __str__(self):
        return self._text

    def __getitem__(self, item: Union[int, slice]):
        return TextSegment(self._text[item], self.color_pair)

    def __add__(self, other: Union[str, "TextSegment"]):
        if isinstance(other, str):
            return TextSegment(self._text + other, self.color_pair)
        elif isinstance(other, TextSegment):
            if self.color_pair != other.color_pair:
                raise ValueError("Cannot add TextSegments with different color pairs")
            return TextSegment(self._text + other._text, self.color_pair)
        else:
            raise TypeError(f"Cannot add {type(other)} to TextSegment")

    def __eq__(self, other: "TextSegment"):
        if isinstance(other, TextSegment):
            return self._text == other._text and self.color_pair == other.color_pair
        else:
            return False

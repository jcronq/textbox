from typing import List
from dataclasses import dataclass

from .rich_text import RichText
from . import Printable


@dataclass
class LineText(Printable):
    rich_texts: List[RichText] = None

    @property
    def rich_text_list(self):
        for rich_text in self.rich_texts:
            if rich_text.background_color is None:
                rich_text.background_color = self.background_color
            if rich_text.foreground_color is None:
                rich_text.foreground_color = self.foreground_color
            yield rich_text

    def __len__(self):
        return sum([len(rich_text) for rich_text in self.text])

    def append(self, rich_text: RichText):
        self.rich_text_list.append(rich_text)

    def prepend(self, rich_text: RichText):
        self.rich_text_list = [rich_text, *self.rich_text_list]

    def count(self):
        return len(self.rich_text_list)

    def __len__(self):
        return sum([len(rich_text) for rich_text in self.rich_text_list])

    def __add__(self, other: RichText):
        if isinstance(other, RichText):
            self.rich_text_list.append(other)
        else:
            raise TypeError(f"Cannot add {type(other)} to TextLine")
        return self

    def __repr__(self):
        return f"TextLine([{','.join([rich_text.__repr__() for rich_text in self.rich_text_list])}])"

    def __str__(self):
        return "".join([f'"{rich_text}"' for rich_text in self.rich_text_list])

    def __eq__(self, other: "LineText"):
        if isinstance(other, LineText):
            return self.rich_text_list == other.rich_text_list
        else:
            return False

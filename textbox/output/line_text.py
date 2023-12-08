from typing import List
from dataclasses import dataclass, field

from .rich_text import RichText
from . import Printable


@dataclass
class LineText(Printable):
    rich_texts: List[RichText] = field(default_factory=list)

    @property
    def rich_text_list(self):
        for rich_text in self.rich_texts:
            tmp_text = rich_text.clone()
            if tmp_text.background_color is None:
                tmp_text.background_color = self.background_color
            if tmp_text.foreground_color is None:
                tmp_text.foreground_color = self.foreground_color
            yield tmp_text

    def __len__(self):
        return sum([len(rich_text) for rich_text in self.text])

    def append(self, rich_text: RichText):
        self.rich_texts.append(rich_text)

    def prepend(self, rich_text: RichText):
        self.rich_texts = [rich_text, *self.rich_texts]

    def count(self):
        return len(self.rich_texts)

    def __len__(self):
        return sum([len(rich_text) for rich_text in self.rich_texts])

    def __add__(self, other: RichText):
        if isinstance(other, RichText):
            self.rich_texts.append(other)
        else:
            raise TypeError(f"Cannot add {type(other)} to TextLine")
        return self

    def __repr__(self):
        options = ", ".join([f"{key}={value}" for key, value in self.__dict__.items() if value is not None])
        return f"LineText({options})"

    def __str__(self):
        return ", ".join([f'"{rich_text}"' for rich_text in self.rich_texts])

    def __eq__(self, other: "LineText"):
        if isinstance(other, LineText):
            return self.rich_texts == other.rich_texts and super().__eq__(other)
        else:
            return False

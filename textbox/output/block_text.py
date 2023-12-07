from typing import List
from dataclasses import dataclass


from .line_text import LineText
from .rich_text import RichText
from . import Printable


@dataclass
class BlockText(Printable):
    width: int = 80

    border_color: str = None
    background_color: str = None

    padding_char: str = " "
    padding_top: int = 0
    padding_left: int = 0
    padding_right: int = 0
    padding_bottom: int = 0

    border_char: str = "*"
    border_top: int = 0
    border_left: int = 0
    border_right: int = 0
    border_bottom: int = 0

    def __len__(self):
        return sum([len(rich_text) for rich_text in self.text])

    def format_text_line(self, line: LineText, pad_with_border=False):
        if pad_with_border:
            padding = self.border_char
            background_color = self.border_color
        else:
            padding = self.padding_char
            background_color = self.background_color
        if self.border_thickness > 0:
            line.prepend(RichText(text=padding * self.padding_thickness, color=background_color))
            if len(line) <= self.width:
                rich_text = line.rich_text_list[-1].clone_settings()
                rich_text.append(" " * (self.width - len(line) + 1))
                line.append(rich_text)
            line.append(RichText(text=padding * self.padding_thickness, color=background_color))
        if self.border_thickness > 0:
            line.prepend(RichText(text=self.border_char * self.border_thickness, color=self.border_color))
            line.append(RichText(text=self.border_char * self.border_thickness, color=self.border_color))
        return line

    @property
    def horizontal_border(self):
        text = RichText(text=self.border_char * self.width, color=self.border_color)
        text_line = LineText([text])
        border = self.format_text_line(text_line, pad_with_border=True)
        return border

    @property
    def horizontal_padding(self):
        text = RichText(text=self.padding_char * self.width, color=self.background_color)
        text_line = LineText([text])
        padding = self.format_text_line(text_line)
        return padding

    def wrapped_text(self, rich_text_list: List[RichText]):
        if self.border_thickness > 0:
            yield self.horizontal_border
        if self.padding_thickness > 0:
            yield self.horizontal_padding
        cur_line = LineText([])
        for rich_text in rich_text_list:
            new_rich_text = rich_text.clone_settings()
            for word in rich_text.words():
                if len(cur_line) + len(new_rich_text) + len(word) > self.width:
                    if len(new_rich_text) > 0:
                        cur_line += new_rich_text
                        yield self.format_text_line(cur_line)
                    if len(word) >= self.width:  # If the word is longer than the width
                        # Split up the word into multiple lines
                        new_rich_text = rich_text.clone_settings()
                        for i in range(0, len(word), self.width):
                            new_rich_text += word[i : i + self.width]
                            if len(new_rich_text) == self.width:
                                cur_line = LineText([new_rich_text])
                                yield self.format_text_line(cur_line)
                                cur_line = LineText([])
                                new_rich_text = rich_text.clone_settings()
                    else:
                        new_rich_text = rich_text.clone_settings()
                        if not RichText.is_whitespace(word):
                            new_rich_text += word
                        cur_line = LineText([])
                elif RichText.is_whitespace(word) and any([char == "\n" for char in word]):
                    cur_line += new_rich_text
                    yield self.format_text_line(cur_line)
                    new_rich_text = rich_text.clone_settings()
                    cur_line = LineText([])
                else:
                    new_rich_text += word
            cur_line += new_rich_text
        if len(cur_line) > 0:
            yield self.format_text_line(cur_line)

        if self.padding_thickness > 0:
            yield self.horizontal_padding
        if self.border_thickness > 0:
            yield self.horizontal_border

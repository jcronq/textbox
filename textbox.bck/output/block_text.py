from typing import List
from dataclasses import dataclass


from .line_text import LineText
from .rich_text import RichText
from . import Printable


@dataclass
class BlockText(Printable):
    width: int = 80

    border_color: str = None

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

    @property
    def padding_width(self):
        if self.padding_left == self.padding_right == self.padding_top == self.padding_bottom:
            return self.padding_left
        else:
            return None

    @padding_width.setter
    def padding_width(self, value):
        self.padding_left = value
        self.padding_right = value
        self.padding_top = value
        self.padding_bottom = value

    @property
    def border_width(self):
        if self.border_left == self.border_right == self.border_top == self.border_bottom:
            return self.border_left
        else:
            return None

    @border_width.setter
    def border_width(self, value):
        self.border_left = value
        self.border_right = value
        self.border_top = value
        self.border_bottom = value

    def add_border_to_line(self, line: LineText, pad_with_border=False):
        # The top and bottom line of the border should be made entirely out of border characters
        if pad_with_border:
            padding = self.border_char
            padding_color = self.border_color
        else:
            padding = self.padding_char
            padding_color = None

        left_padding = RichText(text=padding * self.padding_left)
        right_padding = RichText(text=padding * self.padding_right)
        left_border = RichText(text=self.border_char * self.border_left)
        right_border = RichText(text=self.border_char * self.border_right)
        if self.border_color is not None:
            left_border.foreground_color = self.border_color
            right_border.foreground_color = self.border_color
        if padding_color is not None:
            left_padding.foreground_color = padding_color
            right_padding.foreground_color = padding_color

        # Add the padding to the left of the line
        if self.padding_left > 0:
            line.prepend(left_padding)

        # Add the padding to the right of the line
        if self.padding_right > 0:
            # Fill the rest of the line with padding
            if len(line) <= self.width:
                rich_text = line.rich_texts[-1].clone_settings()
                rich_text.append(" " * (self.width - len(line) + 1))
                line.append(rich_text)
            # Add the padding to the padding_right thickness
            line.append(right_padding)

        # Add the border to the left of the line
        if self.border_left > 0:
            line.prepend(left_border)

        # Add the border to the right of the line
        if self.border_right > 0:
            line.append(right_border)

        return line

    @property
    def horizontal_border(self):
        text = RichText(text=self.border_char * self.width, foreground_color=self.border_color)
        text_line = LineText(rich_texts=[text])
        border = self.add_border_to_line(text_line, pad_with_border=True)
        return border

    @property
    def horizontal_padding(self):
        text = RichText(text=self.padding_char * self.width, foreground_color=self.background_color)
        text_line = LineText(rich_texts=[text])
        padding = self.add_border_to_line(text_line)
        return padding

    def wrapped_text(self, rich_text_list: List[RichText]):
        if self.border_top > 0:
            yield self.horizontal_border
        if self.padding_top > 0:
            yield self.horizontal_padding
        cur_line = LineText(rich_texts=[])
        for rich_text in rich_text_list:
            new_rich_text = rich_text.clone_settings()
            for word in rich_text.words():
                if len(cur_line) + len(new_rich_text) + len(word) > self.width:
                    if len(new_rich_text) > 0:
                        cur_line += new_rich_text
                        yield self.add_border_to_line(cur_line)
                    if len(word) >= self.width:  # If the word is longer than the width
                        # Split up the word into multiple lines
                        new_rich_text = rich_text.clone_settings()
                        for i in range(0, len(word), self.width):
                            new_rich_text += word[i : i + self.width]
                            if len(new_rich_text) == self.width:
                                cur_line = LineText(rich_texts=[new_rich_text])
                                yield self.add_border_to_line(cur_line)
                                cur_line = LineText(rich_texts=[])
                                new_rich_text = rich_text.clone_settings()
                    else:
                        new_rich_text = rich_text.clone_settings()
                        if not RichText.is_whitespace(word):
                            new_rich_text += word
                        cur_line = LineText(rich_texts=[])
                elif RichText.is_whitespace(word) and any([char == "\n" for char in word]):
                    cur_line += new_rich_text
                    yield self.add_border_to_line(cur_line)
                    new_rich_text = rich_text.clone_settings()
                    cur_line = LineText(rich_texts=[])
                else:
                    new_rich_text += word
            cur_line += new_rich_text
        if len(cur_line) > 0:
            yield self.add_border_to_line(cur_line)

        if self.padding_bottom > 0:
            yield self.horizontal_padding
        if self.border_bottom > 0:
            yield self.horizontal_border

    def __repr__(self):
        options = ", ".join([f"{key}={value}" for key, value in self.__dict__.items() if value is not None])
        return f"BlockText({options})"

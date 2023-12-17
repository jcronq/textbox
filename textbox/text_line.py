from typing import Union, Optional, List
from textbox.box_types import Position
from textbox.text_segment import TextSegment
from textbox.segmented_text_line import SegmentedTextLine


class TextLine:
    def __init__(self, text: Union[str, TextSegment, SegmentedTextLine] = ""):
        """A single line of text"""
        self._text: SegmentedTextLine = None
        self.text = text

    def start_of_next_word(self, column_ptr: int, in_white_space: bool) -> Optional[int]:
        if column_ptr is None:
            column_ptr = 0
        for idx in range(column_ptr, len(self.text)):
            if not self.text[idx].isalnum():
                in_white_space = True
            elif in_white_space and self.text[idx].isalnum():
                return idx
        return None

    def start_of_previous_word(self, column_ptr: int):
        in_character_space = False
        if column_ptr is None:
            column_ptr = len(self.text) - 1
        for idx in range(column_ptr - 1, -1, -1):
            if in_character_space and not self.text[idx].isalnum():
                return idx + 1
            elif self.text[idx].isalnum():
                in_character_space = True
        if in_character_space:
            return 0
        return None

    def copy(self):
        return TextLine(self.text)

    def cursor_position(self, column_ptr: int, width: int = None):
        if width is None:
            return Position(0, column_ptr)
        effective_lineno = column_ptr // width
        effective_columnno = column_ptr % width
        return Position(effective_lineno, effective_columnno)

    def line_count(self, width: int):
        """Get the number of lines this TextLine would take up if printed with width"""
        if width is None:
            return 1
        if len(self.text) == 0:
            return 1
        if len(self.text) % width == 0:
            return len(self.text) // width
        return len(self.text) // width + 1

    @property
    def text(self) -> str:
        """Get the text of the TextLine"""
        return str(self._text)

    @text.setter
    def text(self, value: Union[str, TextSegment, List[TextSegment], SegmentedTextLine]):
        """Set the text of the TextLine"""
        if "\n" in value:
            raise ValueError("TextLine cannot contain newlines")

        if isinstance(value, str):
            self._text = SegmentedTextLine(TextSegment(value))
        elif isinstance(value, list):
            if not all([isinstance(segment, TextSegment) for segment in value]):
                raise ValueError(
                    "SegmentedTextLine must be initialized with a list of TextSegments, str, or SegmentedTextLine"
                )
            self._text = SegmentedTextLine(value)
        elif isinstance(value, TextSegment):
            self._text = SegmentedTextLine(value)
        elif isinstance(value, SegmentedTextLine):
            self._text = value
        else:
            raise ValueError("TextLine must be initialized with a string or TextSegment")

    def split_on_width(self, width: int):
        """Split the TextLine into TextLines of width"""
        for idx in range(len(self.text) // width + 1):
            sub_line = TextLine(self._text[idx * width : (idx + 1) * width])
            if len(sub_line) > 0:
                yield sub_line

    def replace_character(self, ch: str, column_ptr: int):
        """Replace the character at column_ptr with ch"""
        if len(ch) != 1:
            raise ValueError("Cannot replace character with string of length != 1")
        if ch == "\n":
            raise ValueError("Cannot replace character with newline")

        if column_ptr < 0:
            raise ValueError("Cannot replace character before the beginning of a line")
        if column_ptr > len(self._text):
            raise ValueError("Cannot replace character past the end of a line")

        if column_ptr == len(self._text):
            self._text = self._text + ch
        self._text = (
            self._text[:column_ptr] + TextSegment(ch, self._text[column_ptr].color_pair) + self._text[column_ptr + 1 :]
        )

    def delete_to_end(self, column_ptr: int) -> str:
        """Delete from column_ptr to the end of the line, returning the deleted text"""
        if column_ptr > len(self._text):
            raise ValueError("Cannot delete past the end of a line")

        remainder = self._text[column_ptr:]
        self._text = self._text[:column_ptr]
        return remainder

    def delete(self, column_ptr: int):
        """Delete the character at column_ptr"""
        if column_ptr < 0:
            raise ValueError("Cannot delete before the beginning of a line")
        if column_ptr > len(self._text):
            raise ValueError("Cannot delete past the end of a line")

        self._text = self._text[:column_ptr] + self._text[column_ptr + 1 :]

    def insert(self, other: str, cursor_ptr: int = None):
        """Insert other at cursor_ptr"""
        if "\n" in other:
            raise ValueError("TextLine cannot contain newlines")

        if cursor_ptr is None:
            cursor_ptr = len(self._text)

        if cursor_ptr < 0:
            raise ValueError("Cannot insert before the beginning of a line")
        if cursor_ptr > len(self._text):
            raise ValueError("Cannot insert past the end of a line")

        if cursor_ptr == len(self._text):
            self._text = self._text + other
        else:
            self._text = self._text[:cursor_ptr] + other + self._text[cursor_ptr:]

    def backspace(self, column_ptr: int = None):
        """Delete the character before column_ptr"""
        if len(self._text) == 0:
            raise ValueError("Cannot backspace an empty line")

        if column_ptr is None:
            column_ptr = len(self._text)

        if column_ptr == 0:
            raise ValueError("Cannot backspace at the beginning of a line")

        if column_ptr > len(self._text):
            raise ValueError("Cannot backspace past the end of a line")

        self._text = self._text[: column_ptr - 1] + self._text[column_ptr:]

    def __getitem__(self, item: Union[int, slice]):
        """Get the character at item"""
        return self._text[item]

    def __len__(self) -> int:
        return len(self.text)

    def __hash__(self) -> int:
        return hash(self.text)

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"TextLine(text={self.text})"

    def __contains__(self, item: str):
        return item in self.text

    def __eq__(self, other: "TextLine") -> bool:
        if isinstance(other, TextLine):
            return self.text == other.text
        return False

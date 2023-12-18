from typing import List, Union
from textbox.text_line import TextLine
from textbox.box_types import Position
from textbox.text_segment import TextSegment
from textbox.segmented_text_line import SegmentedTextLine
import logging


logger = logging.getLogger()


class Text:
    def __init__(self, text: str = "", max_line_width: int = None):
        self._text_lines: List[TextLine] = []
        self._line_ptr = 0
        self._column_ptr = 0
        self._max_line_width = max_line_width
        self._edit_mode = False

        self.text = text

    def copy(self):
        new_text = Text()
        new_text.max_line_width = self.max_line_width
        for line in self._text_lines:
            new_text._text_lines.append(line.copy())
        new_text.to_end_of_text()
        return new_text

    @property
    def edit_mode(self):
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, new_edit_mode: bool):
        previous_edit_mode = self._edit_mode
        self._edit_mode = new_edit_mode
        # If turning off edit mode, and we were past the length of the current line (only possible in edit mode),
        # move cursor to end of line (ie. back one space.)
        if not new_edit_mode and previous_edit_mode and self.column_ptr >= len(self.current_line):
            self.to_end_of_line()

    @property
    def column_ptr(self):
        return self._column_ptr

    @property
    def line_ptr(self):
        return self._line_ptr

    @property
    def max_line_width(self):
        return self._max_line_width

    @max_line_width.setter
    def max_line_width(self, value: int):
        self._max_line_width = value

    @property
    def cursor_position(self):
        if self._max_line_width is None:
            return Position(self._line_ptr, self.column_ptr)
        else:
            line_offset = 0
            for idx in range(self._line_ptr):
                line_offset += self._text_lines[idx].line_count(self._max_line_width)
            offset_position = Position(line_offset, 0)
            line_position = self.current_line.cursor_position(self.column_ptr, self._max_line_width)

            return offset_position + line_position

    @property
    def lines(self) -> List[TextLine]:
        if self._max_line_width is None:
            return [str(text_line) for text_line in self._text_lines]
        lines = []
        for text_line in self._text_lines:
            if len(text_line) >= self._max_line_width:
                for sub_line in text_line.split_on_width(self._max_line_width):
                    lines.append(sub_line)
            else:
                lines.append(text_line)
        return lines

    @property
    def text(self):
        return "\n".join((str(text_line) for text_line in self.lines))

    @text.setter
    def text(self, text: Union[str, List[str], List[TextLine], List[SegmentedTextLine], List[TextSegment]]):
        """Set the text of the textbox."""
        if isinstance(text, str):
            if text == "":
                return
            text = [TextLine(line) for line in text.split("\n")]
        elif isinstance(text, list):
            if all((isinstance(line, str) for line in text)):
                text = [TextLine(line) for line in text]
            elif all((isinstance(line, TextLine) for line in text)):
                text = text
            elif all((isinstance(line, SegmentedTextLine) for line in text)):
                text = [TextLine(line) for line in text]
            elif all((isinstance(line, TextSegment) for line in text)):
                raise NotImplementedError("TextSegments not yet supported")
                # text = [TextLine(line) for line in text]
            else:
                raise ValueError(
                    "Text must be a string or a list of strings or a list of TextLines or a list of SegmentedTextLines or a list of TextSegments"
                )
        else:
            raise ValueError(
                "Text must be a string or a list of strings or a list of TextLines or a list of SegmentedTextLines or a list of TextSegments"
            )
        self.erase()
        self._text_lines = text
        self.to_last_line()
        self.to_end_of_line()

    def set_text_to_str(self, text: str):
        """Set the text of the textbox.  Default string formatting."""
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        self.text = text

    @property
    def current_line(self):
        if len(self._text_lines) == 0:
            return TextLine("")
        return self._text_lines[self._line_ptr]

    @property
    def previous_line(self):
        if self._line_ptr == 0:
            return None
        return self._text_lines[self._line_ptr - 1]

    @property
    def next_line(self):
        if self._line_ptr >= len(self._text_lines):
            return None
        return self._text_lines[self._line_ptr + 1]

    @property
    def last_column_on_line(self):
        return max(len(self.current_line) - (0 if self._edit_mode else 1), 0)

    @property
    def last_line_in_text(self):
        return len(self._text_lines) - 1

    def increment_line_ptr(self):
        if self._line_ptr >= self.last_line_in_text:
            return
        self._line_ptr += 1
        if self.column_ptr >= len(self.current_line):
            self.to_end_of_line()

    def decrement_line_ptr(self):
        if self._line_ptr <= 0:
            return
        self._line_ptr -= 1
        if self.column_ptr >= len(self.current_line):
            self.to_end_of_line()

    def increment_column_ptr(self):
        if self.column_ptr >= self.last_column_on_line:
            if self._line_ptr >= self.last_line_in_text:
                return
            self._line_ptr += 1
            self.to_start_of_line()
        else:
            self._column_ptr += 1

    def decrement_column_ptr(self):
        if self.column_ptr <= 0:
            if self._line_ptr <= 0:
                return
            self._line_ptr -= 1
            self.to_end_of_line()
        else:
            self._column_ptr = max(0, self._column_ptr - 1)

    def to_end_of_line(self):
        self._column_ptr = self.last_column_on_line

    def to_start_of_line(self):
        self._column_ptr = 0

    def to_end_of_text(self):
        self.to_last_line()
        self.to_end_of_line()

    def to_start_of_text(self):
        self.to_first_line()
        self.to_start_of_line()

    def goto(self, position: Position):
        self._line_ptr = position.lineno
        self._column_ptr = position.colno

    def start_of_next_word(self):
        start_search_col = self.column_ptr
        in_whitespace = False
        for idx in range(self.line_ptr, len(self._text_lines)):
            next_word_ptr = self._text_lines[idx].start_of_next_word(start_search_col, in_whitespace)
            in_whitespace = True
            start_search_col = None
            if next_word_ptr is not None:
                return Position(idx, next_word_ptr)
        return None

    def start_of_previous_word(self):
        start_search_col = self.column_ptr
        for idx in range(self.line_ptr, -1, -1):
            next_word_ptr = self._text_lines[idx].start_of_previous_word(start_search_col)
            start_search_col = None
            if next_word_ptr is not None:
                return Position(idx, next_word_ptr)
        return None

    def delete_line(self):
        if len(self._text_lines) == 0:
            return

        self._text_lines.pop(self._line_ptr)
        if self._line_ptr > 0 and self._line_ptr >= len(self._text_lines):
            self.decrement_line_ptr()
        elif self.column_ptr > len(self.current_line):
            self.to_end_of_line()

    def backspace(self):
        """Delete the character before the cursor."""

        # If we're at the beginning of a line, delete the line.
        if self.column_ptr == 0:
            # If we're at the beginning of the first line, do nothing.
            if self._line_ptr == 0:
                return

            # If the current line is not empty, append it to the previous line.
            elif len(self.current_line) > 0:
                self.decrement_line_ptr()
                self.to_end_of_line()
                self.current_line.insert(self.next_line.rich_text)
                self._text_lines.pop(self._line_ptr + 1)
                # Correct positioning is end of preioous line + 1
                # We get that for free in edit mode. Need to set manually otherwise.
                if not self.edit_mode:
                    self.increment_column_ptr()

            # Otherwise, delete the empty line.
            else:
                self._text_lines.pop(self._line_ptr)
                self._line_ptr -= 1
                self.to_end_of_line()

        # Otherwise, delete the character before the cursor on the same line.
        else:
            self.current_line.backspace(self.column_ptr)
            self.decrement_column_ptr()

    @property
    def line_count(self):
        return sum((line.line_count(self._max_line_width) for line in self._text_lines))

    def break_line(self):
        line_remainder = self.current_line.delete_to_end(self.column_ptr)
        self._text_lines.insert(self._line_ptr + 1, TextLine(line_remainder))
        self._line_ptr += 1
        self.to_start_of_line()

    def replace_character(self, ch: str):
        if len(ch) != 1:
            raise ValueError("Cannot replace character with string of length != 1")
        if self.column_ptr < 0:
            raise ValueError("Cannot replace character before the beginning of a line")
        if self.column_ptr > len(self.current_line):
            raise ValueError("Cannot replace character past the end of a line")

        if ch == "\n":
            self.break_line()
            if len(self.current_line) > 0:
                self.increment_column_ptr()
                self.backspace()
        else:
            self.current_line.replace_character(ch, self.column_ptr)
            self.increment_column_ptr()

    def insert_newline(self):
        if self.column_ptr == 0:
            self._text_lines.insert(self._line_ptr, TextLine())
            self._line_ptr += 1
        elif self.column_ptr >= len(self.current_line):
            self._text_lines.insert(self._line_ptr + 1, TextLine())
            self._line_ptr += 1
        else:
            self.break_line()
        self.to_start_of_line()

    def insert(self, text: str):
        if len(self._text_lines) == 0:
            self._text_lines.append(TextLine())

        if not self._edit_mode:
            raise RuntimeError("Cannot insert text when not in edit mode")

        for ch in text:
            if ch == "\n":
                self.insert_newline()
            else:
                self.current_line.insert(ch, self.column_ptr)
                self.increment_column_ptr()

    def erase(self):
        self._text_lines = []
        self.to_first_line()
        self.to_start_of_line()

    def to_first_line(self):
        self._line_ptr = 0

    def to_last_line(self):
        self._line_ptr = max(len(self._text_lines) - 1, 0)

    def __hash__(self) -> int:
        return hash(self.text)

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"Text(text={self.text}, cursor_ptr={self.cursor_position}, line_ptr={self._line_ptr}, column_ptr={self.column_ptr}, lines={self._text_lines}, edit_moode={self._edit_mode}, max_line_width={self._max_line_width}, line_count={self.line_count})"

    def __len__(self):
        return sum([len(line) for line in self._text_lines])

    def __contains__(self, lineno: int):
        return 0 <= lineno < len(self._text_lines)

    def __getitem__(self, lineno: int) -> str:
        return str(self._text_lines[lineno])

    def __iter__(self):
        for line in self._text_lines:
            yield line

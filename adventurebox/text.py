from typing import List, Union
from adventurebox.text_line import TextLine
from adventurebox.box_types import Position


class Text:
    def __init__(self, text: str = "", max_line_width: int = None):
        self._text_lines: List[TextLine] = []
        self._line_ptr = 0
        self._column_ptr = -1
        self._max_line_width = max_line_width
        self._edit_mode = False

        self.text = text

    def copy(self):
        new_text = Text(str(self.text), max_line_width=self._max_line_width)
        return new_text

    @property
    def edit_mode(self):
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, new_edit_mode: bool):
        previous_edit_mode = self._edit_mode
        self._edit_mode = new_edit_mode
        if not new_edit_mode and previous_edit_mode:
            if self._column_ptr >= len(self.current_line):
                self.to_end_of_line()

    @property
    def column_ptr(self):
        return max(self._column_ptr, 0)

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
    def lines(self) -> List[str]:
        if self._max_line_width is None:
            return [str(text_line) for text_line in self._text_lines]
        lines = []
        for text_line in self._text_lines:
            if len(text_line) >= self._max_line_width:
                for sub_line in text_line.split_on_width(self._max_line_width):
                    lines.append(str(sub_line))
            else:
                lines.append(str(text_line))
        return lines

    @property
    def text(self):
        return "\n".join((text_line for text_line in self.lines))

    @text.setter
    def text(self, text: str):
        self.erase()
        if text == "":
            return
        for line in text.split("\n"):
            self._text_lines.append(TextLine(line))
        self.to_last_line()
        self.to_end_of_line()

    def set_text_to_str(self, text: str):
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
    def last_column_on_line(self):
        return len(self.current_line) - (0 if self._edit_mode else 1)

    @property
    def last_line_in_text(self):
        return len(self._text_lines) - 1

    def increment_line_ptr(self):
        if self._line_ptr >= self.last_line_in_text:
            return
        self._line_ptr += 1
        if self._column_ptr >= len(self.current_line):
            self.to_end_of_line()

    def decrement_line_ptr(self):
        if self._line_ptr <= 0:
            return
        self._line_ptr -= 1
        if self._column_ptr >= len(self.current_line):
            self.to_end_of_line()

    def increment_column_ptr(self):
        if self._column_ptr >= self.last_column_on_line:
            if self._line_ptr >= self.last_line_in_text:
                return
            self._line_ptr += 1
            self.to_start_of_line()
        else:
            self._column_ptr += 1

    def decrement_column_ptr(self):
        if self._column_ptr <= 0:
            if self._line_ptr <= 0:
                return
            self._line_ptr -= 1
            self.to_end_of_line()
        else:
            self._column_ptr -= 1

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

    def to_start_of_next_word(self):
        while True:
            if self._column_ptr >= len(self._text_lines[self._line_ptr]):
                if self._line_ptr >= len(self._text_lines) - 1:
                    return
            else:
                splits = self.current_line.text.split(r"[ \.\,\;\:\!\?\-\]\[\(\)]")
                accumulated_length = 0
                for split in splits:
                    if self._column_ptr > accumulated_length:
                        if len(split) > 0:
                            self.column_ptr = accumulated_length
                            break
                    accumulated_length += len(split) + 1
            self._line_ptr += 1
            self.to_start_of_line()

    def delete_line(self):
        if len(self._text_lines) == 0:
            return

        self._text_lines.pop(self._line_ptr)
        if self._line_ptr > 0 and self._line_ptr >= len(self._text_lines):
            self.decrement_line_ptr()
        elif self._column_ptr > len(self.current_line):
            self.to_end_of_line()

    def backspace(self):
        """Delete the character before the cursor."""

        # If we're at the beginning of a line, delete the line.
        if self._column_ptr == 0:
            # If we're at the beginning of the first line, do nothing.
            if self._line_ptr == 0:
                return

            # If the current line is not empty, append it to the previous line.
            elif len(self.current_line) > 0:
                self.to_end_of_line()
                self.previous_line.insert(self.current_line.text)
                self._text_lines.pop(self._line_ptr)
                self._line_ptr -= 1
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
            self._column_ptr -= 1

    @property
    def line_count(self):
        return sum((line.line_count(self._max_line_width) for line in self._text_lines))

    def break_line(self):
        line_remainder = self.current_line.delete_to_end(self._column_ptr)
        self._text_lines.insert(self._line_ptr + 1, TextLine(line_remainder))
        self._line_ptr += 1
        self.to_start_of_line()

    def replace_character(self, ch: str):
        if len(ch) != 1:
            raise ValueError("Cannot replace character with string of length != 1")
        if self._column_ptr < 0:
            raise ValueError("Cannot replace character before the beginning of a line")
        if self._column_ptr > len(self.current_line):
            raise ValueError("Cannot replace character past the end of a line")

        if ch == "\n":
            self.break_line()
            if len(self.current_line) > 0:
                self.increment_column_ptr()
                self.backspace()
        else:
            self.current_line.replace_character(ch, self._column_ptr)
            self.increment_column_ptr()

    def insert_newline(self, before_cursor: bool = True):
        if self.column_ptr >= len(self.current_line):
            self._text_lines.insert(self._line_ptr + 1, TextLine())
        else:
            self.break_line()
        self._line_ptr += 1
        self.to_start_of_line()

    def insert(self, text: str, before_cursor: bool = True):
        if len(self._text_lines) == 0:
            self._text_lines.append(TextLine())

        for ch in text:
            if ch == "\n":
                self.insert_newline(before_cursor)
            else:
                self.current_line.insert(ch, self._column_ptr if before_cursor else self._column_ptr + 1)
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
        return f"Text(text={self.text}, cursor_ptr={self._line_ptr}, line_count={self.line_count})"

    def __len__(self):
        return sum([len(line) for line in self._text_lines])

    def __contains__(self, lineno: int):
        return 0 <= lineno < len(self._text_lines)

    def __getitem__(self, lineno: int) -> str:
        return str(self._text_lines[lineno])

    def __iter__(self):
        for line in self._text_lines:
            yield line

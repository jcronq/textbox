from typing import List, Union, Optional
from textbox.core.text_line import TextLine
from textbox.utils.box_types import Position
from textbox.core.text_segment import TextSegment
from textbox.core.segmented_text_line import SegmentedTextLine
from textbox.utils.color_code import ColorCode
from textbox.core.commands import CommandHistory
import logging


logger = logging.getLogger()


class Text:
    """An abstracted view of a block of text that can be manipulated in a variety of ways.
    It largely adds pointer manipulation and text manipulation to the TextLine class.

    Text may represent multiple lines of text if viewed with a max width. However, all
    operations on Text are treated as if it were a single block of text.

    Each TextLine represents blocks of text seperated by newlines.  Text is a collection of TextLines.
    """

    def __init__(self, text: str = "", max_line_width: int = None) -> None:
        self._text_lines: List[TextLine] = []
        self._line_ptr = 0
        self._column_ptr = 0
        self._max_line_width = max_line_width
        self._edit_mode = False
        self._default_color_pair = None
        self._max_history_lines: Optional[int] = None  # No limit by default
        self._is_selecting = False
        self._selection_start: Optional[Position] = None
        self._selection_end: Optional[Position] = None
        self.command_history = CommandHistory()

        self.text = text

    @property
    def color_pair(self) -> int:
        """Get the color pair of the text.  This is the default color pair for the text."""
        return self._default_color_pair

    @color_pair.setter
    def color_pair(self, value: int) -> None:
        self._default_color_pair = value

    def copy(self) -> "Text":
        """Create a deep copy of the text."""
        new_text = Text()
        new_text.max_line_width = self.max_line_width
        for line in self._text_lines:
            new_text._text_lines.append(line.copy())
        new_text.to_end_of_text()
        return new_text

    @property
    def char_at_cursor(self) -> str:
        """Get the character at the cursor."""
        return self.current_line[self.column_ptr]

    @property
    def edit_mode(self) -> bool:
        """Get whether the text is in edit mode.  In edit mode, text at the cursor can be appended to."""
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, new_edit_mode: bool) -> None:
        """Set whether the text is in edit mode.  In edit mode, text at the cursor can be appended to."""
        previous_edit_mode = self._edit_mode
        self._edit_mode = new_edit_mode
        # If turning off edit mode, and we were past the length of the current line (only possible in edit mode),
        # move cursor to end of line (ie. back one space.)
        if not new_edit_mode and previous_edit_mode and self.column_ptr >= len(self.current_line):
            self.to_end_of_line()

    @property
    def max_history_lines(self) -> Optional[int]:
        """Get the maximum number of lines to keep in history."""
        return self._max_history_lines

    @max_history_lines.setter
    def max_history_lines(self, value: Optional[int]) -> None:
        """Set the maximum number of lines to keep in history.

        When set, old lines will be automatically truncated to prevent
        unbounded memory growth. Set to None for unlimited history.
        """
        self._max_history_lines = value
        if value is not None:
            self._truncate_to_limit()

    def set_max_lines(self, max_lines: int) -> None:
        """Set the maximum number of lines to keep in history.

        Args:
            max_lines: Maximum lines to retain (keeps most recent)
        """
        self.max_history_lines = max_lines

    def _truncate_to_limit(self) -> None:
        """Truncate text lines to max_history_lines, keeping most recent."""
        if self._max_history_lines is None:
            return

        if len(self._text_lines) > self._max_history_lines:
            # Keep the most recent lines
            lines_to_remove = len(self._text_lines) - self._max_history_lines
            self._text_lines = self._text_lines[lines_to_remove:]

            # Adjust line pointer
            self._line_ptr = max(0, self._line_ptr - lines_to_remove)

            logger.debug(
                f"Truncated text history: removed {lines_to_remove} old lines, "
                f"kept {len(self._text_lines)} recent lines"
            )

    @property
    def column_ptr(self) -> int:
        """Get the column pointer of the text.
        This is the current position of the cursor in the text.
        This ignores viewing width.
        """
        return self._column_ptr

    @property
    def line_ptr(self) -> int:
        """Get the line pointer of the text.
        This ignores max_line_width."""
        return self._line_ptr

    @property
    def max_line_width(self) -> Optional[int]:
        """Get the maximum line width of the text.  This is the maximum number of characters that can be displayed on a line."""
        return self._max_line_width

    @max_line_width.setter
    def max_line_width(self, value: int) -> None:
        self._max_line_width = value

    @property
    def cursor_position(self) -> Position:
        """Get the cursor position of the text.
        This is the position of the cursor in the text with wrapping.
        """
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
    def is_selecting(self) -> bool:
        """Get whether the text is in selection mode (visual mode)."""
        return self._is_selecting

    @property
    def selection_start(self) -> Optional[Position]:
        """Get the start position of the visual selection."""
        return self._selection_start

    @property
    def selection_end(self) -> Optional[Position]:
        """Get the end position of the visual selection."""
        if self._is_selecting:
            # If actively selecting, use current cursor position as end
            return self.cursor_position
        return self._selection_end

    def start_selection(self) -> None:
        """Start a visual selection at the current cursor position."""
        self._is_selecting = True
        self._selection_start = self.cursor_position
        self._selection_end = None
        logger.debug(f"Started selection at {self._selection_start}")

    def end_selection(self) -> None:
        """End the visual selection and clear selection state."""
        self._is_selecting = False
        self._selection_start = None
        self._selection_end = None
        logger.debug("Ended selection")

    def get_selected_text(self) -> str:
        """Get the text within the current selection.

        Returns:
            str: The selected text, or empty string if no selection
        """
        if not self._is_selecting or self._selection_start is None:
            return ""

        start = self._selection_start
        end = self.cursor_position

        # Ensure start is before end
        if start.lineno > end.lineno or (start.lineno == end.lineno and start.colno > end.colno):
            start, end = end, start

        if start.lineno == end.lineno:
            # Same line selection
            return str(self._text_lines[start.lineno])[start.colno:end.colno]
        else:
            # Multi-line selection
            result = []
            for line_idx in range(start.lineno, end.lineno + 1):
                if line_idx >= len(self._text_lines):
                    break
                line = str(self._text_lines[line_idx])
                if line_idx == start.lineno:
                    result.append(line[start.colno:])
                elif line_idx == end.lineno:
                    result.append(line[:end.colno])
                else:
                    result.append(line)
            return "\n".join(result)

    @property
    def lines(self) -> List[TextLine]:
        """This renders the text into a list of TextLines that can be printed with wrapping.

        Returns:
            List[TextLine]: A list of TextLines that can be printed.
        """
        if self._max_line_width is None:
            return [str(text_line) for text_line in self._text_lines]

        lines = []
        for text_line in self._text_lines:
            if len(text_line) >= self._max_line_width:
                for sub_line in text_line.split_on_width(self._max_line_width):
                    next_line = sub_line.copy()
                    if next_line.default_color_pair != ColorCode.DEFAULT:
                        next_line.default_color_pair = self.color_pair
                    lines.append(next_line)

            else:
                next_line = text_line.copy()
                if next_line.default_color_pair != ColorCode.DEFAULT:
                    next_line.default_color_pair = self.color_pair
                lines.append(next_line)
        return lines

    @property
    def text(self) -> List[SegmentedTextLine]:
        """Get the text of the textbox.  This is the text as a string with wrapping."""
        return "\n".join((str(text_line) for text_line in self.lines))

    @text.setter
    def text(self, text: Union[str, List[str], List[TextLine], List[SegmentedTextLine], List[TextSegment]]):
        """Set the text of the textbox."""
        self.erase()
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
        self._text_lines = text
        self.to_last_line()
        self.to_end_of_line()

    def set_text_to_str(self, text: str) -> None:
        """Set the text of the textbox.  Default string formatting."""
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        self.text = text

    @property
    def current_line(self) -> Optional[TextLine]:
        if len(self._text_lines) == 0:
            return TextLine("")
        return self._text_lines[self._line_ptr]

    @property
    def previous_line(self) -> Optional[TextLine]:
        if self._line_ptr == 0:
            return None
        return self._text_lines[self._line_ptr - 1]

    @property
    def next_line(self) -> Optional[TextLine]:
        if self._line_ptr >= len(self._text_lines) - 1:
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

    def goto(self, position: Position) -> None:
        """Move cursor to the specified position with validation.

        Args:
            position: Target position (lineno, colno)

        Raises:
            ValueError: If position is out of bounds
        """
        if not isinstance(position, Position):
            raise TypeError(f"Expected Position, got {type(position).__name__}")

        # Validate line number
        if position.lineno < 0:
            raise ValueError(
                f"Line number {position.lineno} cannot be negative. "
                f"Valid range: 0 to {max(0, len(self._text_lines) - 1)}"
            )

        # Handle empty text case
        if len(self._text_lines) == 0:
            if position.lineno == 0 and position.colno == 0:
                # Allow goto(0, 0) on empty text - will be created on first insert
                self._line_ptr = 0
                self._column_ptr = 0
                return
            else:
                raise ValueError(
                    f"Text is empty. Only position (0, 0) is valid. "
                    f"Insert text first to create lines."
                )

        if position.lineno >= len(self._text_lines):
            raise ValueError(
                f"Line {position.lineno} out of range. "
                f"Valid range: 0 to {len(self._text_lines) - 1}. "
                f"Use Text.to_last_line() to move to the last line."
            )

        # Validate column number
        if position.colno < 0:
            raise ValueError(
                f"Column {position.colno} cannot be negative. "
                f"Use Text.to_start_of_line() to move to column 0."
            )

        # Column validation depends on the target line
        target_line = self._text_lines[position.lineno]
        max_col = len(target_line) if self._edit_mode else max(0, len(target_line) - 1)

        if position.colno > max_col:
            logger.warning(
                f"Column {position.colno} exceeds line length {len(target_line)}. "
                f"Clamping to {max_col}."
            )
            self._line_ptr = position.lineno
            self._column_ptr = max_col
            return

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

    def delete_selection(self) -> str:
        """Delete the text within the current selection.

        Returns:
            str: The deleted text
        """
        if not self._is_selecting or self._selection_start is None:
            return ""

        # Get the selected text before deleting
        selected_text = self.get_selected_text()

        start = self._selection_start
        end = self.cursor_position

        # Ensure start is before end
        if start.lineno > end.lineno or (start.lineno == end.lineno and start.colno > end.colno):
            start, end = end, start

        # Delete the selection
        if start.lineno == end.lineno:
            # Same line selection
            line = self._text_lines[start.lineno]
            before = str(line)[:start.colno]
            after = str(line)[end.colno:]
            # Replace the line with before + after
            self._text_lines[start.lineno] = TextLine(before + after)
            # Position cursor at start of deletion
            self._line_ptr = start.lineno
            self._column_ptr = start.colno
        else:
            # Multi-line selection
            # Keep the part before selection on first line and after selection on last line
            first_line = str(self._text_lines[start.lineno])[:start.colno]
            last_line = str(self._text_lines[end.lineno])[end.colno:]
            # Combine them
            new_line = TextLine(first_line + last_line)
            # Replace first line with combined line
            self._text_lines[start.lineno] = new_line
            # Delete lines in between (including last line)
            del self._text_lines[start.lineno + 1:end.lineno + 1]
            # Position cursor at start of deletion
            self._line_ptr = start.lineno
            self._column_ptr = start.colno

        # Clear selection state
        self.end_selection()
        logger.debug(f"Deleted selection: {repr(selected_text)}")

        return selected_text

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

        # Truncate to limit if set
        if self._max_history_lines is not None:
            self._truncate_to_limit()

    def insert(self, text: str) -> None:
        """Insert text at the current cursor position.

        Args:
            text: String to insert (can contain newlines)

        Raises:
            TypeError: If text is not a string
            RuntimeError: If not in edit mode
        """
        if not isinstance(text, str):
            raise TypeError(
                f"Expected str, got {type(text).__name__}. "
                f"Use str() to convert to string first."
            )

        if len(self._text_lines) == 0:
            self._text_lines.append(TextLine())

        if not self._edit_mode:
            raise RuntimeError(
                "Cannot insert text when not in edit mode. "
                "Set edit_mode=True before inserting."
            )

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

    def __len__(self) -> int:
        return sum([len(line) for line in self._text_lines])

    def __contains__(self, lineno: int):
        return 0 <= lineno < len(self._text_lines)

    def __getitem__(self, lineno: int) -> str:
        return str(self._text_lines[lineno])

    def __iter__(self):
        for line in self._text_lines:
            yield line

    def delete_current_line(self) -> str:
        """Delete the entire current line and return the deleted text.

        Returns:
            str: The deleted line text
        """
        if len(self._text_lines) == 0:
            return ""

        deleted_line = str(self._text_lines[self._line_ptr])

        # Delete the line
        self._text_lines.pop(self._line_ptr)

        # If we deleted the last line and there are still lines, move up
        if self._line_ptr > 0 and self._line_ptr >= len(self._text_lines):
            self._line_ptr -= 1

        # If we deleted all lines, create an empty line
        if len(self._text_lines) == 0:
            self._text_lines.append(TextLine())
            self._line_ptr = 0

        # Adjust column pointer if needed
        if self.column_ptr > len(self.current_line):
            self.to_end_of_line()

        return deleted_line

    def insert_line_below(self) -> None:
        """Insert an empty line below the current line and move cursor to it."""
        # Insert new empty line after current line
        self._text_lines.insert(self._line_ptr + 1, TextLine())
        # Move to the new line
        self._line_ptr += 1
        # Move cursor to start of line
        self.to_start_of_line()

    def insert_line_above(self) -> None:
        """Insert an empty line above the current line and move cursor to it."""
        # Insert new empty line before current line
        self._text_lines.insert(self._line_ptr, TextLine())
        # Cursor is already on the new line (same index, but content shifted down)
        # Move cursor to start of line
        self.to_start_of_line()

    def join_with_next_line(self) -> None:
        """Join the current line with the next line, adding a space between them."""
        # If there's no next line, do nothing
        if self._line_ptr >= len(self._text_lines) - 1:
            return

        current_line_text = str(self.current_line)
        next_line_text = str(self.next_line)

        # Join with a space
        joined_text = current_line_text + " " + next_line_text

        # Replace current line with joined text
        self._text_lines[self._line_ptr] = TextLine(joined_text)

        # Delete the next line
        self._text_lines.pop(self._line_ptr + 1)

    def get_current_line(self) -> str:
        """Get the text of the current line.

        Returns:
            str: The current line text
        """
        if len(self._text_lines) == 0:
            return ""
        return str(self.current_line)

    def paste_after(self, text: str) -> None:
        """Paste text after the cursor position.

        Args:
            text: Text to paste
        """
        if not text:
            return

        current_line = self.current_line
        current_text = str(current_line)

        # Insert text after cursor position
        # If at end of line, append
        if self.column_ptr >= len(current_text):
            new_text = current_text + text
            new_cursor = len(current_text) + len(text)
        else:
            # Insert after current character
            insert_pos = self.column_ptr + 1
            new_text = current_text[:insert_pos] + text + current_text[insert_pos:]
            new_cursor = insert_pos + len(text)

        # Update line
        self._text_lines[self._line_ptr] = TextLine(new_text)
        self._column_ptr = new_cursor

        # Move cursor to end of pasted text (vim behavior)
        if self._column_ptr > 0:
            self._column_ptr -= 1

    def paste_before(self, text: str) -> None:
        """Paste text before the cursor position.

        Args:
            text: Text to paste
        """
        if not text:
            return

        current_line = self.current_line
        current_text = str(current_line)

        # Insert text at cursor position
        insert_pos = self.column_ptr
        new_text = current_text[:insert_pos] + text + current_text[insert_pos:]

        # Update line
        self._text_lines[self._line_ptr] = TextLine(new_text)

        # Move cursor to end of pasted text
        self._column_ptr = insert_pos + len(text)

        # Move cursor to end of pasted text (vim behavior)
        if self._column_ptr > 0:
            self._column_ptr -= 1

    def delete_to_end_of_line(self) -> str:
        """Delete from cursor position to end of current line.

        Returns:
            str: The deleted text
        """
        if len(self._text_lines) == 0:
            return ""

        current_line = self.current_line
        deleted_text = str(current_line)[self.column_ptr:]

        # Keep only the text before cursor
        new_line_text = str(current_line)[:self.column_ptr]
        self._text_lines[self._line_ptr] = TextLine(new_line_text)

        # Adjust cursor if needed (shouldn't be necessary, but be safe)
        if self.column_ptr > len(self.current_line):
            self.to_end_of_line()

        return deleted_text

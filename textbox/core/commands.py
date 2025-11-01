"""Command pattern implementation for undo/redo functionality."""

from abc import ABC, abstractmethod
from typing import Optional, List, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from textbox.core.text import Text


class Command(ABC):
    """Base class for undoable commands."""

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass

    def redo(self) -> None:
        """Redo the command (default: just execute again)."""
        self.execute()


class CommandHistory:
    """Manages command history for undo/redo."""

    def __init__(self, max_history: int = 100):
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
        self._max_history = max_history

    def execute_command(self, command: Command) -> None:
        """Execute a command and add to history."""
        command.execute()
        self._undo_stack.append(command)
        # Clear redo stack when new command is executed
        self._redo_stack.clear()
        # Limit history size
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)

    def undo(self) -> bool:
        """Undo the last command. Returns True if successful."""
        if not self._undo_stack:
            return False
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        return True

    def redo(self) -> bool:
        """Redo the last undone command. Returns True if successful."""
        if not self._redo_stack:
            return False
        command = self._redo_stack.pop()
        command.redo()
        self._undo_stack.append(command)
        return True

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0

    def clear(self) -> None:
        """Clear all history."""
        self._undo_stack.clear()
        self._redo_stack.clear()


class InsertTextCommand(Command):
    """Command to insert text at cursor."""

    def __init__(self, text: 'Text', inserted_text: str):
        self.text = text
        self.inserted_text = inserted_text
        self.position: Tuple[int, int] = text.cursor_position  # Save position before insert

    def execute(self) -> None:
        """Insert the text."""
        self.text.insert(self.inserted_text)

    def undo(self) -> None:
        """Remove the inserted text."""
        # Go to where we inserted and delete that many characters
        for _ in self.inserted_text:
            self.text.backspace()


class DeleteCharCommand(Command):
    """Command to delete character(s)."""

    def __init__(self, text: 'Text'):
        self.text = text
        self.position: Tuple[int, int] = text.cursor_position
        # Save character about to be deleted
        # backspace deletes the character before the cursor
        if text.column_ptr > 0:
            line_text = text.current_line.text
            self.deleted_char = line_text[text.column_ptr - 1] if text.column_ptr <= len(line_text) else ''
        else:
            self.deleted_char = ''

    def execute(self) -> None:
        """Delete the character."""
        self.text.backspace()

    def undo(self) -> None:
        """Restore the deleted character."""
        if self.deleted_char:
            self.text.insert(self.deleted_char)


class DeleteLineCommand(Command):
    """Command to delete an entire line (dd operation)."""

    def __init__(self, text: 'Text'):
        self.text = text
        self.line_index = text.line_ptr
        self.deleted_line = str(text.current_line)

    def execute(self) -> None:
        """Delete the current line."""
        self.text.delete_current_line()

    def undo(self) -> None:
        """Restore the deleted line."""
        from textbox.core.text_line import TextLine
        self.text._text_lines.insert(self.line_index, TextLine(self.deleted_line))
        self.text._line_ptr = self.line_index


class InsertLineBelowCommand(Command):
    """Command to insert a line below current line (o operation)."""

    def __init__(self, text: 'Text'):
        self.text = text
        self.original_line_ptr = text.line_ptr

    def execute(self) -> None:
        """Insert an empty line below current line."""
        self.text.insert_line_below()

    def undo(self) -> None:
        """Remove the inserted line."""
        # The new line is at line_ptr, remove it
        self.text._text_lines.pop(self.text._line_ptr)
        # Restore original position
        self.text._line_ptr = self.original_line_ptr


class InsertLineAboveCommand(Command):
    """Command to insert a line above current line (O operation)."""

    def __init__(self, text: 'Text'):
        self.text = text
        self.original_line_ptr = text.line_ptr

    def execute(self) -> None:
        """Insert an empty line above current line."""
        self.text.insert_line_above()

    def undo(self) -> None:
        """Remove the inserted line."""
        # The new line is at line_ptr, remove it
        self.text._text_lines.pop(self.text._line_ptr)
        # Restore original position
        self.text._line_ptr = self.original_line_ptr


class DeleteToEndOfLineCommand(Command):
    """Command to delete from cursor to end of line (D operation)."""

    def __init__(self, text: 'Text'):
        self.text = text
        self.line_ptr = text.line_ptr
        self.column_ptr = text.column_ptr
        self.deleted_text = ""

    def execute(self) -> None:
        """Delete from cursor to end of line."""
        self.deleted_text = self.text.delete_to_end_of_line()

    def undo(self) -> None:
        """Restore the deleted text."""
        if self.deleted_text:
            # Restore position first
            self.text._line_ptr = self.line_ptr
            self.text._column_ptr = self.column_ptr
            # Insert requires edit mode
            old_edit_mode = self.text.edit_mode
            self.text.edit_mode = True
            self.text.insert(self.deleted_text)
            self.text.edit_mode = old_edit_mode
            # Restore cursor position (insert moves it)
            self.text._column_ptr = self.column_ptr


class ChangeToEndOfLineCommand(Command):
    """Command to change from cursor to end of line (C operation)."""

    def __init__(self, text: 'Text'):
        self.text = text
        self.line_ptr = text.line_ptr
        self.column_ptr = text.column_ptr
        self.deleted_text = ""

    def execute(self) -> None:
        """Delete from cursor to end of line."""
        # C command only deletes if not already at end of line
        if self.text.column_ptr < self.text.last_column_on_line:
            self.deleted_text = self.text.delete_to_end_of_line()

    def undo(self) -> None:
        """Restore the deleted text."""
        if self.deleted_text:
            # Restore position first
            self.text._line_ptr = self.line_ptr
            self.text._column_ptr = self.column_ptr
            # Insert requires edit mode
            old_edit_mode = self.text.edit_mode
            self.text.edit_mode = True
            self.text.insert(self.deleted_text)
            self.text.edit_mode = old_edit_mode
            # Restore cursor position (insert moves it)
            self.text._column_ptr = self.column_ptr


class JoinLinesCommand(Command):
    """Command to join current line with next line (J operation)."""

    def __init__(self, text: 'Text'):
        self.text = text
        self.line_ptr = text.line_ptr
        # Save current line and next line before joining
        self.current_line = str(text.current_line)
        if text.line_ptr < len(text._text_lines) - 1:
            self.next_line = str(text._text_lines[text.line_ptr + 1])
        else:
            self.next_line = None

    def execute(self) -> None:
        """Join current line with next line."""
        if self.next_line is not None:
            self.text.join_with_next_line()

    def undo(self) -> None:
        """Split the joined lines back."""
        if self.next_line is not None:
            from textbox.core.text_line import TextLine
            # Restore original lines
            self.text._text_lines[self.line_ptr] = TextLine(self.current_line)
            self.text._text_lines.insert(self.line_ptr + 1, TextLine(self.next_line))


class PasteAfterCommand(Command):
    """Command to paste text after cursor (p operation)."""

    def __init__(self, text: 'Text', content: str):
        self.text = text
        self.content = content
        self.original_line_ptr = text.line_ptr
        self.original_column_ptr = text.column_ptr

    def execute(self) -> None:
        """Paste text after cursor."""
        self.text.paste_after(self.content)

    def undo(self) -> None:
        """Remove the pasted text."""
        # Restore position to where we were before paste
        self.text._line_ptr = self.original_line_ptr
        # paste_after inserts AFTER the cursor position, so pasted text starts at column_ptr + 1
        # We need to delete len(content) characters starting from column_ptr + 1
        for i in range(len(self.content)):
            # Delete character at position column_ptr + 1 (repeatedly, since after each delete, next char shifts left)
            line = self.text._text_lines[self.text._line_ptr]
            line_text = line.text
            delete_pos = self.original_column_ptr + 1
            if delete_pos < len(line_text):
                new_text = line_text[:delete_pos] + line_text[delete_pos + 1:]
                from textbox.core.text_line import TextLine
                self.text._text_lines[self.text._line_ptr] = TextLine(new_text)
        # Restore column pointer
        self.text._column_ptr = self.original_column_ptr


class PasteBeforeCommand(Command):
    """Command to paste text before cursor (P operation)."""

    def __init__(self, text: 'Text', content: str):
        self.text = text
        self.content = content
        self.original_line_ptr = text.line_ptr
        self.original_column_ptr = text.column_ptr

    def execute(self) -> None:
        """Paste text before cursor."""
        self.text.paste_before(self.content)

    def undo(self) -> None:
        """Remove the pasted text."""
        # Restore position to where we were before paste
        self.text._line_ptr = self.original_line_ptr
        # paste_before inserts BEFORE the cursor position, so pasted text is at positions column_ptr to column_ptr+len-1
        # After paste, cursor moves forward by len(content), so we need to delete backwards
        # We'll delete len(content) characters starting from column_ptr (going forward)
        for i in range(len(self.content)):
            # Delete character at original_column_ptr repeatedly (as chars shift left after each delete)
            line = self.text._text_lines[self.text._line_ptr]
            line_text = line.text
            delete_pos = self.original_column_ptr
            if delete_pos < len(line_text):
                new_text = line_text[:delete_pos] + line_text[delete_pos + 1:]
                from textbox.core.text_line import TextLine
                self.text._text_lines[self.text._line_ptr] = TextLine(new_text)
        # Restore column pointer
        self.text._column_ptr = self.original_column_ptr

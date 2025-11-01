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

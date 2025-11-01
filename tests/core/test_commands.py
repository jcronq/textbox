"""Tests for command pattern and undo/redo functionality."""

import pytest
from textbox.core.commands import Command, CommandHistory, InsertTextCommand, DeleteCharCommand
from textbox.core.text import Text
from textbox.utils.box_types import Position


class SimpleCommand(Command):
    """Simple test command that tracks execution state."""

    def __init__(self):
        self.executed = False
        self.undone = False
        self.redone = False

    def execute(self) -> None:
        self.executed = True
        self.undone = False

    def undo(self) -> None:
        self.undone = True
        self.executed = False

    def redo(self) -> None:
        self.redone = True
        self.executed = True


class TestCommandHistory:
    """Test CommandHistory class."""

    def test_execute_command(self):
        """Test executing a command adds it to history."""
        history = CommandHistory()
        cmd = SimpleCommand()

        history.execute_command(cmd)

        assert cmd.executed is True
        assert history.can_undo() is True
        assert history.can_redo() is False

    def test_undo_works(self):
        """Test undo reverses a command."""
        history = CommandHistory()
        cmd = SimpleCommand()

        history.execute_command(cmd)
        result = history.undo()

        assert result is True
        assert cmd.undone is True
        assert history.can_undo() is False
        assert history.can_redo() is True

    def test_redo_works(self):
        """Test redo re-applies an undone command."""
        history = CommandHistory()
        cmd = SimpleCommand()

        history.execute_command(cmd)
        history.undo()
        result = history.redo()

        assert result is True
        assert cmd.redone is True
        assert history.can_undo() is True
        assert history.can_redo() is False

    def test_undo_redo_sequence(self):
        """Test multiple undo/redo operations."""
        history = CommandHistory()
        cmd1 = SimpleCommand()
        cmd2 = SimpleCommand()
        cmd3 = SimpleCommand()

        # Execute three commands
        history.execute_command(cmd1)
        history.execute_command(cmd2)
        history.execute_command(cmd3)

        # Undo twice
        assert history.undo() is True
        assert cmd3.undone is True
        assert history.undo() is True
        assert cmd2.undone is True

        # Redo once
        assert history.redo() is True
        assert cmd2.redone is True

        # Undo again
        assert history.undo() is True
        assert cmd2.undone is True

    def test_max_history_limit(self):
        """Test that history respects max_history limit."""
        history = CommandHistory(max_history=3)
        commands = [SimpleCommand() for _ in range(5)]

        for cmd in commands:
            history.execute_command(cmd)

        # Only last 3 should be in history
        assert history.undo() is True  # cmd5
        assert history.undo() is True  # cmd4
        assert history.undo() is True  # cmd3
        assert history.undo() is False  # No more (cmd1 and cmd2 were dropped)

    def test_can_undo_can_redo(self):
        """Test can_undo and can_redo methods."""
        history = CommandHistory()

        # Initially, can't undo or redo
        assert history.can_undo() is False
        assert history.can_redo() is False

        # After executing command, can undo
        history.execute_command(SimpleCommand())
        assert history.can_undo() is True
        assert history.can_redo() is False

        # After undo, can redo
        history.undo()
        assert history.can_undo() is False
        assert history.can_redo() is True

        # After redo, can undo again
        history.redo()
        assert history.can_undo() is True
        assert history.can_redo() is False

    def test_new_command_clears_redo_stack(self):
        """Test that executing a new command clears the redo stack."""
        history = CommandHistory()
        cmd1 = SimpleCommand()
        cmd2 = SimpleCommand()

        history.execute_command(cmd1)
        history.undo()

        # Can redo at this point
        assert history.can_redo() is True

        # Execute new command
        history.execute_command(cmd2)

        # Redo stack should be cleared
        assert history.can_redo() is False

    def test_undo_on_empty_stack(self):
        """Test undo on empty stack returns False."""
        history = CommandHistory()
        assert history.undo() is False

    def test_redo_on_empty_stack(self):
        """Test redo on empty stack returns False."""
        history = CommandHistory()
        assert history.redo() is False

    def test_clear_history(self):
        """Test clearing history."""
        history = CommandHistory()
        history.execute_command(SimpleCommand())
        history.execute_command(SimpleCommand())

        assert history.can_undo() is True

        history.clear()

        assert history.can_undo() is False
        assert history.can_redo() is False


class TestInsertTextCommand:
    """Test InsertTextCommand."""

    def test_insert_text_command_execute(self):
        """Test executing insert text command."""
        text = Text("hello")
        text.edit_mode = True
        text.to_end_of_line()
        cmd = InsertTextCommand(text, " world")

        cmd.execute()

        assert text.current_line.text == "hello world"

    def test_insert_text_command_undo(self):
        """Test undoing insert text command."""
        text = Text("hello")
        text.edit_mode = True
        text.to_end_of_line()
        cmd = InsertTextCommand(text, " world")

        cmd.execute()
        assert text.current_line.text == "hello world"

        cmd.undo()
        assert text.current_line.text == "hello"

    def test_insert_text_command_saves_position(self):
        """Test that insert command saves cursor position."""
        text = Text("hello")
        text.edit_mode = True
        text.goto(Position(0, 2))  # Middle of word

        cmd = InsertTextCommand(text, "XX")
        assert cmd.position == (0, 2)

    def test_insert_multiple_chars(self):
        """Test inserting multiple characters."""
        text = Text("ab")
        text.edit_mode = True
        text.goto(Position(0, 1))
        cmd = InsertTextCommand(text, "123")

        cmd.execute()
        assert text.current_line.text == "a123b"

        cmd.undo()
        assert text.current_line.text == "ab"


class TestDeleteCharCommand:
    """Test DeleteCharCommand."""

    def test_delete_char_command_execute(self):
        """Test executing delete char command."""
        text = Text("hello")
        text.edit_mode = True
        text.to_end_of_line()
        cmd = DeleteCharCommand(text)

        cmd.execute()

        assert text.current_line.text == "hell"

    def test_delete_char_command_undo(self):
        """Test undoing delete char command."""
        text = Text("hello")
        text.edit_mode = True
        text.to_end_of_line()
        cmd = DeleteCharCommand(text)

        cmd.execute()
        assert text.current_line.text == "hell"

        cmd.undo()
        assert text.current_line.text == "hello"

    def test_delete_char_saves_deleted_char(self):
        """Test that delete command saves the deleted character."""
        text = Text("hello")
        text.edit_mode = True
        text.goto(Position(0, 2))

        cmd = DeleteCharCommand(text)
        # Should save 'e' (char before cursor, since backspace deletes before)
        assert cmd.deleted_char == "e"

    def test_delete_at_start_of_line(self):
        """Test deleting at start of line."""
        text = Text("hello")
        text.edit_mode = True
        text.goto(Position(0, 0))
        cmd = DeleteCharCommand(text)

        # Should save empty string when at start
        assert cmd.deleted_char == ""

        cmd.execute()
        # Behavior depends on Text.backspace() implementation
        # Just verify undo doesn't crash
        cmd.undo()


class TestCommandIntegration:
    """Test commands working together with Text."""

    def test_text_has_command_history(self):
        """Test that Text instances have a command_history attribute."""
        text = Text("hello")
        assert hasattr(text, 'command_history')
        assert isinstance(text.command_history, CommandHistory)

    def test_insert_and_delete_sequence(self):
        """Test a sequence of insert and delete commands."""
        text = Text("")
        text.edit_mode = True

        # Insert "hello"
        insert1 = InsertTextCommand(text, "hello")
        insert1.execute()
        assert text.current_line.text == "hello"

        # Insert " world"
        insert2 = InsertTextCommand(text, " world")
        insert2.execute()
        assert text.current_line.text == "hello world"

        # Delete last char
        delete1 = DeleteCharCommand(text)
        delete1.execute()
        assert text.current_line.text == "hello worl"

        # Undo delete
        delete1.undo()
        assert text.current_line.text == "hello world"

        # Undo second insert
        insert2.undo()
        assert text.current_line.text == "hello"

        # Undo first insert
        insert1.undo()
        assert text.current_line.text == ""

    def test_command_history_execute_command(self):
        """Test using CommandHistory.execute_command with Text."""
        text = Text("")
        text.edit_mode = True
        cmd = InsertTextCommand(text, "test")

        text.command_history.execute_command(cmd)

        assert text.current_line.text == "test"
        assert text.command_history.can_undo() is True

        text.command_history.undo()
        assert text.current_line.text == ""

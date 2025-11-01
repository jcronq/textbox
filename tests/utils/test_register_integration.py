"""Integration tests for register system with Text class."""

import pytest
from textbox.core.text import Text
from textbox.utils.registers import RegisterManager


class TestTextAndRegisterIntegration:
    """Test that Text class methods work with RegisterManager."""

    def test_get_current_line_returns_string(self):
        """Test that get_current_line returns proper string."""
        text = Text()
        text.edit_mode = True
        text.insert("Hello World")

        line = text.get_current_line()
        assert line == "Hello World"
        assert isinstance(line, str)

    def test_paste_after_inserts_correctly(self):
        """Test paste_after method."""
        text = Text()
        text.edit_mode = True
        text.insert("abc")
        text.to_start_of_line()  # Cursor at 'a'

        text.paste_after("X")
        assert str(text) == "aXbc"

    def test_paste_before_inserts_correctly(self):
        """Test paste_before method."""
        text = Text()
        text.edit_mode = True
        text.insert("abc")
        text.to_start_of_line()  # Cursor at 'a'

        text.paste_before("X")
        assert str(text) == "Xabc"

    def test_yank_and_paste_workflow(self):
        """Test complete yank and paste workflow."""
        rm = RegisterManager()
        text = Text()

        # Set up text
        text.edit_mode = True
        text.insert("line one")

        # Yank current line
        yanked = text.get_current_line()
        rm.yank_to_register(None, yanked)

        # Verify it's in registers
        assert rm.get_register('"') == "line one"  # unnamed
        assert rm.get_register('0') == "line one"  # yank register

        # Create new text and paste
        text2 = Text()
        text2.edit_mode = True
        text2.insert("start")
        text2.to_start_of_line()

        content = rm.get_register('"')
        text2.paste_after(content)

        assert "line one" in str(text2)

    def test_delete_to_register_workflow(self):
        """Test delete to register workflow."""
        rm = RegisterManager()
        text = Text()

        # Set up text
        text.edit_mode = True
        text.insert("to be deleted")

        # Delete line
        deleted = text.delete_current_line()
        rm.delete_to_register(None, deleted)

        # Should be in unnamed and register 1
        assert rm.get_register('"') == "to be deleted"
        assert rm.get_register('1') == "to be deleted"

        # Original text should be empty
        assert str(text) == ""

    def test_multiple_deletes_shift_registers(self):
        """Test that multiple deletes shift numbered registers."""
        rm = RegisterManager()

        # Delete 3 items
        rm.delete_to_register(None, "first delete")
        rm.delete_to_register(None, "second delete")
        rm.delete_to_register(None, "third delete")

        # Check they're in correct registers
        assert rm.get_register('1') == "third delete"  # most recent
        assert rm.get_register('2') == "second delete"
        assert rm.get_register('3') == "first delete"  # oldest

    def test_named_register_workflow(self):
        """Test yanking to named registers."""
        rm = RegisterManager()
        text = Text()

        # Yank to register 'a'
        text.edit_mode = True
        text.insert("content for a")
        yanked = text.get_current_line()
        rm.yank_to_register('a', yanked)

        # Yank different content to register 'b'
        text2 = Text()
        text2.edit_mode = True
        text2.insert("content for b")
        yanked2 = text2.get_current_line()
        rm.yank_to_register('b', yanked2)

        # Verify both registers kept their content
        assert rm.get_register('a') == "content for a"
        assert rm.get_register('b') == "content for b"

        # Most recent yank should be in register 0
        assert rm.get_register('0') == "content for b"

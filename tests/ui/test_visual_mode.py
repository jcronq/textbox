"""
Tests for Visual Mode implementation.

Following TDD: Write tests first describing intended visual mode behavior.
These tests describe what SHOULD happen for visual mode in v0.2.0.
"""

import pytest
from unittest.mock import MagicMock, patch, call
import curses
from textbox.ui.workspace import InputOutputWorkspace, INPUT_MODE
from textbox.ui.input_manager import AsyncInputManager
from textbox.ui.window import Window
from textbox.core.text import Text
from textbox.utils.box_types import Position


class TestVisualModeEnum:
    """Test that INPUT_MODE enum includes visual modes."""

    def test_input_mode_has_visual(self):
        """Test that INPUT_MODE has VISUAL mode."""
        assert hasattr(INPUT_MODE, 'VISUAL')

    def test_input_mode_has_visual_line(self):
        """Test that INPUT_MODE has VISUAL_LINE mode."""
        assert hasattr(INPUT_MODE, 'VISUAL_LINE')


class TestVisualModeEntry:
    """Test entering and exiting visual modes."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_v_key_enters_visual_mode_from_command(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that 'v' key in COMMAND mode enters VISUAL mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Start in command mode
        workspace.enter_command_mode()
        assert workspace.input_mode == INPUT_MODE.COMMAND

        # Press 'v' to enter visual mode
        await workspace.handle_keypress(ord('v'))

        assert workspace.input_mode == INPUT_MODE.VISUAL

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_V_key_enters_visual_line_mode(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that 'V' key in COMMAND mode enters VISUAL_LINE mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('V'))

        assert workspace.input_mode == INPUT_MODE.VISUAL_LINE

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_escape_exits_visual_mode(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that Escape key exits visual mode back to COMMAND."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Enter visual mode
        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('v'))
        assert workspace.input_mode == INPUT_MODE.VISUAL

        # Press Escape
        await workspace.handle_keypress(27)

        assert workspace.input_mode == INPUT_MODE.COMMAND

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_visual_mode_shows_status(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that entering visual mode updates status line."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('v'))

        # Should show "-- VISUAL --" in command box
        assert "VISUAL" in str(workspace.command_box.text).upper()


class TestTextSelectionTracking:
    """Test that Text class can track visual selections."""

    def test_text_has_selection_start(self):
        """Test that Text has selection_start property."""
        text = Text("Hello World")
        assert hasattr(text, 'selection_start')

    def test_text_has_selection_end(self):
        """Test that Text has selection_end property."""
        text = Text("Hello World")
        assert hasattr(text, 'selection_end')

    def test_text_has_is_selecting_property(self):
        """Test that Text has is_selecting property."""
        text = Text("Hello World")
        assert hasattr(text, 'is_selecting')

    def test_text_start_selection_sets_anchor(self):
        """Test that start_selection() sets the selection anchor."""
        text = Text("Hello World")
        text.goto(Position(0, 5))

        text.start_selection()

        assert text.is_selecting == True
        assert text.selection_start == Position(0, 5)

    def test_text_end_selection_clears_state(self):
        """Test that end_selection() clears selection state."""
        text = Text("Hello World")
        text.goto(Position(0, 5))
        text.start_selection()

        text.end_selection()

        assert text.is_selecting == False
        assert text.selection_start is None
        assert text.selection_end is None

    def test_selection_updates_with_cursor_movement(self):
        """Test that selection_end updates as cursor moves."""
        text = Text("Hello World")
        text.goto(Position(0, 0))
        text.start_selection()

        # Move cursor
        text.goto(Position(0, 5))

        assert text.selection_start == Position(0, 0)
        assert text.selection_end == Position(0, 5)


class TestVisualModeNavigation:
    """Test that navigation works in visual mode and extends selection."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_hjkl_navigation_works_in_visual_mode(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that h, j, k, l keys move cursor in visual mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Add some text
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line 1\nLine 2\nLine 3")
        workspace.user_box.text.goto(Position(0, 0))

        # Enter visual mode
        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('v'))

        # Move right with 'l'
        await workspace.handle_keypress(ord('l'))

        # Cursor should have moved
        assert workspace.user_box.text.cursor_position.colno > 0

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_word_navigation_works_in_visual_mode(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that w, b keys work in visual mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("hello world test")
        workspace.user_box.text.goto(Position(0, 0))

        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('v'))

        # Word forward with 'w'
        await workspace.handle_keypress(ord('w'))

        # Should have moved to next word
        assert workspace.user_box.text.cursor_position.colno > 0


class TestVisualModeOperations:
    """Test visual mode operations (yank, delete, change)."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_d_deletes_visual_selection(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that 'd' in visual mode deletes selection."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Hello World")
        workspace.user_box.text.goto(Position(0, 0))

        # Enter visual mode and select "Hello"
        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('v'))
        workspace.user_box.text.goto(Position(0, 5))

        # Delete with 'd'
        await workspace.handle_keypress(ord('d'))

        # Text should be deleted
        text_str = str(workspace.user_box.text)
        assert "Hello" not in text_str or len(text_str) < 11
        # Should return to command mode
        assert workspace.input_mode == INPUT_MODE.COMMAND

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_y_yanks_visual_selection(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that 'y' in visual mode yanks (copies) selection."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Hello World")
        workspace.user_box.text.goto(Position(0, 0))

        # Enter visual mode and select "Hello"
        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('v'))
        workspace.user_box.text.goto(Position(0, 5))

        # Yank with 'y'
        await workspace.handle_keypress(ord('y'))

        # Text should remain unchanged
        assert str(workspace.user_box.text) == "Hello World"
        # Should have stored the yanked text somewhere
        assert hasattr(workspace, 'yank_register') or hasattr(workspace, '_yank_buffer')
        # Should return to command mode
        assert workspace.input_mode == INPUT_MODE.COMMAND

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_c_changes_visual_selection(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that 'c' in visual mode deletes and enters insert mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Hello World")
        workspace.user_box.text.goto(Position(0, 0))

        # Enter visual mode and select "Hello"
        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('v'))
        workspace.user_box.text.goto(Position(0, 5))

        # Change with 'c'
        await workspace.handle_keypress(ord('c'))

        # Selection should be deleted
        text_str = str(workspace.user_box.text)
        assert "Hello" not in text_str or len(text_str) < 11
        # Should enter insert mode
        assert workspace.input_mode == INPUT_MODE.INSERT


class TestVisualLineMode:
    """Test VISUAL_LINE mode specific behavior."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_visual_line_selects_entire_lines(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that VISUAL_LINE mode selects entire lines."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line 1\nLine 2\nLine 3")
        workspace.user_box.text.goto(Position(1, 3))  # Middle of line 2

        # Enter visual line mode
        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('V'))

        # Should have line-based selection
        # Check that selection includes full line
        assert workspace.user_box.text.is_selecting == True

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_visual_line_d_deletes_entire_lines(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that 'd' in VISUAL_LINE mode deletes entire lines."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line 1\nLine 2\nLine 3")
        workspace.user_box.text.goto(Position(1, 0))

        # Enter visual line mode and delete
        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('V'))
        await workspace.handle_keypress(ord('d'))

        # Line 2 should be deleted
        text_str = str(workspace.user_box.text)
        assert "Line 2" not in text_str
        # Should still have other lines
        assert "Line 1" in text_str or "Line 3" in text_str


class TestVisualModeEdgeCases:
    """Test edge cases in visual mode."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_visual_mode_on_empty_text(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that visual mode handles empty text gracefully."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Enter visual mode on empty text
        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('v'))

        # Should not crash
        assert workspace.input_mode == INPUT_MODE.VISUAL

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_visual_mode_at_end_of_text(self, mock_curses, mock_inputbox, mock_textbox):
        """Test visual mode when cursor is at end of text."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Hello")
        workspace.user_box.text.edit_mode = False
        workspace.user_box.text.goto(Position(0, 4))  # Last character

        # Enter visual mode
        workspace.enter_command_mode()
        await workspace.handle_keypress(ord('v'))

        # Should work
        assert workspace.input_mode == INPUT_MODE.VISUAL

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_cannot_enter_visual_from_insert_mode(self, mock_curses, mock_inputbox, mock_textbox):
        """Test that 'v' in INSERT mode inserts 'v', doesn't enter VISUAL."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Enter insert mode
        workspace.enter_insert_mode()
        assert workspace.input_mode == INPUT_MODE.INSERT

        # Press 'v' - should insert character
        await workspace.handle_keypress(ord('v'))

        # Should still be in insert mode
        assert workspace.input_mode == INPUT_MODE.INSERT
        # Should have inserted 'v'
        assert 'v' in str(workspace.user_box.text)

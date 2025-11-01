"""
Tests for InputOutputWorkspace mode switching and mode-specific behavior.

Tests mode transitions, focused box changes, and mode-specific key handling.
Target: Improve workspace.py coverage from 14% to 70%.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from textbox.ui.workspace import InputOutputWorkspace, INPUT_MODE
from textbox.ui.window import Window
from textbox.ui.input_manager import AsyncInputManager


class TestInsertMode:
    """Test INSERT mode functionality."""

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_enter_insert_mode_changes_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that enter_insert_mode() changes to INSERT mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_insert_mode()

        assert workspace.input_mode == INPUT_MODE.INSERT
        mock_curses.curs_set.assert_called_with(1)

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_insert_mode_sets_focused_box(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that INSERT mode sets user_box as focused."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_insert_mode()

        assert workspace.focused_box == workspace.user_box

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_insert_mode_enables_edit_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that INSERT mode sets edit_mode on user_box text."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_insert_mode()

        # The focused box's text should have edit_mode = True
        assert workspace.focused_box.text.edit_mode == True


class TestReplaceMode:
    """Test REPLACE mode functionality."""

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_enter_replace_mode_changes_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that enter_replace_mode() changes to REPLACE mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_replace_mode()

        assert workspace.input_mode == INPUT_MODE.REPLACE
        mock_curses.curs_set.assert_called_with(1)

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_replace_mode_sets_focused_box(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that REPLACE mode sets user_box as focused."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_replace_mode()

        assert workspace.focused_box == workspace.user_box


class TestCommandMode:
    """Test COMMAND mode functionality."""

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_enter_command_mode_changes_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that enter_command_mode() changes to COMMAND mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        # Start in a different mode first
        workspace.enter_insert_mode()

        # Now enter command mode
        workspace.enter_command_mode()

        assert workspace.input_mode == INPUT_MODE.COMMAND
        mock_curses.curs_set.assert_called_with(1)

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_command_mode_sets_focused_box(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that COMMAND mode keeps user_box focused."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_mode()

        assert workspace.focused_box == workspace.user_box


class TestReadingMode:
    """Test READING (read-only) mode functionality."""

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_enter_reading_mode_changes_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that enter_reading_mode() changes to READ_ONLY mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_reading_mode()

        assert workspace.input_mode == INPUT_MODE.READ_ONLY
        mock_curses.curs_set.assert_called_with(0)

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_reading_mode_sets_focused_box(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that READING mode sets output_box as focused."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_reading_mode()

        assert workspace.focused_box == workspace.output_box


class TestCommandEntryMode:
    """Test COMMAND_ENTRY mode functionality."""

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_enter_command_entry_mode_changes_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that enter_command_entry_mode() changes to COMMAND_ENTRY mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_entry_mode()

        assert workspace.input_mode == INPUT_MODE.COMMAND_ENTRY

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_command_entry_mode_sets_focused_box(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that COMMAND_ENTRY mode sets command_box as focused."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_entry_mode()

        assert workspace.focused_box == workspace.command_box


class TestModeTransitions:
    """Test transitions between different modes."""

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_transition_insert_to_command(self, mock_textbox, mock_inputbox, mock_curses):
        """Test transitioning from INSERT to COMMAND mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        workspace.enter_insert_mode()
        assert workspace.input_mode == INPUT_MODE.INSERT

        workspace.enter_command_mode()
        assert workspace.input_mode == INPUT_MODE.COMMAND

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_transition_command_to_reading(self, mock_textbox, mock_inputbox, mock_curses):
        """Test transitioning from COMMAND to READ_ONLY mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        workspace.enter_command_mode()
        assert workspace.input_mode == INPUT_MODE.COMMAND

        workspace.enter_reading_mode()
        assert workspace.input_mode == INPUT_MODE.READ_ONLY

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_mode_can_be_changed_multiple_times(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that mode can be changed multiple times."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        workspace.enter_insert_mode()
        assert workspace.input_mode == INPUT_MODE.INSERT

        workspace.enter_command_mode()
        assert workspace.input_mode == INPUT_MODE.COMMAND

        workspace.enter_reading_mode()
        assert workspace.input_mode == INPUT_MODE.READ_ONLY

        workspace.enter_replace_mode()
        assert workspace.input_mode == INPUT_MODE.REPLACE

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_focused_box_changes_with_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that focused box changes appropriately with mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # INSERT mode -> user_box
        workspace.enter_insert_mode()
        assert workspace.focused_box == workspace.user_box

        # READING mode -> output_box
        workspace.enter_reading_mode()
        assert workspace.focused_box == workspace.output_box

        # COMMAND_ENTRY mode -> command_box
        workspace.enter_command_entry_mode()
        assert workspace.focused_box == workspace.command_box

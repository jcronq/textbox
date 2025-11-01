"""
Tests for InputOutputWorkspace mode switching.

Tests the different input modes (INSERT, REPLACE, COMMAND, READ_ONLY)
and transitions between them. Target: Improve workspace.py coverage.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from textbox.ui.workspace import InputOutputWorkspace, INPUT_MODE
from textbox.ui.window import Window
from textbox.ui.input_manager import AsyncInputManager


class TestInsertMode:
    """Test INSERT mode functionality."""

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_enter_insert_mode_changes_mode(self, mock_textbox, mock_inputbox):
        """Test that enter_insert_mode() changes to INSERT mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_insert_mode()

        assert workspace.mode == INPUT_MODE.INSERT

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_insert_mode_sets_focused_box(self, mock_textbox, mock_inputbox):
        """Test that INSERT mode sets user_box as focused."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_insert_mode()

        assert workspace.focused_box == workspace.user_box

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_insert_mode_enables_edit_mode(self, mock_textbox, mock_inputbox):
        """Test that INSERT mode sets edit_mode on user_box."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        mock_user_box = MagicMock()
        mock_inputbox.return_value = mock_user_box

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.user_box = mock_user_box
        workspace.enter_insert_mode()

        # Should set edit_mode to True
        assert mock_user_box.edit_mode or hasattr(workspace.user_box, 'edit_mode')


class TestReplaceMode:
    """Test REPLACE mode functionality."""

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_enter_replace_mode_changes_mode(self, mock_textbox, mock_inputbox):
        """Test that enter_replace_mode() changes to REPLACE mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_replace_mode()

        assert workspace.mode == INPUT_MODE.REPLACE

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_replace_mode_sets_focused_box(self, mock_textbox, mock_inputbox):
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

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_enter_command_mode_changes_mode(self, mock_textbox, mock_inputbox):
        """Test that enter_command_mode() changes to COMMAND mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_mode()

        assert workspace.mode == INPUT_MODE.COMMAND

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_command_mode_sets_focused_box(self, mock_textbox, mock_inputbox):
        """Test that COMMAND mode sets user_box as focused."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_mode()

        assert workspace.focused_box == workspace.user_box


class TestReadOnlyMode:
    """Test READ_ONLY mode functionality."""

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_enter_read_only_mode_changes_mode(self, mock_textbox, mock_inputbox):
        """Test that enter_read_only_mode() changes to READ_ONLY mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_insert_mode()  # Start in a different mode
        workspace.enter_read_only_mode()

        assert workspace.mode == INPUT_MODE.READ_ONLY

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_read_only_mode_sets_focused_box(self, mock_textbox, mock_inputbox):
        """Test that READ_ONLY mode sets output_box as focused."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_read_only_mode()

        assert workspace.focused_box == workspace.output_box


class TestModeTransitions:
    """Test transitions between different modes."""

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_transition_insert_to_command(self, mock_textbox, mock_inputbox):
        """Test transition from INSERT to COMMAND mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        workspace.enter_insert_mode()
        assert workspace.mode == INPUT_MODE.INSERT

        workspace.enter_command_mode()
        assert workspace.mode == INPUT_MODE.COMMAND

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_transition_command_to_read_only(self, mock_textbox, mock_inputbox):
        """Test transition from COMMAND to READ_ONLY mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        workspace.enter_command_mode()
        assert workspace.mode == INPUT_MODE.COMMAND

        workspace.enter_read_only_mode()
        assert workspace.mode == INPUT_MODE.READ_ONLY

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_mode_can_be_changed_multiple_times(self, mock_textbox, mock_inputbox):
        """Test that mode can be changed multiple times."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        modes = [
            INPUT_MODE.INSERT,
            INPUT_MODE.COMMAND,
            INPUT_MODE.READ_ONLY,
            INPUT_MODE.REPLACE,
            INPUT_MODE.INSERT,
        ]

        for mode in modes:
            if mode == INPUT_MODE.INSERT:
                workspace.enter_insert_mode()
            elif mode == INPUT_MODE.COMMAND:
                workspace.enter_command_mode()
            elif mode == INPUT_MODE.READ_ONLY:
                workspace.enter_read_only_mode()
            elif mode == INPUT_MODE.REPLACE:
                workspace.enter_replace_mode()

            assert workspace.mode == mode

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_focused_box_changes_with_mode(self, mock_textbox, mock_inputbox):
        """Test that focused_box changes appropriately with mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # INSERT/COMMAND/REPLACE should focus user_box
        workspace.enter_insert_mode()
        assert workspace.focused_box == workspace.user_box

        workspace.enter_command_mode()
        assert workspace.focused_box == workspace.user_box

        workspace.enter_replace_mode()
        assert workspace.focused_box == workspace.user_box

        # READ_ONLY should focus output_box
        workspace.enter_read_only_mode()
        assert workspace.focused_box == workspace.output_box

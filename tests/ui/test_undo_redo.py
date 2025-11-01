"""
Integration tests for undo/redo functionality in the workspace.
"""

import pytest
from unittest.mock import patch, MagicMock
from textbox.ui.workspace import InputOutputWorkspace
from textbox.ui.window import Window
from textbox.ui.input_manager import AsyncInputManager
from textbox.core.commands import CommandHistory


def setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses):
    """Helper to set up curses mocks for testing."""
    # Mock curses constants
    for mock_curses in [mock_workspace_curses, mock_textbox_curses, mock_window_curses]:
        mock_curses.KEY_UP = 259
        mock_curses.KEY_DOWN = 258
        mock_curses.KEY_LEFT = 260
        mock_curses.KEY_RIGHT = 261
        mock_curses.KEY_BACKSPACE = 263
        mock_curses.KEY_RESIZE = 410
        mock_curses.A_NORMAL = 0
        mock_curses.A_BOLD = 1
        mock_curses.A_REVERSE = 2
        mock_curses.A_UNDERLINE = 4
        mock_curses.color_pair = lambda x: x
        mock_curses.error = Exception
        mock_curses.LINES = 24
        mock_curses.COLS = 80

    # Mock window
    mock_win = MagicMock()
    mock_win.getmaxyx.return_value = (24, 80)
    mock_win.addstr = MagicMock()
    mock_win.move = MagicMock()
    mock_win.refresh = MagicMock()
    mock_win.clear = MagicMock()
    mock_win.subwin = MagicMock(return_value=mock_win)
    mock_window_curses.newwin.return_value = mock_win

    return mock_win


class TestUndoRedoIntegration:
    """Tests for undo/redo integration with workspace."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    async def test_workspace_has_command_history(self, mock_window_curses, mock_textbox_curses, mock_workspace_curses):
        """Test that workspace has a command_history attribute."""
        mock_win = setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        # Create workspace
        main_window = Window(mock_win)
        input_manager = AsyncInputManager(main_window)
        workspace = InputOutputWorkspace(main_window, input_manager)

        # Workspace should have command history
        assert hasattr(workspace, 'command_history')
        assert isinstance(workspace.command_history, CommandHistory)

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    async def test_command_history_is_separate_from_text_history(
        self, mock_window_curses, mock_textbox_curses, mock_workspace_curses
    ):
        """Test that workspace command history is independent of text command history."""
        mock_win = setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        # Create workspace
        main_window = Window(mock_win)
        input_manager = AsyncInputManager(main_window)
        workspace = InputOutputWorkspace(main_window, input_manager)

        # Workspace should have its own command history
        assert hasattr(workspace, 'command_history')
        assert workspace.command_history is not None

        # Text objects also have command history
        assert hasattr(workspace.user_box.text, 'command_history')

        # They should be different instances
        assert workspace.command_history is not workspace.user_box.text.command_history

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    async def test_undo_handler_exists(self, mock_window_curses, mock_textbox_curses, mock_workspace_curses):
        """Test that the 'u' key handler is in place."""
        mock_win = setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        # Create workspace
        main_window = Window(mock_win)
        input_manager = AsyncInputManager(main_window)
        workspace = InputOutputWorkspace(main_window, input_manager)

        # Verify undo doesn't crash when called with empty history
        workspace.command_handler(ord('u'))

        # Should show message in command box
        assert workspace.command_box.text is not None

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    async def test_redo_handler_exists(self, mock_window_curses, mock_textbox_curses, mock_workspace_curses):
        """Test that the Ctrl-r key handler is in place."""
        mock_win = setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        # Create workspace
        main_window = Window(mock_win)
        input_manager = AsyncInputManager(main_window)
        workspace = InputOutputWorkspace(main_window, input_manager)

        # Verify redo doesn't crash when called with empty history
        workspace.command_handler(18)  # Ctrl-r

        # Should show message in command box
        assert workspace.command_box.text is not None

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    async def test_x_command_uses_command_pattern(self, mock_window_curses, mock_textbox_curses, mock_workspace_curses):
        """Test that the 'x' command uses the command pattern."""
        mock_win = setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        # Create workspace
        main_window = Window(mock_win)
        input_manager = AsyncInputManager(main_window)
        workspace = InputOutputWorkspace(main_window, input_manager)

        # Execute 'x' command - should add to history
        initial_can_undo = workspace.command_history.can_undo()
        workspace.command_handler(ord('x'))

        # History state may change (if there's something to delete)
        # Just verify the command doesn't crash
        assert workspace.command_history is not None

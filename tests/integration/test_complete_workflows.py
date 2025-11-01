"""Integration tests for complete editing workflows.

Tests end-to-end user workflows combining multiple features.
"""

import pytest
from unittest.mock import MagicMock, patch
import curses

from textbox.ui.workspace import InputOutputWorkspace, INPUT_MODE
from textbox.ui.window import Window
from textbox.ui.input_manager import AsyncInputManager
from textbox.utils.box_types import BoundingBox, Dimensions, Position


def create_mock_window():
    """Create a properly mocked Window for testing."""
    mock_window = MagicMock(spec=Window)
    mock_window.height = 24
    mock_window.width = 80
    mock_window.dimensions = Dimensions(24, 80)
    mock_window.position = Position(0, 0)
    mock_window.bounding_box = BoundingBox(0, 0, 24, 80)

    def create_subwindow(box):
        sub = MagicMock(spec=Window)
        sub.height = box.height
        sub.width = box.width
        sub.dimensions = Dimensions(box.height, box.width)
        sub.position = Position(box.lineno, box.colno)
        sub.bounding_box = box
        return sub

    mock_window.create_new_window.side_effect = create_subwindow
    return mock_window


def setup_curses_mocks(*mocks):
    """Setup curses mocks with common configuration."""
    for mock_curses in mocks:
        mock_curses.curs_set = MagicMock()
        mock_curses.color_pair = MagicMock(return_value=1)
        mock_curses.error = curses.error
        mock_curses.A_NORMAL = 0
        mock_curses.A_BOLD = 1
        mock_curses.A_REVERSE = 2


class TestCompleteEditingWorkflow:
    """Test complete editing workflows."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_visual_yank_paste_undo_workflow(
        self, mock_workspace_curses, mock_textbox_curses, mock_window_curses
    ):
        """Test complete workflow: visual select → yank → paste → undo."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Setup text
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("hello world")
        workspace.user_box.text.edit_mode = False
        workspace.user_box.text.to_start_of_text()

        # Enter visual mode
        workspace.enter_visual_mode()
        assert workspace.input_mode == INPUT_MODE.VISUAL

        # Select "hello"
        for _ in range(5):
            await workspace.handle_keypress(ord('l'))

        # Yank
        await workspace.handle_keypress(ord('y'))
        assert workspace.input_mode == INPUT_MODE.COMMAND

        # Move to end
        await workspace.handle_keypress(ord('$'))

        # Paste
        await workspace.handle_keypress(ord('p'))
        text_after_paste = str(workspace.user_box.text)
        # Paste after cursor adds the yanked text
        assert "hello worldhello" == text_after_paste or "hello world hello" in text_after_paste

        # Undo paste
        await workspace.handle_keypress(ord('u'))
        text_after_undo = str(workspace.user_box.text)
        assert "hello world" in text_after_undo

        # Redo paste
        await workspace.handle_keypress(18)  # Ctrl-r
        text_after_redo = str(workspace.user_box.text)
        assert text_after_redo == text_after_paste

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_search_and_replace_workflow(
        self, mock_workspace_curses, mock_textbox_curses, mock_window_curses
    ):
        """Test search → navigate → delete → undo workflow."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Setup text with multiple occurrences
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("foo bar\nfoo baz\nfoo qux")
        workspace.user_box.text.edit_mode = False
        workspace.user_box.text.to_start_of_text()

        # Search for "foo"
        await workspace.handle_keypress(ord('/'))
        for char in "foo":
            await workspace.handle_keypress(ord(char))
        await workspace.handle_keypress(ord('\n'))

        # Should be on first "foo"
        assert workspace.user_box.text.line_ptr == 0

        # Go to next occurrence
        await workspace.handle_keypress(ord('n'))
        assert workspace.user_box.text.line_ptr == 1

        # Delete the line
        await workspace.handle_keypress(ord('d'))
        await workspace.handle_keypress(ord('d'))

        # Verify deletion
        text_str = str(workspace.user_box.text)
        assert "baz" not in text_str

        # Undo
        await workspace.handle_keypress(ord('u'))
        text_str = str(workspace.user_box.text)
        assert "baz" in text_str

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_register_workflow(
        self, mock_workspace_curses, mock_textbox_curses, mock_window_curses
    ):
        """Test register workflow: yank to named register → paste multiple times."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Setup text
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("line1\nline2\nline3")
        workspace.user_box.text.edit_mode = False
        workspace.user_box.text._line_ptr = 0

        # Yank line 1 to register 'a'
        await workspace.handle_keypress(ord('"'))  # Register prefix
        await workspace.handle_keypress(ord('a'))  # Register name
        await workspace.handle_keypress(ord('y'))
        await workspace.handle_keypress(ord('y'))

        # Move to line 2
        await workspace.handle_keypress(ord('j'))
        assert workspace.user_box.text.line_ptr == 1

        # Paste from register 'a'
        await workspace.handle_keypress(ord('"'))
        await workspace.handle_keypress(ord('a'))
        await workspace.handle_keypress(ord('p'))

        # Move to line 3 (accounting for pasted line)
        await workspace.handle_keypress(ord('j'))
        await workspace.handle_keypress(ord('j'))

        # Paste from register 'a' again
        await workspace.handle_keypress(ord('"'))
        await workspace.handle_keypress(ord('a'))
        await workspace.handle_keypress(ord('p'))

        # Verify we pasted twice from same register
        text_str = str(workspace.user_box.text)
        # Should have original line1 plus two pastes of line1
        assert text_str.count("line1") == 3


class TestModeTransitionWorkflows:
    """Test workflows involving mode transitions."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_insert_command_visual_workflow(
        self, mock_workspace_curses, mock_textbox_curses, mock_window_curses
    ):
        """Test INSERT → COMMAND → VISUAL → COMMAND workflow."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Start in COMMAND, enter INSERT
        await workspace.handle_keypress(ord('i'))
        assert workspace.input_mode == INPUT_MODE.INSERT

        # Type some text
        for char in "test text":
            await workspace.handle_keypress(ord(char))

        # ESC to COMMAND
        await workspace.handle_keypress(27)
        assert workspace.input_mode == INPUT_MODE.COMMAND

        # Enter VISUAL
        await workspace.handle_keypress(ord('v'))
        assert workspace.input_mode == INPUT_MODE.VISUAL

        # Select some text
        await workspace.handle_keypress(ord('l'))
        await workspace.handle_keypress(ord('l'))

        # Delete (returns to COMMAND)
        await workspace.handle_keypress(ord('d'))
        assert workspace.input_mode == INPUT_MODE.COMMAND


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_empty_text_operations(
        self, mock_workspace_curses, mock_textbox_curses, mock_window_curses
    ):
        """Test operations on empty text."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Try to delete empty text
        await workspace.handle_keypress(ord('d'))
        await workspace.handle_keypress(ord('d'))

        # Try to yank empty text
        await workspace.handle_keypress(ord('y'))
        await workspace.handle_keypress(ord('y'))

        # Try to paste into empty text
        await workspace.handle_keypress(ord('p'))

        # Try to undo with no history
        await workspace.handle_keypress(ord('u'))

        # Should not crash

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_unicode_text_handling(
        self, mock_workspace_curses, mock_textbox_curses, mock_window_curses
    ):
        """Test handling of unicode characters."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Insert unicode
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("hello 世界 🌍")
        workspace.user_box.text.edit_mode = False

        # Try visual mode on unicode
        workspace.user_box.text.to_start_of_text()
        workspace.enter_visual_mode()

        # Select some characters
        for _ in range(8):
            await workspace.handle_keypress(ord('l'))

        # Yank
        await workspace.handle_keypress(ord('y'))

        # Paste
        await workspace.handle_keypress(ord('$'))
        await workspace.handle_keypress(ord('p'))

        # Should handle unicode correctly

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_rapid_undo_redo_sequence(
        self, mock_workspace_curses, mock_textbox_curses, mock_window_curses
    ):
        """Test rapid undo/redo operations."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Make several edits
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("a")
        workspace.user_box.text.edit_mode = False

        await workspace.handle_keypress(ord('x'))  # Delete
        await workspace.handle_keypress(ord('u'))  # Undo
        await workspace.handle_keypress(18)  # Redo (Ctrl-r)
        await workspace.handle_keypress(ord('u'))  # Undo again
        await workspace.handle_keypress(18)  # Redo again
        await workspace.handle_keypress(ord('u'))  # Undo

        # Should remain stable

"""Tests for search functionality (/, ?, n, N commands)."""

import pytest
from unittest.mock import MagicMock, patch
import curses

from textbox.ui.workspace import InputOutputWorkspace, INPUT_MODE
from textbox.ui.window import Window
from textbox.ui.input_manager import AsyncInputManager


def setup_curses_mocks(*mocks):
    """Setup curses mocks with common configuration."""
    for mock_curses in mocks:
        mock_curses.curs_set = MagicMock()
        mock_curses.color_pair = MagicMock(return_value=1)
        mock_curses.error = curses.error
        mock_curses.A_NORMAL = 0
        mock_curses.A_BOLD = 1
        mock_curses.A_REVERSE = 2


def create_mock_window():
    """Create a properly mocked Window for testing."""
    from textbox.utils.box_types import BoundingBox, Position, Dimensions

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


class TestSearchEntry:
    """Test entering search mode with / and ?."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_forward_slash_enters_search_mode(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that '/' in COMMAND mode enters forward search mode."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Should start in command mode
        assert workspace.input_mode == INPUT_MODE.COMMAND

        # Press '/' to enter search mode
        await workspace.handle_keypress(ord('/'))

        # Should be in search entry mode
        assert workspace.input_mode == INPUT_MODE.SEARCH_ENTRY
        # Command box should show search prompt
        assert "/" in str(workspace.command_box.text)

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_question_mark_enters_backward_search_mode(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that '?' in COMMAND mode enters backward search mode."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Press '?' to enter backward search mode
        await workspace.handle_keypress(ord('?'))

        # Should be in search entry mode
        assert workspace.input_mode == INPUT_MODE.SEARCH_ENTRY
        # Command box should show backward search prompt
        assert "?" in str(workspace.command_box.text)


class TestSearchExecution:
    """Test executing searches and finding results."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_forward_search_finds_text(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that forward search finds text and moves cursor."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Set up text with search target
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("hello world\nfoo bar\nhello again")
        workspace.user_box.text.edit_mode = False
        workspace.user_box.text.to_start_of_text()

        # Enter search mode
        await workspace.handle_keypress(ord('/'))

        # Type "bar"
        for char in "bar":
            await workspace.handle_keypress(ord(char))

        # Press Enter to execute search
        await workspace.handle_keypress(ord('\n'))

        # Should be back in command mode
        assert workspace.input_mode == INPUT_MODE.COMMAND

        # Cursor should be on line with "bar" (line 1)
        assert workspace.user_box.text.line_ptr == 1

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_backward_search_finds_text(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that backward search finds text and moves cursor backward."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Set up text with search target
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("hello world\nfoo bar\nhello again")
        workspace.user_box.text.edit_mode = False
        # Move to end
        workspace.user_box.text._line_ptr = 2
        workspace.user_box.text._column_ptr = 5

        # Enter backward search mode
        await workspace.handle_keypress(ord('?'))

        # Type "foo"
        for char in "foo":
            await workspace.handle_keypress(ord(char))

        # Press Enter to execute search
        await workspace.handle_keypress(ord('\n'))

        # Should be back in command mode
        assert workspace.input_mode == INPUT_MODE.COMMAND

        # Cursor should be on line with "foo" (line 1)
        assert workspace.user_box.text.line_ptr == 1


class TestSearchNavigation:
    """Test navigating through search results with n and N."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_n_finds_next_occurrence(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'n' finds next search result."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Set up text with multiple occurrences
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("hello world\nhello foo\nhello bar")
        workspace.user_box.text.edit_mode = False
        workspace.user_box.text.to_start_of_text()

        # Search for "hello"
        await workspace.handle_keypress(ord('/'))
        for char in "hello":
            await workspace.handle_keypress(ord(char))
        await workspace.handle_keypress(ord('\n'))

        # Should be on first line
        assert workspace.user_box.text.line_ptr == 0

        # Press 'n' to find next
        await workspace.handle_keypress(ord('n'))

        # Should move to second line
        assert workspace.user_box.text.line_ptr == 1

        # Press 'n' again
        await workspace.handle_keypress(ord('n'))

        # Should move to third line
        assert workspace.user_box.text.line_ptr == 2

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_N_finds_previous_occurrence(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'N' finds previous search result."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Set up text with multiple occurrences
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("hello world\nhello foo\nhello bar")
        workspace.user_box.text.edit_mode = False
        # Start at beginning of second line
        workspace.user_box.text._line_ptr = 1
        workspace.user_box.text._column_ptr = 0

        # Search backward for "hello" (should find line 0)
        await workspace.handle_keypress(ord('?'))
        for char in "hello":
            await workspace.handle_keypress(ord(char))
        await workspace.handle_keypress(ord('\n'))

        # Should find line 0 (searching backward from line 1)
        assert workspace.user_box.text.line_ptr == 0

        # Press 'N' to find next in opposite direction (forward for backward search)
        await workspace.handle_keypress(ord('N'))

        # Should move forward to line 1
        assert workspace.user_box.text.line_ptr == 1

        # Press 'N' again
        await workspace.handle_keypress(ord('N'))

        # Should move forward to line 2
        assert workspace.user_box.text.line_ptr == 2

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_search_wraps_around(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that search wraps around to beginning when reaching end."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Set up text with occurrences
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("hello world\nfoo bar\nhello again")
        workspace.user_box.text.edit_mode = False
        workspace.user_box.text._line_ptr = 2  # Start at last line

        # Search for "hello"
        await workspace.handle_keypress(ord('/'))
        for char in "hello":
            await workspace.handle_keypress(ord(char))
        await workspace.handle_keypress(ord('\n'))

        # Should wrap to first occurrence (line 0)
        assert workspace.user_box.text.line_ptr == 0


class TestSearchEdgeCases:
    """Test edge cases for search functionality."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_search_not_found_shows_message(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that searching for non-existent text shows message."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Set up text
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("hello world")
        workspace.user_box.text.edit_mode = False

        # Search for non-existent text
        await workspace.handle_keypress(ord('/'))
        for char in "xyz":
            await workspace.handle_keypress(ord(char))
        await workspace.handle_keypress(ord('\n'))

        # Should show "not found" message in command box
        assert "not found" in str(workspace.command_box.text).lower() or "not" in str(workspace.command_box.text).lower()

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_escape_cancels_search(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that ESC cancels search entry."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Enter search mode
        await workspace.handle_keypress(ord('/'))
        assert workspace.input_mode == INPUT_MODE.SEARCH_ENTRY

        # Type some text
        for char in "test":
            await workspace.handle_keypress(ord(char))

        # Press ESC to cancel
        await workspace.handle_keypress(27)

        # Should be back in command mode
        assert workspace.input_mode == INPUT_MODE.COMMAND

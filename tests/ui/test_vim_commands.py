"""
Tests for additional Vim commands implementation (Phase 2.3).

Following TDD: Write tests first describing intended vim command behavior.
These tests describe what SHOULD happen for vim commands in v0.2.0.
"""

import pytest
from unittest.mock import MagicMock, patch
import curses
from textbox.ui.workspace import InputOutputWorkspace, INPUT_MODE
from textbox.ui.input_manager import AsyncInputManager
from textbox.ui.window import Window
from textbox.core.text import Text
from textbox.utils.box_types import Position


def setup_curses_mocks(*mocks):
    """Setup curses mocks with common configuration."""
    for mock_curses in mocks:
        mock_curses.curs_set = MagicMock()
        mock_curses.color_pair = MagicMock(return_value=1)
        mock_curses.error = curses.error


def create_mock_window():
    """Create a properly mocked Window for testing."""
    from textbox.utils.box_types import BoundingBox, Position, Dimensions

    mock_window = MagicMock(spec=Window)
    mock_window.height = 24
    mock_window.width = 80
    mock_window.dimensions = Dimensions(24, 80)
    mock_window.position = Position(0, 0)
    mock_window.bounding_box = BoundingBox(0, 0, 24, 80)

    # Mock create_new_window to return a Window-like mock
    def create_subwindow(box, *args, **kwargs):
        subwin = MagicMock(spec=Window)
        subwin.height = box.height
        subwin.width = box.width
        subwin.dimensions = box.dimensions
        subwin.position = box.position
        subwin.bounding_box = box
        # Mock the internal curses window
        subwin._local_window = MagicMock()
        subwin._local_window.getmaxyx.return_value = (box.height, box.width)
        return subwin

    mock_window.create_new_window = MagicMock(side_effect=create_subwindow)
    return mock_window


class TestDeleteLineCommand:
    """Test dd - delete current line."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_dd_deletes_current_line(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'dd' in COMMAND mode deletes the current line."""

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        # Add multi-line text
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line 1\nLine 2\nLine 3")
        workspace.user_box.text.goto(Position(1, 0))  # Line 2
        workspace.enter_command_mode()

        # Press 'd' twice
        await workspace.handle_keypress(ord('d'))
        await workspace.handle_keypress(ord('d'))

        # Line 2 should be deleted
        text_str = str(workspace.user_box.text)
        assert "Line 2" not in text_str
        assert "Line 1" in text_str
        assert "Line 3" in text_str

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_dd_stores_in_yank_register(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'dd' stores deleted line in yank register."""

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line to delete")
        workspace.user_box.text.goto(Position(0, 0))
        workspace.enter_command_mode()

        # Delete line
        await workspace.handle_keypress(ord('d'))
        await workspace.handle_keypress(ord('d'))

        # Should be stored in unnamed register
        assert "Line to delete" in workspace.register_manager.get_register('"')

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_dd_on_single_line_leaves_empty(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'dd' on single line leaves empty text."""

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Only line")
        workspace.user_box.text.goto(Position(0, 0))
        workspace.enter_command_mode()

        # Delete line
        await workspace.handle_keypress(ord('d'))
        await workspace.handle_keypress(ord('d'))

        # Should have empty or single empty line
        text_str = str(workspace.user_box.text).strip()
        assert text_str == "" or len(workspace.user_box.text._text_lines) == 1

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_single_d_does_not_delete(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that single 'd' without second 'd' does nothing."""

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line 1\nLine 2")
        original_text = str(workspace.user_box.text)
        workspace.user_box.text.goto(Position(0, 0))
        workspace.enter_command_mode()

        # Press 'd' once, then different key
        await workspace.handle_keypress(ord('d'))
        await workspace.handle_keypress(ord('j'))  # Move down instead

        # Text should be unchanged
        assert str(workspace.user_box.text) == original_text


class TestOpenLineCommands:
    """Test o and O - open line below/above."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_o_opens_line_below(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'o' opens a new line below and enters INSERT mode."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line 1\nLine 2")
        workspace.user_box.text.goto(Position(0, 3))  # On Line 1
        workspace.enter_command_mode()

        # Press 'o'
        await workspace.handle_keypress(ord('o'))

        # Should be in INSERT mode
        assert workspace.input_mode == INPUT_MODE.INSERT
        # Cursor should be on line 1 (the new empty line)
        assert workspace.user_box.text.line_ptr == 1
        # Cursor should be at start of line
        assert workspace.user_box.text.column_ptr == 0

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_O_opens_line_above(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'O' opens a new line above and enters INSERT mode."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line 1\nLine 2")
        workspace.user_box.text.goto(Position(1, 3))  # On Line 2
        workspace.enter_command_mode()

        # Press 'O'
        await workspace.handle_keypress(ord('O'))

        # Should be in INSERT mode
        assert workspace.input_mode == INPUT_MODE.INSERT
        # Cursor should be on the new line (still line 1)
        assert workspace.user_box.text.line_ptr == 1
        # Cursor should be at start of line
        assert workspace.user_box.text.column_ptr == 0

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_o_at_end_of_text(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'o' at end of text creates new line."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Only line")
        workspace.user_box.text.goto(Position(0, 0))
        workspace.enter_command_mode()

        # Press 'o'
        await workspace.handle_keypress(ord('o'))

        # Should have 2 lines now
        assert len(workspace.user_box.text._text_lines) >= 2
        assert workspace.input_mode == INPUT_MODE.INSERT


class TestAppendInsertAtBoundaries:
    """Test A and I - append at end / insert at beginning."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_A_appends_at_end_of_line(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'A' moves to end of line and enters INSERT mode."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Hello World")
        workspace.user_box.text.goto(Position(0, 0))  # Start of line
        workspace.enter_command_mode()

        # Press 'A'
        await workspace.handle_keypress(ord('A'))

        # Should be at end of line
        assert workspace.user_box.text.column_ptr == len("Hello World")
        # Should be in INSERT mode
        assert workspace.input_mode == INPUT_MODE.INSERT

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_I_inserts_at_beginning_of_line(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'I' moves to beginning of line and enters INSERT mode."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Hello World")
        workspace.user_box.text.goto(Position(0, 5))  # Middle of line
        workspace.enter_command_mode()

        # Press 'I'
        await workspace.handle_keypress(ord('I'))

        # Should be at start of line
        assert workspace.user_box.text.column_ptr == 0
        # Should be in INSERT mode
        assert workspace.input_mode == INPUT_MODE.INSERT


class TestChangeDeleteToEnd:
    """Test C and D - change/delete to end of line."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_C_changes_to_end_of_line(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'C' deletes from cursor to end and enters INSERT mode."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Hello World")
        workspace.user_box.text.goto(Position(0, 6))  # After "Hello "
        workspace.enter_command_mode()

        # Press 'C'
        await workspace.handle_keypress(ord('C'))

        # Should have deleted "World"
        text_str = str(workspace.user_box.text)
        assert text_str.startswith("Hello ")
        assert "World" not in text_str
        # Should be in INSERT mode
        assert workspace.input_mode == INPUT_MODE.INSERT

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_D_deletes_to_end_of_line(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'D' deletes from cursor to end and stays in COMMAND mode."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Hello World")
        workspace.user_box.text.goto(Position(0, 6))  # After "Hello "
        workspace.enter_command_mode()

        # Press 'D'
        await workspace.handle_keypress(ord('D'))

        # Should have deleted "World"
        text_str = str(workspace.user_box.text)
        assert text_str.startswith("Hello ")
        assert "World" not in text_str
        # Should remain in COMMAND mode
        assert workspace.input_mode == INPUT_MODE.COMMAND

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_C_at_end_of_line_just_enters_insert(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'C' at end of line just enters INSERT mode."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Hello")
        workspace.enter_command_mode()
        workspace.user_box.text.to_end_of_line()

        original_text = str(workspace.user_box.text)

        # Press 'C'
        await workspace.handle_keypress(ord('C'))

        # Text should be unchanged
        assert str(workspace.user_box.text) == original_text
        # Should be in INSERT mode
        assert workspace.input_mode == INPUT_MODE.INSERT


class TestChangeLineCommand:
    """Test cc - change entire line."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_cc_changes_entire_line(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'cc' deletes entire line and enters INSERT mode."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line 1\nLine 2\nLine 3")
        workspace.user_box.text.goto(Position(1, 3))  # Middle of Line 2
        workspace.enter_command_mode()

        # Press 'c' twice
        await workspace.handle_keypress(ord('c'))
        await workspace.handle_keypress(ord('c'))

        # Line 2 should be empty (or deleted and replaced with empty)
        # Should be in INSERT mode
        assert workspace.input_mode == INPUT_MODE.INSERT
        # Cursor should be on line 1 (where Line 2 was)
        assert workspace.user_box.text.line_ptr == 1

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_cc_stores_in_yank_register(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'cc' stores deleted line in yank register."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line to change")
        workspace.user_box.text.goto(Position(0, 0))
        workspace.enter_command_mode()

        # Change line
        await workspace.handle_keypress(ord('c'))
        await workspace.handle_keypress(ord('c'))

        # Should be stored in unnamed register
        assert "Line to change" in workspace.register_manager.get_register('"')


class TestJoinLinesCommand:
    """Test J - join current line with next."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_J_joins_with_next_line(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'J' joins current line with next line."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line 1\nLine 2")
        workspace.user_box.text.goto(Position(0, 0))
        workspace.enter_command_mode()

        # Press 'J'
        await workspace.handle_keypress(ord('J'))

        # Lines should be joined
        text_str = str(workspace.user_box.text)
        assert "Line 1 Line 2" in text_str or "Line 1Line 2" in text_str

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_J_adds_space_between_lines(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'J' adds a space between joined lines."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Hello\nWorld")
        workspace.user_box.text.goto(Position(0, 0))
        workspace.enter_command_mode()

        # Press 'J'
        await workspace.handle_keypress(ord('J'))

        # Should have space between
        text_str = str(workspace.user_box.text)
        assert "Hello World" in text_str

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_J_on_last_line_does_nothing(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'J' on last line does nothing."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line 1\nLine 2")
        workspace.user_box.text.goto(Position(1, 0))  # Last line
        workspace.enter_command_mode()

        original_text = str(workspace.user_box.text)

        # Press 'J'
        await workspace.handle_keypress(ord('J'))

        # Text should be unchanged
        assert str(workspace.user_box.text) == original_text

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_J_stays_in_command_mode(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'J' keeps us in COMMAND mode."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Line 1\nLine 2")
        workspace.user_box.text.goto(Position(0, 0))
        workspace.enter_command_mode()

        # Press 'J'
        await workspace.handle_keypress(ord('J'))

        # Should remain in COMMAND mode
        assert workspace.input_mode == INPUT_MODE.COMMAND


class TestTextClassMethods:
    """Test new methods added to Text class."""

    def test_delete_current_line_method_exists(self):
        """Test that Text has delete_current_line method."""
        text = Text("Line 1\nLine 2\nLine 3")
        assert hasattr(text, 'delete_current_line')

    def test_delete_current_line_returns_deleted_text(self):
        """Test that delete_current_line returns the deleted line."""
        text = Text("Line 1\nLine 2\nLine 3")
        text.goto(Position(1, 0))

        deleted = text.delete_current_line()

        assert "Line 2" in deleted
        assert "Line 2" not in str(text)

    def test_insert_line_below_method_exists(self):
        """Test that Text has insert_line_below method."""
        text = Text("Line 1")
        assert hasattr(text, 'insert_line_below')

    def test_insert_line_below_creates_new_line(self):
        """Test that insert_line_below creates empty line below cursor."""
        text = Text("Line 1\nLine 2")
        text.goto(Position(0, 0))
        original_lines = len(text._text_lines)

        text.insert_line_below()

        # Should have one more line
        assert len(text._text_lines) == original_lines + 1
        # Cursor should be on new line
        assert text.line_ptr == 1

    def test_insert_line_above_method_exists(self):
        """Test that Text has insert_line_above method."""
        text = Text("Line 1")
        assert hasattr(text, 'insert_line_above')

    def test_insert_line_above_creates_new_line(self):
        """Test that insert_line_above creates empty line above cursor."""
        text = Text("Line 1\nLine 2")
        text.goto(Position(1, 0))  # Line 2
        original_lines = len(text._text_lines)

        text.insert_line_above()

        # Should have one more line
        assert len(text._text_lines) == original_lines + 1
        # Cursor should be on new line (still index 1)
        assert text.line_ptr == 1

    def test_join_with_next_line_method_exists(self):
        """Test that Text has join_with_next_line method."""
        text = Text("Line 1")
        assert hasattr(text, 'join_with_next_line')

    def test_join_with_next_line_joins_lines(self):
        """Test that join_with_next_line joins current and next line."""
        text = Text("Hello\nWorld")
        text.goto(Position(0, 0))

        text.join_with_next_line()

        # Should have one line now
        text_str = str(text)
        assert "Hello World" in text_str or "Hello World" in text_str

    def test_delete_to_end_of_line_method_exists(self):
        """Test that Text has delete_to_end_of_line method."""
        text = Text("Hello World")
        assert hasattr(text, 'delete_to_end_of_line')

    def test_delete_to_end_of_line_deletes_correctly(self):
        """Test that delete_to_end_of_line deletes from cursor to end."""
        text = Text("Hello World")
        text.goto(Position(0, 6))  # After "Hello "

        deleted = text.delete_to_end_of_line()

        assert "World" in deleted
        assert str(text).startswith("Hello ")
        assert "World" not in str(text)


class TestEdgeCases:
    """Test edge cases for new vim commands."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_dd_on_empty_text(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'dd' on empty text doesn't crash."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.enter_command_mode()

        # Press 'dd' on empty text
        await workspace.handle_keypress(ord('d'))
        await workspace.handle_keypress(ord('d'))

        # Should not crash
        assert workspace.input_mode == INPUT_MODE.COMMAND

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_D_at_start_of_line_deletes_all(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """Test that 'D' at start of line deletes entire line content."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("Hello World")
        workspace.user_box.text.goto(Position(0, 0))
        workspace.enter_command_mode()

        # Press 'D'
        await workspace.handle_keypress(ord('D'))

        # Entire line should be deleted
        text_str = str(workspace.user_box.text).strip()
        assert text_str == ""

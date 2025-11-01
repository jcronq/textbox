"""Tests for paste commands (p/P) and register integration."""

import pytest
from unittest.mock import MagicMock, patch
import curses
from textbox.ui.workspace import InputOutputWorkspace, INPUT_MODE
from textbox.ui.input_manager import AsyncInputManager
from textbox.ui.window import Window
from textbox.core.text import Text, TextLine
from textbox.core.text_segment import TextSegment


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


class TestRegisterManagerIntegration:
    """Test that workspace integrates RegisterManager."""

    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    def test_workspace_has_register_manager(self, mock_curses, mock_inputbox, mock_textbox):
        """Workspace should have register_manager instead of yank_register."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)

        assert hasattr(workspace, 'register_manager')
        assert hasattr(workspace.register_manager, 'get_register')
        assert hasattr(workspace.register_manager, 'yank_to_register')


class TestRegisterPrefixHandling:
    """Test " key for specifying registers."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_quote_key_sets_pending_register(self, mock_curses, mock_inputbox, mock_textbox):
        """Pressing \" in COMMAND mode should set pending register flag."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        # Press " to start register specification
        await workspace.handle_keypress(ord('"'))

        assert workspace._pending_register is not None
        # Should still be in command mode
        assert workspace.input_mode == INPUT_MODE.COMMAND

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_next_key_after_quote_is_register_name(self, mock_curses, mock_inputbox, mock_textbox):
        """After \", next key should be stored as register name."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        # Sequence: " followed by 'a'
        await workspace.handle_keypress(ord('"'))
        await workspace.handle_keypress(ord('a'))

        # _pending_register should be set to 'a'
        assert workspace._pending_register == 'a'


class TestYankToRegister:
    """Test yanking to specific registers."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_yy_yanks_to_unnamed_register(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """yy in COMMAND mode should yank line to unnamed register."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        # Set up text in user box using edit mode
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("test line")

        # Press 'yy' to yank line
        await workspace.handle_keypress(ord('y'))
        await workspace.handle_keypress(ord('y'))

        # Should be in unnamed register
        assert workspace.register_manager.get_register('"') == "test line"

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_quote_a_yy_yanks_to_register_a(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """\"ayy should yank line to register a."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        # Set up text using edit mode
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("test line for register a")

        # Sequence: "ayy
        await workspace.handle_keypress(ord('"'))
        await workspace.handle_keypress(ord('a'))
        await workspace.handle_keypress(ord('y'))
        await workspace.handle_keypress(ord('y'))

        # Should be in register a
        assert workspace.register_manager.get_register('a') == "test line for register a"
        # And in register 0 (most recent yank)
        assert workspace.register_manager.get_register('0') == "test line for register a"

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_visual_yank_to_register(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """In visual mode, yank selection to unnamed register."""
        from textbox.utils.box_types import Position
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        # Set up text in edit mode first
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("hello world")
        workspace.user_box.text.goto(Position(0, 0))

        # Enter visual mode (properly initializes selection)
        await workspace.handle_keypress(ord('v'))

        # Move cursor to select text (e.g., select "hello" - 5 characters)
        # Selection runs from position 0 to position 5
        workspace.user_box.text.goto(Position(0, 5))

        # Yank the selection with 'y'
        await workspace.handle_keypress(ord('y'))

        # Visual yank should go to unnamed register
        yanked = workspace.register_manager.get_register('"')
        assert yanked == "hello"  # Should have yanked "hello"


class TestPasteAfter:
    """Test 'p' command (paste after cursor)."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_p_pastes_from_unnamed_register(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """p should paste from unnamed register after cursor."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        # Manually set register content
        workspace.register_manager.yank_to_register(None, "pasted")

        # Set cursor position
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("ab")
        workspace.user_box.text.to_start_of_line()

        # Press 'p' to paste after cursor
        await workspace.handle_keypress(ord('p'))

        # Should paste "pasted" after 'a'
        result = str(workspace.user_box.text)
        assert "pasted" in result

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_quote_a_p_pastes_from_register_a(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """\"ap should paste from register a."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        # Set up registers
        workspace.register_manager.yank_to_register('a', "from_a")
        workspace.register_manager.yank_to_register(None, "from_unnamed")

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("start")

        # Paste from register a: "ap
        await workspace.handle_keypress(ord('"'))
        await workspace.handle_keypress(ord('a'))
        await workspace.handle_keypress(ord('p'))

        result = str(workspace.user_box.text)
        assert "from_a" in result

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_p_inserts_after_current_position(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """p should insert content after current cursor position."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        workspace.register_manager.yank_to_register(None, "X")
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("abc")
        workspace.user_box.text.to_start_of_line()  # At 'a'

        await workspace.handle_keypress(ord('p'))

        # Should insert X after 'a': "aXbc"
        result = str(workspace.user_box.text)
        assert result == "aXbc"


class TestPasteBefore:
    """Test 'P' command (paste before cursor)."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_P_pastes_from_unnamed_register(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """P should paste from unnamed register before cursor."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        workspace.register_manager.yank_to_register(None, "pasted")
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("ab")
        workspace.user_box.text.to_start_of_line()

        # Press 'P' to paste before cursor
        await workspace.handle_keypress(ord('P'))

        result = str(workspace.user_box.text)
        assert "pasted" in result

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_quote_b_P_pastes_from_register_b(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """\"bP should paste from register b before cursor."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        workspace.register_manager.yank_to_register('b', "from_b")
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("start")

        # Paste from register b: "bP
        await workspace.handle_keypress(ord('"'))
        await workspace.handle_keypress(ord('b'))
        await workspace.handle_keypress(ord('P'))

        result = str(workspace.user_box.text)
        assert "from_b" in result

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_P_inserts_before_current_position(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """P should insert content before current cursor position."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        workspace.register_manager.yank_to_register(None, "X")
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("abc")
        workspace.user_box.text.to_start_of_line()  # At 'a'

        await workspace.handle_keypress(ord('P'))

        # Should insert X before 'a': "Xabc"
        result = str(workspace.user_box.text)
        assert result == "Xabc"


class TestDeleteToRegister:
    """Test that delete operations use registers."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_dd_deletes_to_unnamed_register(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """dd should delete line to unnamed register."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("line to delete")

        # Press 'dd' to delete line
        await workspace.handle_keypress(ord('d'))
        await workspace.handle_keypress(ord('d'))

        # Should be in unnamed register and register 1
        assert workspace.register_manager.get_register('"') == "line to delete"
        assert workspace.register_manager.get_register('1') == "line to delete"

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_quote_c_dd_deletes_to_register_c(self, mock_workspace_curses, mock_textbox_curses, mock_window_curses):
        """\"cdd should delete line to register c."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("line for register c")

        # Sequence: "cdd
        await workspace.handle_keypress(ord('"'))
        await workspace.handle_keypress(ord('c'))
        await workspace.handle_keypress(ord('d'))
        await workspace.handle_keypress(ord('d'))

        # Should be in register c
        assert workspace.register_manager.get_register('c') == "line for register c"
        # Should NOT be in register 1 (named delete doesn't affect numbered)
        assert workspace.register_manager.get_register('1') == ""


class TestRegisterClearAfterOperation:
    """Test that pending register is cleared after use."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_pending_register_cleared_after_yank(self, mock_curses, mock_inputbox, mock_textbox):
        """After yanking with a register, pending register should be cleared."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("test")

        # Yank with register: "ayy
        await workspace.handle_keypress(ord('"'))
        await workspace.handle_keypress(ord('a'))
        await workspace.handle_keypress(ord('y'))
        await workspace.handle_keypress(ord('y'))

        # Pending register should be cleared
        assert workspace._pending_register is None

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.TextBox')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.curses')
    async def test_pending_register_cleared_after_paste(self, mock_curses, mock_inputbox, mock_textbox):
        """After pasting with a register, pending register should be cleared."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_mgr = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr)
        workspace.enter_command_mode()

        workspace.register_manager.yank_to_register('a', "content")
        workspace.user_box.text.edit_mode = True
        workspace.user_box.text.insert("test")

        # Paste with register: "ap
        await workspace.handle_keypress(ord('"'))
        await workspace.handle_keypress(ord('a'))
        await workspace.handle_keypress(ord('p'))

        # Pending register should be cleared
        assert workspace._pending_register is None

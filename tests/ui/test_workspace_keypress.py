"""
Tests for InputOutputWorkspace keypress handling.

Tests key handling in different modes (INSERT, COMMAND, READ_ONLY, etc.).
Target: Improve workspace.py coverage from 32% to 70%.
"""

import pytest
from unittest.mock import MagicMock, patch
import curses
from textbox.ui.workspace import InputOutputWorkspace, INPUT_MODE
from textbox.ui.window import Window
from textbox.ui.input_manager import AsyncInputManager
from textbox.utils.signals import WindowQuit


class TestKeypressInsertMode:
    """Test keypress handling in INSERT mode."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_arrow_key_up_in_insert_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that up arrow moves cursor up in INSERT mode."""
        mock_curses.KEY_UP = curses.KEY_UP
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_insert_mode()

        await workspace.handle_keypress(curses.KEY_UP)

        workspace.focused_box.cursor_up.assert_called_once()

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_arrow_key_down_in_insert_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that down arrow moves cursor down in INSERT mode."""
        mock_curses.KEY_DOWN = curses.KEY_DOWN
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_insert_mode()

        await workspace.handle_keypress(curses.KEY_DOWN)

        workspace.focused_box.cursor_down.assert_called_once()

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_escape_key_enters_command_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that Escape key switches to COMMAND mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_insert_mode()
        assert workspace.input_mode == INPUT_MODE.INSERT

        await workspace.handle_keypress(27)  # ESC key

        assert workspace.input_mode == INPUT_MODE.COMMAND

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_backspace_key_in_insert_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that backspace deletes character."""
        mock_curses.KEY_BACKSPACE = curses.KEY_BACKSPACE
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_insert_mode()

        await workspace.handle_keypress(curses.KEY_BACKSPACE)

        workspace.focused_box.handle_backspace.assert_called_once()

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_regular_character_in_insert_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that regular characters are inserted."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_insert_mode()

        await workspace.handle_keypress(ord('a'))

        workspace.focused_box.insert_character_at_cursor.assert_called_once_with('a')

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_regular_character_in_replace_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that regular characters replace in REPLACE mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_replace_mode()

        await workspace.handle_keypress(ord('b'))

        workspace.focused_box.replace_character_at_cursor.assert_called_once_with('b')


class TestKeypressCommandMode:
    """Test keypress handling in COMMAND mode."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_j_key_moves_cursor_down(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that 'j' moves cursor down in COMMAND mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_mode()

        await workspace.handle_keypress(ord('j'))

        workspace.focused_box.cursor_down.assert_called_once()

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_k_key_moves_cursor_up(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that 'k' moves cursor up in COMMAND mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_mode()

        await workspace.handle_keypress(ord('k'))

        workspace.focused_box.cursor_up.assert_called_once()

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_h_key_moves_cursor_left(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that 'h' moves cursor left in COMMAND mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_mode()

        await workspace.handle_keypress(ord('h'))

        workspace.focused_box.cursor_left.assert_called_once()

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_l_key_moves_cursor_right(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that 'l' moves cursor right in COMMAND mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_mode()

        await workspace.handle_keypress(ord('l'))

        workspace.focused_box.cursor_right.assert_called_once()

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_i_key_enters_insert_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that 'i' enters INSERT mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_mode()

        await workspace.handle_keypress(ord('i'))

        assert workspace.input_mode == INPUT_MODE.INSERT

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_a_key_enters_insert_mode_append(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that 'a' enters INSERT mode with append."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_mode()

        await workspace.handle_keypress(ord('a'))

        assert workspace.input_mode == INPUT_MODE.INSERT

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_colon_enters_command_entry_mode(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that ':' enters COMMAND_ENTRY mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_command_mode()

        await workspace.handle_keypress(ord(':'))

        assert workspace.input_mode == INPUT_MODE.COMMAND_ENTRY


class TestKeypressReadOnlyMode:
    """Test keypress handling in READ_ONLY mode."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_tab_key_cycles_focus(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that tab cycles focus in READ_ONLY mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)
        workspace.enter_reading_mode()

        # Initially focused on output_box
        assert workspace.focused_box == workspace.output_box

        await workspace.handle_keypress(ord('\t'))

        # Should switch to user_box
        assert workspace.focused_box == workspace.user_box


class TestSubmitAndCommandExecution:
    """Test submit and command execution."""

    @pytest.mark.asyncio
    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    async def test_submit_calls_callback(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that submit calls the registered callback."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        callback = MagicMock()
        workspace.set_submit_callback(callback)

        # Mock the focused_box text to have content
        workspace.focused_box.text.__len__.return_value = 5
        workspace.focused_box.text.copy.return_value = MagicMock()

        workspace.enter_insert_mode()
        await workspace.handle_keypress(ord('\n'))  # Enter key

        # Callback should be called
        callback.assert_called_once()

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_q_command_raises_window_quit(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that 'q' command raises WindowQuit."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # Simulate entering command ':q'
        with pytest.raises(WindowQuit):
            workspace.execute_command("q")

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_custom_command_calls_callback(self, mock_textbox, mock_inputbox, mock_curses):
        """Test that custom commands call the command callback."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        callback = MagicMock()
        workspace.set_command_callback(callback)

        workspace.execute_command("custom arg1 arg2")

        callback.assert_called_once_with("custom arg1 arg2")


class TestCycleFocus:
    """Test focus cycling."""

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_cycle_focus_from_user_to_output(self, mock_textbox, mock_inputbox, mock_curses):
        """Test cycling focus from user_box to output_box."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # Start with user_box focused
        workspace.focused_box = workspace.user_box

        workspace.cycle_focus()

        # Should switch to output_box
        assert workspace.focused_box == workspace.output_box

    @patch('textbox.ui.workspace.curses')
    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_cycle_focus_from_output_to_user(self, mock_textbox, mock_inputbox, mock_curses):
        """Test cycling focus from output_box to user_box."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # Start with output_box focused
        workspace.focused_box = workspace.output_box

        workspace.cycle_focus()

        # Should switch to user_box
        assert workspace.focused_box == workspace.user_box

"""
Tests for InputOutputWorkspace initialization and setup.

Tests workspace creation, box initialization, and initial state.
Target: Improve workspace.py coverage from 14% to 70%.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from textbox.ui.workspace import InputOutputWorkspace, INPUT_MODE
from textbox.ui.window import Window
from textbox.ui.input_manager import AsyncInputManager
from textbox.utils.box_types import BoundingBox


class TestWorkspaceCreation:
    """Test InputOutputWorkspace instantiation and initialization."""

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_workspace_creates_successfully(self, mock_textbox, mock_inputbox):
        """Test that workspace can be instantiated."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        assert workspace is not None
        assert isinstance(workspace, InputOutputWorkspace)

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_workspace_stores_window_reference(self, mock_textbox, mock_inputbox):
        """Test that workspace stores window reference."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        assert workspace.main_window == mock_window

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_workspace_registers_with_input_manager(self, mock_textbox, mock_inputbox):
        """Test that workspace registers handlers with input manager."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # Workspace should set on_keypress and redraw on the input manager
        assert mock_input_manager.on_keypress == workspace.handle_keypress
        assert mock_input_manager.redraw == workspace.redraw

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_workspace_creates_user_box(self, mock_textbox, mock_inputbox):
        """Test that workspace creates user input box."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # InputBox should be called for user_box
        assert mock_inputbox.called
        assert workspace.user_box is not None

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_workspace_creates_output_box(self, mock_textbox, mock_inputbox):
        """Test that workspace creates output display box."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # TextBox should be called for output_box
        assert mock_textbox.called
        assert workspace.output_box is not None

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_workspace_creates_command_box(self, mock_textbox, mock_inputbox):
        """Test that workspace creates command line box."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # InputBox should be called for command_box
        assert workspace.command_box is not None

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_workspace_initial_mode_is_command(self, mock_textbox, mock_inputbox):
        """Test that workspace starts in COMMAND mode."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        assert workspace.input_mode == INPUT_MODE.COMMAND

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_workspace_registers_keypress_handler(self, mock_textbox, mock_inputbox):
        """Test that workspace registers keypress handler with input manager."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # Should set on_keypress attribute to handle_keypress method
        assert mock_input_manager.on_keypress == workspace.handle_keypress


class TestWorkspaceBoundingBoxes:
    """Test workspace bounding box calculations and layout."""

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_workspace_calculates_bounding_boxes(self, mock_textbox, mock_inputbox):
        """Test that workspace calculates bounding boxes for all components."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # Should have bounding boxes for all three boxes
        assert workspace.user_bounding_box is not None
        assert workspace.output_bounding_box is not None
        assert workspace.command_bounding_box is not None

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_bounding_boxes_fill_window(self, mock_textbox, mock_inputbox):
        """Test that bounding boxes properly divide the window space."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        # All boxes should fit within window dimensions
        if workspace.user_bounding_box:
            assert workspace.user_bounding_box.width <= mock_window.width
        if workspace.output_bounding_box:
            assert workspace.output_bounding_box.width <= mock_window.width
        if workspace.command_bounding_box:
            assert workspace.command_bounding_box.width <= mock_window.width


class TestWorkspaceCallbacks:
    """Test workspace callback registration and management."""

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_set_submit_callback_stores_callback(self, mock_textbox, mock_inputbox):
        """Test that set_submit_callback stores the callback."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        test_callback = Mock()
        workspace.set_submit_callback(test_callback)

        assert workspace._submit_callback == test_callback

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_set_command_callback_stores_callback(self, mock_textbox, mock_inputbox):
        """Test that set_command_callback stores the callback."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        test_callback = Mock()
        workspace.set_command_callback(test_callback)

        assert workspace._command_callback == test_callback

    @patch('textbox.ui.workspace.InputBox')
    @patch('textbox.ui.workspace.TextBox')
    def test_callbacks_can_be_replaced(self, mock_textbox, mock_inputbox):
        """Test that callbacks can be replaced with new ones."""
        mock_window = MagicMock(spec=Window)
        mock_window.height = 24
        mock_window.width = 80
        mock_input_manager = MagicMock(spec=AsyncInputManager)

        workspace = InputOutputWorkspace(mock_window, mock_input_manager)

        callback1 = Mock()
        callback2 = Mock()

        workspace.set_submit_callback(callback1)
        assert workspace._submit_callback == callback1

        workspace.set_submit_callback(callback2)
        assert workspace._submit_callback == callback2

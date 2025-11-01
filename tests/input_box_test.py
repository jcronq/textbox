import pytest
from unittest.mock import Mock, MagicMock
from textbox.ui.input_box import InputBox
from textbox.core.text import Text


def test_edit_mode_getter_no_side_effect():
    """Test that reading edit_mode property doesn't change its value"""
    # Create a mock window and parent window to avoid needing curses
    mock_parent_window = Mock()
    mock_window = Mock()
    mock_window.height = 10
    mock_window.width = 80
    mock_parent_window.create_new_window = Mock(return_value=mock_window)

    # Create mock BoundingBox
    mock_box = Mock()

    # Create InputBox
    input_box = InputBox(
        name="test",
        parent_window=mock_parent_window,
        box=mock_box,
        top_to_bottom=True
    )

    # Set edit mode to False
    input_box.edit_mode = False

    # Reading edit_mode should not change it
    assert input_box.edit_mode == False
    assert input_box.edit_mode == False  # Read again, should still be False
    assert input_box.text.edit_mode == False

    # Set edit mode to True
    input_box.edit_mode = True

    # Reading edit_mode should not change it
    assert input_box.edit_mode == True
    assert input_box.edit_mode == True  # Read again, should still be True
    assert input_box.text.edit_mode == True

    # Verify that reading doesn't set it to True when it's False
    input_box.edit_mode = False
    for _ in range(5):
        mode = input_box.edit_mode
        assert mode == False, "Reading edit_mode should not change its value"


def test_edit_mode_setter():
    """Test that edit_mode setter works correctly"""
    # Create a mock window and parent window
    mock_parent_window = Mock()
    mock_window = Mock()
    mock_window.height = 10
    mock_window.width = 80
    mock_parent_window.create_new_window = Mock(return_value=mock_window)

    mock_box = Mock()

    input_box = InputBox(
        name="test",
        parent_window=mock_parent_window,
        box=mock_box,
        top_to_bottom=True
    )

    # Test setting to True
    input_box.edit_mode = True
    assert input_box.text.edit_mode == True

    # Test setting to False
    input_box.edit_mode = False
    assert input_box.text.edit_mode == False

    # Test toggling
    input_box.edit_mode = True
    assert input_box.text.edit_mode == True
    input_box.edit_mode = False
    assert input_box.text.edit_mode == False

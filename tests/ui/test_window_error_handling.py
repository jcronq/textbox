"""
Tests for Window error handling improvements.

Following TDD: Write tests first, then implement the improved error handling.
These tests describe the INTENDED behavior for v0.2.0.
"""

import pytest
from unittest.mock import MagicMock, patch
import curses
from textbox.ui.window import Window
from textbox.utils.box_types import BoundingBox, Position, Dimensions


class TestWindowResizeValidation:
    """Test Window.resize() validates dimensions and provides helpful errors."""

    @patch('textbox.ui.window.curses')
    def test_resize_with_negative_height_raises_error(self, mock_curses):
        """Test that negative height raises ValueError with helpful message."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_stdscr = MagicMock()
        window = Window(mock_stdscr)

        with pytest.raises(ValueError) as exc_info:
            window.resize(BoundingBox(0, 0, -5, 80))

        error_msg = str(exc_info.value).lower()
        assert "positive" in error_msg or "negative" in error_msg or "invalid" in error_msg
        assert "height" in error_msg

    @patch('textbox.ui.window.curses')
    def test_resize_with_negative_width_raises_error(self, mock_curses):
        """Test that negative width raises ValueError."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_stdscr = MagicMock()
        window = Window(mock_stdscr)

        with pytest.raises(ValueError) as exc_info:
            window.resize(BoundingBox(0, 0, 24, -10))

        error_msg = str(exc_info.value).lower()
        assert "positive" in error_msg or "negative" in error_msg or "invalid" in error_msg
        assert "width" in error_msg

    @patch('textbox.ui.window.curses')
    def test_resize_with_zero_dimensions_raises_error(self, mock_curses):
        """Test that zero dimensions raise ValueError."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_stdscr = MagicMock()
        window = Window(mock_stdscr)

        with pytest.raises(ValueError) as exc_info:
            window.resize(BoundingBox(0, 0, 0, 0))

        error_msg = str(exc_info.value).lower()
        assert "must be positive" in error_msg or "greater than zero" in error_msg


class TestWindowCursesErrorHandling:
    """Test that curses errors are caught and logged with context."""

    @patch('textbox.ui.window.logger')
    @patch('textbox.ui.window.curses')
    def test_addstr_curses_error_is_logged_with_context(self, mock_curses, mock_logger):
        """Test that curses errors in addstr are logged with position context."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_curses.error = curses.error  # Use real error class

        mock_stdscr = MagicMock()
        # Use real curses.error
        mock_stdscr.addstr.side_effect = curses.error("write failed")
        mock_stdscr.getyx.return_value = (0, 0)

        window = Window(mock_stdscr)

        # Should not raise, but should log
        window.addstr("test", position=Position(5, 10))

        # Verify logging was called with context
        assert mock_logger.debug.called
        # Check that position was included in log message
        log_calls = str(mock_logger.debug.call_args_list)
        assert ("5" in log_calls and "10" in log_calls) or "position" in log_calls.lower()

    @patch('textbox.ui.window.logger')
    @patch('textbox.ui.window.curses')
    def test_addch_curses_error_is_logged_with_context(self, mock_curses, mock_logger):
        """Test that curses errors in addch are logged with context."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_curses.error = curses.error  # Use real error class

        mock_stdscr = MagicMock()
        # Use real curses.error
        mock_stdscr.addch.side_effect = curses.error("write failed")
        mock_stdscr.getyx.return_value = (0, 0)

        window = Window(mock_stdscr)

        # Should not raise
        window.addch('X', position=Position(23, 79))

        # Should have logged with context
        assert mock_logger.debug.called


class TestWindowErrorMessages:
    """Test that error messages are helpful and actionable."""

    @patch('textbox.ui.window.curses')
    def test_resize_error_includes_current_size(self, mock_curses):
        """Test that resize errors show current window size."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_stdscr = MagicMock()
        window = Window(mock_stdscr)

        with pytest.raises(ValueError) as exc_info:
            window.resize(BoundingBox(0, 0, -1, 80))

        error_msg = str(exc_info.value)
        # Should mention current or attempted dimensions
        assert "24" in error_msg or "80" in error_msg or "-1" in error_msg

    @patch('textbox.ui.window.curses')
    def test_resize_error_explains_what_was_wrong(self, mock_curses):
        """Test that resize errors explain what was invalid."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_stdscr = MagicMock()
        window = Window(mock_stdscr)

        with pytest.raises(ValueError) as exc_info:
            window.resize(BoundingBox(5, 10, -3, 50))

        error_msg = str(exc_info.value).lower()
        # Should explain the problem
        assert "height" in error_msg or "dimension" in error_msg
        assert "positive" in error_msg or "negative" in error_msg or "invalid" in error_msg


class TestWindowDrawingErrorRecovery:
    """Test that drawing errors don't crash the application."""

    @patch('textbox.ui.window.curses')
    def test_drawing_at_edge_doesnt_crash(self, mock_curses):
        """Test that drawing at window edge is handled gracefully."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_curses.error = curses.error  # Use real error class

        mock_stdscr = MagicMock()
        # Use real curses.error
        mock_stdscr.addch.side_effect = curses.error("cursor moved beyond window")
        mock_stdscr.getyx.return_value = (0, 0)

        window = Window(mock_stdscr)

        # Should not crash
        window.addch('X', position=Position(23, 79))
        # Position 24,0 will fail validation before calling curses, so no crash

    @patch('textbox.ui.window.curses')
    def test_multiple_drawing_errors_are_handled(self, mock_curses):
        """Test that multiple curses errors don't cause issues."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_curses.error = curses.error  # Use real error class

        mock_stdscr = MagicMock()
        # Use real curses.error
        mock_stdscr.addstr.side_effect = curses.error("error")
        mock_stdscr.getyx.return_value = (0, 0)

        window = Window(mock_stdscr)

        # Should handle multiple errors
        for i in range(5):
            window.addstr(f"Line {i}", position=Position(i, 0))

        # Should still be functional
        assert window.width == 80
        assert window.height == 24

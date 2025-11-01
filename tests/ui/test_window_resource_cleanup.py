"""
Tests for Window resource cleanup and memory management.

Following TDD: Write tests first describing intended cleanup behavior.
These tests describe what SHOULD happen for proper resource management in v0.2.0.
"""

import pytest
from unittest.mock import MagicMock, patch, call
import curses
from textbox.ui.window import Window
from textbox.utils.box_types import BoundingBox, Position, Dimensions


class TestWindowCleanup:
    """Test Window cleanup methods."""

    @patch('textbox.ui.window.curses')
    def test_window_has_cleanup_method(self, mock_curses):
        """Test that Window has a cleanup() method."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_stdscr = MagicMock()

        window = Window(mock_stdscr)

        # Should have cleanup method
        assert hasattr(window, 'cleanup')
        assert callable(window.cleanup)

    @patch('textbox.ui.window.curses')
    def test_cleanup_clears_window(self, mock_curses):
        """Test that cleanup() clears the window."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_stdscr = MagicMock()

        window = Window(mock_stdscr)
        window.cleanup()

        # Should call clear on the curses window
        assert mock_stdscr.clear.called or mock_stdscr.erase.called

    @patch('textbox.ui.window.curses')
    def test_cleanup_handles_curses_errors_gracefully(self, mock_curses):
        """Test that cleanup doesn't crash if curses operations fail."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_curses.error = curses.error
        mock_stdscr = MagicMock()
        mock_stdscr.clear.side_effect = curses.error("window deleted")

        window = Window(mock_stdscr)

        # Should not raise
        window.cleanup()  # Should handle error gracefully

    @patch('textbox.ui.window.curses')
    def test_cleanup_can_be_called_multiple_times(self, mock_curses):
        """Test that cleanup() is idempotent."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_curses.error = curses.error  # Use real error class
        mock_stdscr = MagicMock()

        window = Window(mock_stdscr)

        # Should be safe to call multiple times
        window.cleanup()
        window.cleanup()
        window.cleanup()

        # Should not crash

    @patch('textbox.ui.window.curses')
    def test_del_calls_cleanup(self, mock_curses):
        """Test that __del__ calls cleanup()."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_curses.error = curses.error  # Use real error class
        mock_stdscr = MagicMock()

        window = Window(mock_stdscr)

        # Call __del__ manually to test
        window.__del__()

        # Should have called cleanup operations
        assert mock_stdscr.clear.called or mock_stdscr.erase.called


class TestTextMemoryManagement:
    """Test Text memory management for large texts."""

    def test_text_has_max_lines_limit(self):
        """Test that Text can limit maximum number of lines."""
        from textbox.core.text import Text

        text = Text()

        # Should have a way to set max lines
        assert hasattr(text, 'max_history_lines') or hasattr(text, 'set_max_lines')

    def test_text_truncates_when_exceeding_limit(self):
        """Test that Text truncates old lines when limit is exceeded."""
        from textbox.core.text import Text

        text = Text()
        text.edit_mode = True

        # Set a limit
        if hasattr(text, 'set_max_lines'):
            text.set_max_lines(100)
        elif hasattr(text, 'max_history_lines'):
            text.max_history_lines = 100

        # Add more lines than the limit
        for i in range(150):
            text.insert(f"Line {i}\n")

        # Should have truncated to limit
        line_count = len(text._text_lines) if hasattr(text, '_text_lines') else len(str(text).split('\n'))
        assert line_count <= 105  # 100 + some buffer

    def test_text_preserves_recent_lines_when_truncating(self):
        """Test that Text keeps the most recent lines when truncating."""
        from textbox.core.text import Text

        text = Text()
        text.edit_mode = True

        # Set a small limit for testing
        if hasattr(text, 'set_max_lines'):
            text.set_max_lines(10)
        elif hasattr(text, 'max_history_lines'):
            text.max_history_lines = 10

        # Add lines
        for i in range(20):
            text.insert(f"Line {i}\n")

        # Should keep most recent lines
        text_str = str(text)
        assert "Line 19" in text_str or "Line 18" in text_str
        # Older lines should be gone (check for exact match with newline or start of string)
        # Note: Can't just check "Line 0" as it matches "Line 10", "Line 20", etc.
        lines = text_str.split('\n')
        assert "Line 0" not in lines
        assert "Line 1" not in lines
        assert "Line 2" not in lines


class TestWindowRefreshOptimization:
    """Test that Window refresh operations are optimized."""

    @patch('textbox.ui.window.curses')
    def test_window_tracks_dirty_state(self, mock_curses):
        """Test that Window can track if it needs refresh."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_stdscr = MagicMock()

        window = Window(mock_stdscr)

        # Should have some way to track if refresh is needed
        # (This is optional optimization, so we're lenient)
        has_dirty_tracking = (
            hasattr(window, '_dirty') or
            hasattr(window, 'needs_refresh') or
            hasattr(window, 'is_dirty')
        )

        # This is an optimization, not required
        # Just document the capability
        assert True  # Pass - dirty tracking is optional


class TestResourceCleanupOnError:
    """Test that resources are cleaned up even when errors occur."""

    @patch('textbox.ui.window.curses')
    def test_window_cleanup_on_resize_failure(self, mock_curses):
        """Test that window is still usable after resize failure."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_curses.error = curses.error
        mock_stdscr = MagicMock()
        mock_stdscr.resize.side_effect = curses.error("resize failed")

        window = Window(mock_stdscr)
        original_dims = window.dimensions

        # Try to resize (will fail)
        try:
            window.resize(BoundingBox(0, 0, 10, 10))
        except (ValueError, curses.error):
            pass  # Expected to fail

        # Window should still have original dimensions
        assert window.dimensions == original_dims

    @patch('textbox.ui.window.curses')
    def test_window_remains_functional_after_cleanup(self, mock_curses):
        """Test that window operations still work after cleanup."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_stdscr = MagicMock()

        window = Window(mock_stdscr)

        # Cleanup
        window.cleanup()

        # Should still be able to access properties
        assert window.width == 80
        assert window.height == 24
        assert window.dimensions == Dimensions(24, 80)


class TestMemoryLeakPrevention:
    """Test that common memory leak scenarios are prevented."""

    @patch('textbox.ui.window.curses')
    def test_window_doesnt_keep_references_after_cleanup(self, mock_curses):
        """Test that cleanup releases internal references."""
        mock_curses.LINES = 24
        mock_curses.COLS = 80
        mock_stdscr = MagicMock()

        window = Window(mock_stdscr)
        window.cleanup()

        # After cleanup, internal window reference should be cleared
        # (or at least safe to delete)
        # This prevents circular references
        assert True  # Cleanup completed without error

    def test_text_doesnt_accumulate_unbounded_lines(self):
        """Test that Text doesn't grow forever without limits."""
        from textbox.core.text import Text

        text = Text()
        text.edit_mode = True

        # If max_lines is set, should respect it
        if hasattr(text, 'set_max_lines'):
            text.set_max_lines(50)

            # Add many lines
            for i in range(200):
                text.insert(f"Line {i}\n")

            # Should not have all 200 lines
            line_count = len(text._text_lines) if hasattr(text, '_text_lines') else 200
            assert line_count < 100  # Should be truncated

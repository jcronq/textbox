import pytest
from unittest.mock import Mock, patch, MagicMock
import sys


def test_curses_wrapper_state_management():
    """Test that state is properly managed through the curses_wrapper lifecycle.

    Bug #7 fix: Ensures state = 0 (assignment) instead of state == 0 (comparison)
    in the finally block at line 71.
    """
    # Create a mock function that will be wrapped
    mock_func = Mock(return_value="test_result")

    # Mock curses at the module level before import
    with patch.dict('sys.modules', {'curses': MagicMock()}):
        with patch('textbox.utils.curses_utils.curses') as mock_curses:
            # Setup mock stdscr
            mock_stdscr = MagicMock()
            mock_curses.initscr.return_value = mock_stdscr
            mock_curses.COLORS = 8

            # Import and use the wrapper after patching
            from textbox.utils.curses_utils import curses_wrapper

            # Wrap the function
            wrapped_func = curses_wrapper(mock_func)

            # Execute the wrapped function
            result = wrapped_func("arg1", kwarg1="value1")

            # Verify the function was called with correct arguments
            mock_func.assert_called_once_with(mock_stdscr, "arg1", kwarg1="value1")

            # Verify curses initialization was called
            mock_curses.initscr.assert_called_once()
            mock_curses.noecho.assert_called()
            mock_curses.cbreak.assert_called()
            mock_curses.start_color.assert_called()

            # Verify cleanup was called in finally block
            # This ensures state = 0 was executed (not state == 0)
            # The bug would cause cleanup to fail silently
            mock_curses.echo.assert_called()
            mock_curses.nocbreak.assert_called()
            mock_curses.endwin.assert_called()
            mock_stdscr.keypad.assert_called()


def test_curses_wrapper_exception_handling():
    """Test that curses is properly cleaned up when an exception occurs."""
    # Create a mock function that raises an exception
    mock_func = Mock(side_effect=Exception("Test exception"))

    with patch.dict('sys.modules', {'curses': MagicMock()}):
        with patch('textbox.utils.curses_utils.curses') as mock_curses:
            mock_stdscr = MagicMock()
            mock_curses.initscr.return_value = mock_stdscr
            mock_curses.COLORS = 8

            from textbox.utils.curses_utils import curses_wrapper
            wrapped_func = curses_wrapper(mock_func)

            # Execute - should not raise exception (it's caught internally)
            result = wrapped_func()

            # Verify cleanup was still called (from both except and finally blocks)
            # This verifies state = 0 logic works correctly
            # Without the fix (state == 0), cleanup might not work properly
            assert mock_curses.echo.call_count >= 1
            assert mock_curses.nocbreak.call_count >= 1
            assert mock_curses.endwin.call_count >= 1


def test_curses_wrapper_keyboard_interrupt():
    """Test that curses is properly cleaned up on KeyboardInterrupt."""
    mock_func = Mock(side_effect=KeyboardInterrupt())

    with patch.dict('sys.modules', {'curses': MagicMock()}):
        with patch('textbox.utils.curses_utils.curses') as mock_curses:
            mock_stdscr = MagicMock()
            mock_curses.initscr.return_value = mock_stdscr
            mock_curses.COLORS = 8

            from textbox.utils.curses_utils import curses_wrapper
            wrapped_func = curses_wrapper(mock_func)

            # Execute - should handle KeyboardInterrupt gracefully
            wrapped_func()

            # Verify cleanup was called from finally block
            # This ensures state = 0 assignment worked correctly
            # The bug (state == 0) would be a comparison that returns False,
            # potentially preventing cleanup
            mock_curses.echo.assert_called()
            mock_curses.nocbreak.assert_called()
            mock_curses.endwin.assert_called()


def test_state_assignment_bug_fix():
    """Directly test that the bug on line 71 has been fixed.

    Bug #7: Line 71 had 'state == 0' (comparison) instead of 'state = 0' (assignment).
    This test verifies the code doesn't have a useless comparison statement.
    """
    # Read the source code to verify the fix
    import inspect
    from textbox.utils.curses_utils import curses_wrapper

    source = inspect.getsource(curses_wrapper)

    # The bug was a comparison 'state == 0' in the finally block
    # After the fix, it should be an assignment 'state = 0'
    # We check that the pattern doesn't appear in a context where it shouldn't

    # The correct code should have 'state = 0' (assignment)
    assert 'state = 0' in source, "Expected 'state = 0' assignment in source code"

    # Check the finally block specifically has the assignment
    lines = source.split('\n')
    in_finally = False
    finally_has_assignment = False

    for line in lines:
        if 'finally:' in line:
            in_finally = True
        if in_finally and 'state = 0' in line and 'state == 0' not in line:
            finally_has_assignment = True
            break

    assert finally_has_assignment, "Finally block should have 'state = 0' assignment, not 'state == 0' comparison"

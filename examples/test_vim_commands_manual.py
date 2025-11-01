"""
Manual test to demonstrate vim commands work correctly.
This script tests the Text class methods directly without workspace/UI mocking issues.
"""

from textbox.core.text import Text
from textbox.utils.box_types import Position


def test_dd_delete_line():
    """Test dd - delete current line."""
    print("Testing dd (delete current line)...")
    text = Text("Line 1\nLine 2\nLine 3")
    text.goto(Position(1, 0))  # Go to Line 2

    deleted = text.delete_current_line()

    assert "Line 2" in deleted
    assert "Line 2" not in str(text)
    assert "Line 1" in str(text)
    assert "Line 3" in str(text)
    print("✓ dd works correctly")


def test_o_open_line_below():
    """Test o - open line below."""
    print("Testing o (open line below)...")
    text = Text("Line 1\nLine 2")
    text.goto(Position(0, 0))  # Go to Line 1

    text.insert_line_below()

    assert len(text._text_lines) == 3
    assert text.line_ptr == 1  # Should be on new line
    assert text.column_ptr == 0  # Should be at start
    print("✓ o works correctly")


def test_O_open_line_above():
    """Test O - open line above."""
    print("Testing O (open line above)...")
    text = Text("Line 1\nLine 2")
    text.goto(Position(1, 0))  # Go to Line 2

    text.insert_line_above()

    assert len(text._text_lines) == 3
    assert text.line_ptr == 1  # Should be on new line
    assert text.column_ptr == 0  # Should be at start
    print("✓ O works correctly")


def test_J_join_lines():
    """Test J - join lines."""
    print("Testing J (join lines)...")
    text = Text("Hello\nWorld")
    text.goto(Position(0, 0))

    text.join_with_next_line()

    text_str = str(text)
    assert "Hello World" in text_str
    assert len(text._text_lines) == 1
    print("✓ J works correctly")


def test_D_delete_to_end():
    """Test D - delete to end of line."""
    print("Testing D (delete to end of line)...")
    text = Text("Hello World")
    text.goto(Position(0, 6))  # After "Hello "

    deleted = text.delete_to_end_of_line()

    assert "World" in deleted
    assert str(text) == "Hello "
    print("✓ D works correctly")


def test_C_change_to_end():
    """Test C - change to end (same as D, but enters insert mode in workspace)."""
    print("Testing C (change to end of line)...")
    text = Text("Hello World")
    text.goto(Position(0, 6))  # After "Hello "

    deleted = text.delete_to_end_of_line()

    assert "World" in deleted
    assert str(text) == "Hello "
    print("✓ C works correctly (delete part)")


def test_cc_change_line():
    """Test cc - change entire line."""
    print("Testing cc (change entire line)...")
    text = Text("Line 1\nLine 2\nLine 3")
    text.goto(Position(1, 3))  # Middle of Line 2

    deleted = text.delete_current_line()

    assert "Line 2" in deleted
    assert "Line 2" not in str(text)
    # Should still have 2 lines (or 3 if empty line added)
    assert len(text._text_lines) >= 2
    print("✓ cc works correctly (delete part)")


if __name__ == "__main__":
    print("=" * 60)
    print("Manual Vim Commands Test")
    print("=" * 60)
    print()

    try:
        test_dd_delete_line()
        test_o_open_line_below()
        test_O_open_line_above()
        test_J_join_lines()
        test_D_delete_to_end()
        test_C_change_to_end()
        test_cc_change_line()

        print()
        print("=" * 60)
        print("All manual tests passed! ✓")
        print("=" * 60)
        print()
        print("Note: Workspace-level commands (A, I) just use existing methods:")
        print("  - A: text.to_end_of_line() + enter_insert_mode(append=True)")
        print("  - I: text.to_start_of_line() + enter_insert_mode()")
        print("  - These work via composition, no new Text methods needed")

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        raise

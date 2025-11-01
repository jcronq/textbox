"""
Tests for Text class input validation.

Tests the new validation logic added in v0.2.0 to ensure helpful error messages.
"""

import pytest
from textbox.core.text import Text
from textbox.utils.box_types import Position


class TestGotoValidation:
    """Test Text.goto() input validation."""

    def test_goto_with_negative_line_raises_error(self):
        """Test that negative line numbers raise ValueError with helpful message."""
        text = Text("Line 1\nLine 2\nLine 3")

        with pytest.raises(ValueError) as exc_info:
            text.goto(Position(-1, 0))

        assert "cannot be negative" in str(exc_info.value).lower()
        assert "0 to 2" in str(exc_info.value)

    def test_goto_with_line_out_of_range_raises_error(self):
        """Test that out-of-range line numbers raise ValueError."""
        text = Text("Line 1\nLine 2")

        with pytest.raises(ValueError) as exc_info:
            text.goto(Position(5, 0))

        assert "out of range" in str(exc_info.value).lower()
        assert "to_last_line" in str(exc_info.value)

    def test_goto_with_negative_column_raises_error(self):
        """Test that negative column numbers raise ValueError."""
        text = Text("Hello World")

        with pytest.raises(ValueError) as exc_info:
            text.goto(Position(0, -1))

        assert "cannot be negative" in str(exc_info.value).lower()
        assert "to_start_of_line" in str(exc_info.value)

    def test_goto_with_invalid_type_raises_error(self):
        """Test that non-Position types raise TypeError."""
        text = Text("Hello")

        with pytest.raises(TypeError) as exc_info:
            text.goto((0, 0))  # tuple instead of Position

        assert "Expected Position" in str(exc_info.value)

    def test_goto_with_column_past_line_end_clamps(self):
        """Test that excessive column is clamped with warning."""
        text = Text("Hello")  # 5 characters
        text.edit_mode = True

        # Should not raise, but clamps to valid position
        text.goto(Position(0, 100))

        # Should clamp to end of line (position 5 in edit mode)
        assert text.cursor_position.colno == 5

    def test_goto_valid_position_works(self):
        """Test that valid positions work correctly."""
        text = Text("Line 1\nLine 2\nLine 3")

        text.goto(Position(1, 3))

        assert text.cursor_position.lineno == 1
        assert text.cursor_position.colno == 3


class TestInsertValidation:
    """Test Text.insert() input validation."""

    def test_insert_with_non_string_raises_error(self):
        """Test that non-string types raise TypeError."""
        text = Text()
        text.edit_mode = True

        with pytest.raises(TypeError) as exc_info:
            text.insert(123)  # int instead of str

        assert "Expected str" in str(exc_info.value)
        assert "Use str()" in str(exc_info.value)

    def test_insert_without_edit_mode_raises_error(self):
        """Test that insert without edit mode raises RuntimeError."""
        text = Text()
        text.edit_mode = False

        with pytest.raises(RuntimeError) as exc_info:
            text.insert("test")

        assert "not in edit mode" in str(exc_info.value).lower()
        assert "edit_mode=True" in str(exc_info.value)

    def test_insert_with_valid_string_works(self):
        """Test that valid string insertion works."""
        text = Text()
        text.edit_mode = True

        text.insert("Hello World")

        assert str(text) == "Hello World"

    def test_insert_with_newlines_works(self):
        """Test that insertion with newlines works."""
        text = Text()
        text.edit_mode = True

        text.insert("Line 1\nLine 2")

        assert "Line 1" in str(text)
        assert "Line 2" in str(text)


class TestValidationErrorMessages:
    """Test that error messages are helpful and actionable."""

    def test_goto_error_includes_valid_range(self):
        """Test that goto errors show the valid range."""
        text = Text("A\nB\nC\nD")  # 4 lines (0-3)

        with pytest.raises(ValueError) as exc_info:
            text.goto(Position(10, 0))

        error_msg = str(exc_info.value)
        assert "0 to 3" in error_msg  # Shows valid range

    def test_goto_error_suggests_alternative(self):
        """Test that goto errors suggest alternative methods."""
        text = Text("Hello")

        with pytest.raises(ValueError) as exc_info:
            text.goto(Position(0, -5))

        assert "to_start_of_line" in str(exc_info.value)

    def test_insert_error_shows_type_received(self):
        """Test that insert errors show what type was received."""
        text = Text()
        text.edit_mode = True

        with pytest.raises(TypeError) as exc_info:
            text.insert(['list', 'of', 'strings'])

        error_msg = str(exc_info.value)
        assert "list" in error_msg  # Shows actual type received

    def test_insert_error_explains_solution(self):
        """Test that insert errors explain how to fix."""
        text = Text()
        text.edit_mode = True

        with pytest.raises(TypeError) as exc_info:
            text.insert(42)

        assert "Use str()" in str(exc_info.value)


class TestEdgeCases:
    """Test edge cases in validation."""

    def test_goto_on_empty_text_raises_error(self):
        """Test goto on empty text."""
        text = Text("")  # Empty text has 1 empty line

        # Should work for line 0
        text.goto(Position(0, 0))
        assert text.cursor_position == Position(0, 0)

        # Should fail for line 1
        with pytest.raises(ValueError):
            text.goto(Position(1, 0))

    def test_goto_respects_edit_mode_for_column_validation(self):
        """Test that column validation respects edit_mode."""
        text = Text("Hello")  # 5 characters

        # In command mode, max column is 4 (length - 1)
        text.edit_mode = False
        text.goto(Position(0, 4))
        assert text.cursor_position.colno == 4

        # In edit mode, max column is 5 (length)
        text.edit_mode = True
        text.goto(Position(0, 5))
        assert text.cursor_position.colno == 5

    def test_insert_empty_string_works(self):
        """Test that inserting empty string doesn't error."""
        text = Text("Hello")
        text.edit_mode = True

        text.insert("")  # Should not raise

        assert str(text) == "Hello"

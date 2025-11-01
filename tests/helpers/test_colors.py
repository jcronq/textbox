"""
Tests for color helper functions in textbox.utils.colors.

These functions provide convenient shortcuts for creating colored TextSegments.
Target: Improve coverage from 0% to 90%.
"""

import pytest
from textbox.utils.colors import dark_blue, light_blue, dark_purple, light_purple
from textbox.core.text_segment import TextSegment
from textbox.utils.color_code import ColorCode


class TestDarkBlue:
    """Test dark_blue() helper function."""

    def test_dark_blue_returns_text_segment(self):
        """Test that dark_blue() returns a TextSegment."""
        result = dark_blue("test")
        assert isinstance(result, TextSegment)

    def test_dark_blue_has_correct_color(self):
        """Test that dark_blue() sets DARK_BLUE color code."""
        result = dark_blue("test")
        assert result.color_pair == ColorCode.DARK_BLUE

    def test_dark_blue_preserves_text(self):
        """Test that dark_blue() preserves the input text."""
        text = "Hello, World!"
        result = dark_blue(text)
        assert str(result) == text

    def test_dark_blue_with_empty_string(self):
        """Test dark_blue() with empty string."""
        result = dark_blue("")
        assert isinstance(result, TextSegment)
        assert str(result) == ""

    def test_dark_blue_type_validation(self):
        """Test that dark_blue() validates input type."""
        with pytest.raises(TypeError) as exc_info:
            dark_blue(123)
        assert "string" in str(exc_info.value).lower()

    def test_dark_blue_with_unicode(self):
        """Test dark_blue() with unicode characters."""
        text = "Hello 世界 🌍"
        result = dark_blue(text)
        assert str(result) == text


class TestLightBlue:
    """Test light_blue() helper function."""

    def test_light_blue_returns_text_segment(self):
        """Test that light_blue() returns a TextSegment."""
        result = light_blue("test")
        assert isinstance(result, TextSegment)

    def test_light_blue_has_correct_color(self):
        """Test that light_blue() sets LIGHT_BLUE color code."""
        result = light_blue("test")
        assert result.color_pair == ColorCode.LIGHT_BLUE

    def test_light_blue_preserves_text(self):
        """Test that light_blue() preserves the input text."""
        text = "Test message"
        result = light_blue(text)
        assert str(result) == text

    def test_light_blue_type_validation(self):
        """Test that light_blue() validates input type."""
        with pytest.raises(TypeError):
            light_blue(None)


class TestDarkPurple:
    """Test dark_purple() helper function."""

    def test_dark_purple_returns_text_segment(self):
        """Test that dark_purple() returns a TextSegment."""
        result = dark_purple("test")
        assert isinstance(result, TextSegment)

    def test_dark_purple_has_correct_color(self):
        """Test that dark_purple() sets DARK_PURPLE color code."""
        result = dark_purple("test")
        assert result.color_pair == ColorCode.DARK_PURPLE

    def test_dark_purple_preserves_text(self):
        """Test that dark_purple() preserves the input text."""
        text = "Purple text"
        result = dark_purple(text)
        assert str(result) == text

    def test_dark_purple_type_validation(self):
        """Test that dark_purple() validates input type."""
        with pytest.raises(TypeError) as exc_info:
            dark_purple([])
        assert "string" in str(exc_info.value).lower()


class TestLightPurple:
    """Test light_purple() helper function."""

    def test_light_purple_returns_text_segment(self):
        """Test that light_purple() returns a TextSegment."""
        result = light_purple("test")
        assert isinstance(result, TextSegment)

    def test_light_purple_has_correct_color(self):
        """Test that light_purple() sets LIGHT_PURPLE color code."""
        result = light_purple("test")
        assert result.color_pair == ColorCode.LIGHT_PURPLE

    def test_light_purple_preserves_text(self):
        """Test that light_purple() preserves the input text."""
        text = "Light purple text"
        result = light_purple(text)
        assert str(result) == text

    def test_light_purple_with_special_chars(self):
        """Test light_purple() with special characters."""
        text = "!@#$%^&*()"
        result = light_purple(text)
        assert str(result) == text

    def test_light_purple_type_validation(self):
        """Test that light_purple() validates input type."""
        with pytest.raises(TypeError):
            light_purple({'key': 'value'})


class TestColorHelperConsistency:
    """Test consistency across all color helper functions."""

    def test_all_helpers_return_text_segments(self):
        """Test that all helpers return TextSegment instances."""
        helpers = [dark_blue, light_blue, dark_purple, light_purple]
        text = "test"

        for helper in helpers:
            result = helper(text)
            assert isinstance(result, TextSegment), f"{helper.__name__} didn't return TextSegment"

    def test_all_helpers_validate_string_input(self):
        """Test that all helpers validate string input."""
        helpers = [dark_blue, light_blue, dark_purple, light_purple]

        for helper in helpers:
            with pytest.raises(TypeError):
                helper(12345)

    def test_color_codes_are_unique(self):
        """Test that each helper uses a different color code."""
        text = "test"
        colors = {
            'dark_blue': dark_blue(text).color_pair,
            'light_blue': light_blue(text).color_pair,
            'dark_purple': dark_purple(text).color_pair,
            'light_purple': light_purple(text).color_pair,
        }

        # All colors should be different
        color_values = list(colors.values())
        assert len(color_values) == len(set(color_values)), "Color codes should be unique"

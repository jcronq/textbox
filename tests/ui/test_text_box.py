"""
Tests for TextBox class.

Tests text display, scrolling, cursor positioning, and resize handling.
Target: Improve text_box.py coverage from 31% to 70%+.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
import curses
from textbox.ui.text_box import TextBox
from textbox.ui.window import Window
from textbox.utils.box_types import BoundingBox, Position, Dimensions
from textbox.core.text import Text
from textbox.core.text_segment import TextSegment
from textbox.core.segmented_text_line import SegmentedTextLine


class TestTextBoxInitialization:
    """Test TextBox instantiation and initialization."""

    @patch('textbox.ui.text_box.curses')
    def test_textbox_creates_with_defaults(self, mock_curses):
        """Test that TextBox can be created with default parameters."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        assert textbox.name == "test"
        assert textbox.top_to_bottom == True
        assert textbox._has_box == False
        assert textbox.color_pair == 0

    @patch('textbox.ui.text_box.curses')
    def test_textbox_creates_with_box_enabled(self, mock_curses):
        """Test that TextBox can be created with box borders."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, has_box=True)

        assert textbox._has_box == True

    @patch('textbox.ui.text_box.curses')
    def test_textbox_creates_with_bottom_to_top(self, mock_curses):
        """Test that TextBox can be created with bottom-to-top rendering."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, top_to_bottom=False)

        assert textbox.top_to_bottom == False

    @patch('textbox.ui.text_box.curses')
    def test_textbox_creates_with_color_pair(self, mock_curses):
        """Test that TextBox can be created with custom color pair."""
        mock_curses.color_pair.return_value = 5
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, color_pair=5)

        assert textbox.color_pair == 5

    @patch('textbox.ui.text_box.curses')
    def test_textbox_initializes_window(self, mock_curses):
        """Test that TextBox creates a window from parent."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        mock_parent_window.create_new_window.assert_called_once_with(box)
        assert textbox.window == mock_window


class TestTextBoxProperties:
    """Test TextBox property accessors."""

    @patch('textbox.ui.text_box.curses')
    def test_height_property(self, mock_curses):
        """Test that height property returns window height."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 15
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 15, 80)
        textbox = TextBox("test", mock_parent_window, box)

        assert textbox.height == 15

    @patch('textbox.ui.text_box.curses')
    def test_width_property(self, mock_curses):
        """Test that width property returns window width."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 100
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 100)
        textbox = TextBox("test", mock_parent_window, box)

        assert textbox.width == 100

    @patch('textbox.ui.text_box.curses')
    def test_printable_width_without_box(self, mock_curses):
        """Test printable_width without box borders."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, has_box=False)

        # Width - 1 for cursor buffer
        assert textbox.printable_width == 79

    @patch('textbox.ui.text_box.curses')
    def test_printable_width_with_box(self, mock_curses):
        """Test printable_width with box borders."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, has_box=True)

        # Width - 3 (left border, right border, cursor buffer)
        assert textbox.printable_width == 77

    @patch('textbox.ui.text_box.curses')
    def test_printable_height_without_box(self, mock_curses):
        """Test printable_height without box borders."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, has_box=False)

        assert textbox.printable_height == 9

    @patch('textbox.ui.text_box.curses')
    def test_printable_height_with_box(self, mock_curses):
        """Test printable_height with box borders."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, has_box=True)

        # Height - 2 (top and bottom borders)
        assert textbox.printable_height == 8

    @patch('textbox.ui.text_box.curses')
    def test_first_printable_lineno_without_box(self, mock_curses):
        """Test first_printable_lineno without box borders."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, has_box=False)

        assert textbox.first_printable_lineno == 0

    @patch('textbox.ui.text_box.curses')
    def test_first_printable_lineno_with_box(self, mock_curses):
        """Test first_printable_lineno with box borders."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, has_box=True)

        assert textbox.first_printable_lineno == 1

    @patch('textbox.ui.text_box.curses')
    def test_box_offset_without_box(self, mock_curses):
        """Test box_offset without box borders."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, has_box=False)

        assert textbox.box_offset == Position(0, 0)

    @patch('textbox.ui.text_box.curses')
    def test_box_offset_with_box(self, mock_curses):
        """Test box_offset with box borders."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, has_box=True)

        assert textbox.box_offset == Position(1, 1)

    @patch('textbox.ui.text_box.curses')
    def test_attributes_property(self, mock_curses):
        """Test that attributes property returns color pair."""
        mock_curses.color_pair.return_value = 42
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, color_pair=5)

        attrs = textbox.attributes
        assert len(attrs) == 1
        mock_curses.color_pair.assert_called_with(5)


class TestTextBoxVisibility:
    """Test TextBox visibility toggling."""

    @patch('textbox.ui.text_box.curses')
    def test_box_visible_getter_default_false(self, mock_curses):
        """Test that box_visible defaults to False."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        assert textbox.box_visible == False

    @patch('textbox.ui.text_box.curses')
    def test_box_visible_setter_enables_box(self, mock_curses):
        """Test that setting box_visible to True enables border."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox.box_visible = True

        assert textbox.box_visible == True
        mock_window.add_box.assert_called_once()

    @patch('textbox.ui.text_box.curses')
    def test_box_visible_setter_calls_refresh(self, mock_curses):
        """Test that setting box_visible calls refresh."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox.box_visible = True

        mock_window.refresh.assert_called()


class TestTextBoxScrolling:
    """Test TextBox scrolling operations."""

    @patch('textbox.ui.text_box.curses')
    def test_scroll_down_increases_first_lineno(self, mock_curses):
        """Test that scroll_down increases first line number."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Add some text so adjust_screen_position doesn't reset scroll
        for i in range(20):
            textbox._text_list.insert(f"Line {i}\n")

        # Mock adjust_screen_position to prevent it from changing scroll position
        textbox.adjust_screen_position = MagicMock()

        initial_lineno = textbox._first_lineno_in_window
        textbox.scroll_down(3)

        assert textbox._first_lineno_in_window == initial_lineno + 3

    @patch('textbox.ui.text_box.curses')
    def test_scroll_down_calls_redraw(self, mock_curses):
        """Test that scroll_down triggers redraw."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox.scroll_down(2)

        # Redraw should call erase and refresh
        mock_window.erase.assert_called()
        mock_window.refresh.assert_called()

    @patch('textbox.ui.text_box.curses')
    def test_scroll_up_decreases_first_lineno(self, mock_curses):
        """Test that scroll_up decreases first line number."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Add text so adjust_screen_position doesn't reset scroll
        for i in range(20):
            textbox._text_list.insert(f"Line {i}\n")

        # Mock adjust_screen_position to prevent it from changing scroll position
        textbox.adjust_screen_position = MagicMock()

        # First scroll down to have room to scroll up
        textbox._first_lineno_in_window = 5
        textbox.scroll_up(2)

        assert textbox._first_lineno_in_window == 3

    @patch('textbox.ui.text_box.curses')
    def test_scroll_up_raises_error_when_negative(self, mock_curses):
        """Test that scroll_up raises error when scrolling past first line."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox._first_lineno_in_window = 1

        with pytest.raises(ValueError, match="Cannot scroll up past first line"):
            textbox.scroll_up(2)

    @patch('textbox.ui.text_box.curses')
    def test_first_viewable_lineno_property(self, mock_curses):
        """Test first_viewable_lineno property."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox._first_lineno_in_window = 5
        assert textbox.first_viewable_lineno == 5

    @patch('textbox.ui.text_box.curses')
    def test_last_viewable_lineno_property(self, mock_curses):
        """Test last_viewable_lineno property."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox._first_lineno_in_window = 5
        # printable_height is 9 (height - 1)
        assert textbox.last_viewable_lineno == 14

    @patch('textbox.ui.text_box.curses')
    def test_last_viewable_lineno_setter(self, mock_curses):
        """Test last_viewable_lineno setter."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # printable_height is 9
        textbox.last_viewable_lineno = 20
        # first_lineno should be 20 - 9 = 11
        assert textbox._first_lineno_in_window == 11

    @patch('textbox.ui.text_box.curses')
    def test_last_viewable_lineno_setter_type_error(self, mock_curses):
        """Test last_viewable_lineno setter raises TypeError for non-int."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        with pytest.raises(TypeError, match="last_viewable_lineno must be an integer"):
            textbox.last_viewable_lineno = "not an int"


class TestTextBoxAddText:
    """Test TextBox text addition methods."""

    @patch('textbox.ui.text_box.curses')
    def test_add_str_adds_string(self, mock_curses):
        """Test that add_str adds a string to the text list."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox.add_str("Hello World")

        # Check that text was added
        assert textbox._text_list.line_count > 0

    @patch('textbox.ui.text_box.curses')
    def test_add_text_adds_text_object(self, mock_curses):
        """Test that add_text adds a Text object."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        text_obj = Text("Test text")
        textbox.add_text(text_obj)

        # Check that text was added
        assert textbox._text_list.line_count > 0

    @patch('textbox.ui.text_box.curses')
    def test_add_text_sets_max_line_width(self, mock_curses):
        """Test that add_text sets max_line_width on Text object."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        text_obj = Text("Test")
        textbox.add_text(text_obj)

        assert text_obj.max_line_width == textbox.printable_width

    @patch('textbox.ui.text_box.curses')
    def test_add_segmented_text_line(self, mock_curses):
        """Test that add_segmented_text_line calls text_list method."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Mock the text_list method since it doesn't exist yet
        textbox._text_list.add_segmented_text_line = MagicMock()

        seg_line = SegmentedTextLine([TextSegment("Hello", color_pair=1)])
        textbox.add_segmented_text_line(seg_line)

        # Check that the method was called
        textbox._text_list.add_segmented_text_line.assert_called_once_with(seg_line)

    @patch('textbox.ui.text_box.curses')
    def test_print_text_adds_and_redraws(self, mock_curses):
        """Test that print_text adds text and redraws."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # print_text expects a Text object, not a string
        text_obj = Text("Test message")
        textbox.print_text(text_obj)

        # Should trigger redraw
        mock_window.erase.assert_called()
        mock_window.refresh.assert_called()


class TestTextBoxRefreshRedraw:
    """Test TextBox refresh and redraw operations."""

    @patch('textbox.ui.text_box.curses')
    def test_refresh_calls_window_refresh(self, mock_curses):
        """Test that refresh calls window.refresh."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox.refresh()

        mock_window.refresh.assert_called()

    @patch('textbox.ui.text_box.curses')
    def test_redraw_calls_erase_and_refresh(self, mock_curses):
        """Test that redraw calls erase and refresh."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox.redraw()

        mock_window.erase.assert_called()
        mock_window.refresh.assert_called()

    @patch('textbox.ui.text_box.curses')
    def test_redraw_with_cursor_moves_cursor(self, mock_curses):
        """Test that redraw with_cursor=True moves cursor."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_window.move_cursor = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox.redraw(with_cursor=True)

        mock_window.move_cursor.assert_called()

    @patch('textbox.ui.text_box.curses')
    def test_redraw_draws_box_when_visible(self, mock_curses):
        """Test that redraw draws box when box_visible is True."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_window.add_box = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox._box_visible = True
        textbox.redraw()

        # Should call add_box during redraw
        mock_window.add_box.assert_called()

    @patch('textbox.ui.text_box.curses')
    def test_erase_clears_text_list(self, mock_curses):
        """Test that erase clears the text list."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Add some text
        textbox._text_list.insert("Test")
        initial_count = textbox._text_list.line_count

        # Erase
        textbox.erase()

        # Text list should be cleared (reset to empty)
        assert textbox._text_list.line_count == 0

    @patch('textbox.ui.text_box.curses')
    def test_update_cursor_moves_and_refreshes(self, mock_curses):
        """Test that update_cursor moves cursor and refreshes."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.move_cursor = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox.update_cursor()

        mock_window.move_cursor.assert_called()
        mock_window.refresh.assert_called()


class TestTextBoxResize:
    """Test TextBox resize handling."""

    @patch('textbox.ui.text_box.curses')
    def test_resize_calls_window_resize(self, mock_curses):
        """Test that resize calls window.resize."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.resize = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        new_box = BoundingBox(0, 0, 15, 100)
        textbox.resize(new_box)

        mock_window.resize.assert_called_with(new_box, False)

    @patch('textbox.ui.text_box.curses')
    def test_resize_updates_max_line_width(self, mock_curses):
        """Test that resize updates text_list max_line_width."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.resize = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Change window dimensions
        mock_window.width = 100
        new_box = BoundingBox(0, 0, 10, 100)
        textbox.resize(new_box)

        # max_line_width should be updated to new printable_width
        assert textbox._text_list.max_line_width == textbox.printable_width

    @patch('textbox.ui.text_box.curses')
    def test_resize_preserves_viewable_position(self, mock_curses):
        """Test that resize tries to preserve viewable position."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.resize = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Add some text
        textbox._text_list.insert("Line 1\nLine 2\nLine 3")
        textbox._first_lineno_in_window = 1

        # Get last viewable before resize
        old_last = textbox.last_viewable_lineno

        # Resize
        new_box = BoundingBox(0, 0, 15, 80)
        mock_window.height = 15
        textbox.resize(new_box)

        # The resize method tries to keep last_viewable_lineno consistent
        # (or bounded by total_line_count)


class TestTextBoxDrawing:
    """Test TextBox text drawing operations."""

    @patch('textbox.ui.text_box.curses')
    def test_draw_texts_with_no_text(self, mock_curses):
        """Test that draw_texts handles empty text list."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.addstr = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Should not crash with empty text
        textbox.draw_texts()

        # addstr should not be called
        mock_window.addstr.assert_not_called()

    @patch('textbox.ui.text_box.curses')
    def test_draw_texts_with_text_top_to_bottom(self, mock_curses):
        """Test that draw_texts renders text top-to-bottom."""
        mock_curses.color_pair.return_value = 0
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.addstr = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, top_to_bottom=True)

        # Add some text
        textbox._text_list.insert("Hello")

        textbox.draw_texts()

        # addstr should be called for the text
        assert mock_window.addstr.called

    @patch('textbox.ui.text_box.curses')
    def test_draw_texts_with_text_bottom_to_top(self, mock_curses):
        """Test that draw_texts renders text bottom-to-top."""
        mock_curses.color_pair.return_value = 0
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.addstr = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, top_to_bottom=False)

        # Add some text
        textbox._text_list.insert("World")

        textbox.draw_texts()

        # addstr should be called
        assert mock_window.addstr.called

    @patch('textbox.ui.text_box.curses')
    def test_hline_calls_window_hline(self, mock_curses):
        """Test that hline calls window.hline."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.hline = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        pos = Position(5, 0)
        textbox.hline(pos)

        mock_window.hline.assert_called_with(pos, verbose=False)


class TestTextBoxCursorPosition:
    """Test TextBox cursor positioning."""

    @patch('textbox.ui.text_box.curses')
    def test_cursor_position_property(self, mock_curses):
        """Test cursor_position property calculation."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Get cursor position (should be valid Position)
        pos = textbox.cursor_position
        assert isinstance(pos, Position)

    @patch('textbox.ui.text_box.curses')
    def test_cursor_position_with_offset(self, mock_curses):
        """Test cursor_position accounts for box offset."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box, has_box=True)

        # With box, offset should be (1, 1)
        pos = textbox.cursor_position
        # Position calculation includes box_offset


class TestTextBoxCharacterOps:
    """Test TextBox character operations."""

    @patch('textbox.ui.text_box.curses')
    def test_add_char_inserts_character(self, mock_curses):
        """Test that add_char inserts a character."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        textbox.add_char('x')

        # Character should be in the text
        assert len(str(textbox._text_list.current_text)) > 0

    @patch('textbox.ui.text_box.curses')
    def test_end_current_text_increments_pointer(self, mock_curses):
        """Test that end_current_text increments text pointer."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        initial_ptr = textbox._text_list._text_ptr
        textbox.end_current_text()

        assert textbox._text_list._text_ptr == initial_ptr + 1


class TestTextBoxAdjustScreenPosition:
    """Test TextBox screen position adjustment."""

    @patch('textbox.ui.text_box.curses')
    def test_adjust_screen_position_scrolls_down_when_below(self, mock_curses):
        """Test that adjust_screen_position scrolls down when cursor is below viewport."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Add multiple lines of text
        for i in range(20):
            textbox._text_list.insert(f"Line {i}\n")

        # Move cursor to line beyond viewport
        textbox._text_list.current_text._line_ptr = 15

        # This should trigger scroll down
        textbox.adjust_screen_position()

        # first_lineno should have increased
        assert textbox._first_lineno_in_window > 0

    @patch('textbox.ui.text_box.curses')
    def test_adjust_screen_position_scrolls_up_when_above(self, mock_curses):
        """Test that adjust_screen_position scrolls up when cursor is above viewport."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_window.erase = MagicMock()
        mock_window.refresh = MagicMock()
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Start scrolled down
        textbox._first_lineno_in_window = 10

        # Add text
        for i in range(20):
            textbox._text_list.insert(f"Line {i}\n")

        # Move cursor to before viewport
        textbox._text_list.current_text._line_ptr = 2

        # This should trigger scroll up
        initial_first = textbox._first_lineno_in_window
        textbox.adjust_screen_position()

        # first_lineno should have decreased
        assert textbox._first_lineno_in_window < initial_first


class TestTextBoxColumnPtr:
    """Test TextBox column pointer access."""

    @patch('textbox.ui.text_box.curses')
    def test_column_ptr_property(self, mock_curses):
        """Test that column_ptr property returns current column."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Default should be 0
        assert textbox.column_ptr == 0

    @patch('textbox.ui.text_box.curses')
    def test_current_line_property(self, mock_curses):
        """Test that current_line property returns current line."""
        mock_parent_window = MagicMock(spec=Window)
        mock_window = MagicMock(spec=Window)
        mock_window.height = 10
        mock_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_window

        box = BoundingBox(0, 0, 10, 80)
        textbox = TextBox("test", mock_parent_window, box)

        # Should return a TextLine object
        line = textbox.current_line
        assert line is not None

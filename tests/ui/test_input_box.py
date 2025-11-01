"""
Tests for InputBox class.

Tests text input handling, cursor management, history scrolling, and edit operations.
Target: Improve input_box.py coverage from 28% to 70%+.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
import curses
from textbox.ui.input_box import InputBox, InputHistory
from textbox.ui.window import Window
from textbox.utils.box_types import BoundingBox, Position
from textbox.core.text import Text
from textbox.core.text_line import TextLine


class TestInputHistory:
    """Test InputHistory class for command history management."""

    def test_input_history_initialization(self):
        """Test that InputHistory initializes with correct defaults."""
        history = InputHistory()

        assert len(history) == 0
        assert history._history_ptr == 0
        assert history._max_size == 100
        assert history._short_term_memory is None

    def test_input_history_custom_max_size(self):
        """Test InputHistory with custom max size."""
        history = InputHistory(max_size=50)

        assert history._max_size == 50

    def test_append_text_to_history(self):
        """Test appending text to history."""
        history = InputHistory()
        text = Text([TextLine("test")])

        history.append(text)

        assert len(history) == 1
        assert history._history_ptr == 1

    def test_append_invalid_type_raises_error(self):
        """Test that appending non-Text raises ValueError."""
        history = InputHistory()

        with pytest.raises(ValueError, match="Text must be a Text object"):
            history.append("not a Text object")

    def test_append_multiple_texts(self):
        """Test appending multiple texts to history."""
        history = InputHistory()

        for i in range(5):
            text = Text([TextLine(f"test{i}")])
            history.append(text)

        assert len(history) == 5
        assert history._history_ptr == 5

    def test_history_max_size_enforcement(self):
        """Test that history enforces max_size limit."""
        history = InputHistory(max_size=3)

        for i in range(5):
            text = Text([TextLine(f"test{i}")])
            history.append(text)

        # Should only keep last 3
        assert len(history) == 3
        assert str(history[0]) == "test2"
        assert str(history[2]) == "test4"

    def test_at_present_returns_true_initially(self):
        """Test that at_present returns True when at end of history."""
        history = InputHistory()
        text = Text([TextLine("test")])
        history.append(text)

        assert history.at_present() is True

    def test_at_present_returns_false_after_previous(self):
        """Test that at_present returns False after moving back."""
        history = InputHistory()
        text1 = Text([TextLine("test1")])
        text2 = Text([TextLine("test2")])
        history.append(text1)
        history.append(text2)

        history.previous()

        assert history.at_present() is False

    def test_has_history_returns_false_when_empty(self):
        """Test that has_history returns False when empty."""
        history = InputHistory()

        assert history.has_history() is False

    def test_has_history_returns_true_when_items_exist(self):
        """Test that has_history returns True when history has items and ptr > 0."""
        history = InputHistory()
        text = Text([TextLine("test")])
        history.append(text)

        # After append, ptr = 1 and len = 1, so len > 0 and ptr > 0 = True
        assert history.has_history() is True

    def test_has_history_returns_false_after_previous_to_beginning(self):
        """Test that has_history returns False when at beginning (ptr=0)."""
        history = InputHistory()
        text = Text([TextLine("test")])
        history.append(text)
        history.previous()  # This sets ptr = 0

        # ptr = 0, so has_history should be False (even though len > 0)
        assert history.has_history() is False

    def test_previous_decrements_pointer(self):
        """Test that previous() decrements history pointer."""
        history = InputHistory()
        text1 = Text([TextLine("test1")])
        text2 = Text([TextLine("test2")])
        history.append(text1)
        history.append(text2)

        result = history.previous()

        assert history._history_ptr == 1
        assert str(result) == "test2"

    def test_previous_at_beginning_returns_first_item(self):
        """Test that previous() at beginning returns first item."""
        history = InputHistory()
        text = Text([TextLine("test")])
        history.append(text)

        history.previous()
        result = history.previous()

        assert history._history_ptr == 0
        assert str(result) == "test"

    def test_next_increments_pointer(self):
        """Test that next() increments history pointer."""
        history = InputHistory()
        text1 = Text([TextLine("test1")])
        text2 = Text([TextLine("test2")])
        history.append(text1)
        history.append(text2)
        history.previous()
        history.previous()

        result = history.next()

        assert history._history_ptr == 1
        assert str(result) == "test2"

    def test_next_at_end_returns_short_term_memory(self):
        """Test that next() at end returns short term memory."""
        history = InputHistory()
        text1 = Text([TextLine("test1")])
        text2 = Text([TextLine("test2")])
        memory = Text([TextLine("memory")])
        history.append(text1)
        history.append(text2)
        history.set_short_term_memory(memory)
        history.previous()

        result = history.next()

        assert str(result) == "memory"
        assert history.at_present() is True

    def test_next_beyond_end_returns_none(self):
        """Test that next() beyond end returns None."""
        history = InputHistory()
        text = Text([TextLine("test")])
        history.append(text)

        result = history.next()

        assert result is None

    def test_set_short_term_memory(self):
        """Test setting short term memory."""
        history = InputHistory()
        memory = Text([TextLine("memory")])

        history.set_short_term_memory(memory)

        assert history.has_short_term_memory() is True

    def test_set_short_term_memory_invalid_type_raises_error(self):
        """Test that setting non-Text as memory raises ValueError."""
        history = InputHistory()

        with pytest.raises(ValueError, match="Text must be a Text object"):
            history.set_short_term_memory("not a Text object")

    def test_pop_short_term_memory(self):
        """Test popping short term memory."""
        history = InputHistory()
        memory = Text([TextLine("memory")])
        history.set_short_term_memory(memory)

        result = history.pop_short_term_memory()

        assert str(result) == "memory"
        assert history.has_short_term_memory() is False

    def test_pop_short_term_memory_when_none(self):
        """Test popping short term memory when none exists."""
        history = InputHistory()

        result = history.pop_short_term_memory()

        assert result is None

    def test_getitem_returns_history_entry(self):
        """Test that __getitem__ returns history entry."""
        history = InputHistory()
        text1 = Text([TextLine("test1")])
        text2 = Text([TextLine("test2")])
        history.append(text1)
        history.append(text2)

        assert str(history[0]) == "test1"
        assert str(history[1]) == "test2"

    def test_getitem_with_slice(self):
        """Test that __getitem__ works with slices."""
        history = InputHistory()
        for i in range(5):
            history.append(Text([TextLine(f"test{i}")]))

        result = history[1:3]

        assert len(result) == 2
        assert str(result[0]) == "test1"
        assert str(result[1]) == "test2"

    def test_repr_shows_state(self):
        """Test that __repr__ shows history state."""
        history = InputHistory()
        text = Text([TextLine("test")])
        history.append(text)

        repr_str = repr(history)

        assert "len=1" in repr_str
        assert "ptr=1" in repr_str


class TestInputBoxInitialization:
    """Test InputBox instantiation and initialization."""

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_input_box_creates_successfully(self, mock_window_curses, mock_textbox_curses):
        """Test that InputBox can be instantiated."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True

        assert input_box is not None
        assert isinstance(input_box._history, InputHistory)

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_input_box_requires_top_to_bottom(self, mock_window_curses, mock_textbox_curses):
        """Test that InputBox requires top_to_bottom=True."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_parent_window.create_new_window.return_value = MagicMock()
        bbox = BoundingBox(0, 0, 5, 80)

        with pytest.raises(ValueError, match="InputBox must be top-to-bottom"):
            InputBox("test", mock_parent_window, bbox, top_to_bottom=False)

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_input_box_initializes_text_list(self, mock_window_curses, mock_textbox_curses):
        """Test that InputBox initializes with empty text."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True

        assert input_box._text_ptr == 0
        assert isinstance(input_box._history, InputHistory)


class TestInputBoxTextOperations:
    """Test InputBox text manipulation methods."""

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_set_text(self, mock_window_curses, mock_textbox_curses):
        """Test setting text on InputBox."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        new_text = Text([TextLine("new text")])

        with patch.object(input_box, 'redraw'):
            input_box.set_text(new_text)

        # Verify text was set
        assert str(input_box.text).strip() == "new text"

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_set_text_invalid_type_raises_error(self, mock_window_curses, mock_textbox_curses):
        """Test that set_text with non-Text raises ValueError."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True

        with pytest.raises(ValueError, match="Text must be a Text object"):
            input_box.set_text("not a Text object")

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_set_text_to_str(self, mock_window_curses, mock_textbox_curses):
        """Test setting text from string."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True

        with patch.object(input_box, 'redraw'):
            input_box.set_text_to_str("test string")

        assert "test string" in str(input_box.text)

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_set_text_to_str_invalid_type_raises_error(self, mock_window_curses, mock_textbox_curses):
        """Test that set_text_to_str with non-string raises ValueError."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True

        with pytest.raises(ValueError, match="Text must be a string"):
            input_box.set_text_to_str(123)


class TestInputBoxCursorMovement:
    """Test InputBox cursor movement methods."""

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_cursor_up(self, mock_window_curses, mock_textbox_curses):
        """Test cursor_up moves cursor up."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.edit_mode = True
        input_box.text.insert("line1\nline2")
        input_box.text.to_end_of_text()

        with patch.object(input_box, 'redraw'):
            input_box.cursor_up()

        assert input_box.text.line_ptr == 0

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_cursor_down(self, mock_window_curses, mock_textbox_curses):
        """Test cursor_down moves cursor down."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("line1\nline2")
        input_box.text.goto(Position(0, 0))  # Go to line 0, column 0

        with patch.object(input_box, 'redraw'):
            input_box.cursor_down()

        assert input_box.text.line_ptr == 1

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_cursor_left(self, mock_window_curses, mock_textbox_curses):
        """Test cursor_left moves cursor left."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.edit_mode = True
        input_box.text.insert("test")

        with patch.object(input_box, 'redraw'):
            input_box.cursor_left()

        assert input_box.text.column_ptr == 3

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_cursor_right(self, mock_window_curses, mock_textbox_curses):
        """Test cursor_right moves cursor right."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.edit_mode = True
        input_box.text.insert("test")
        input_box.text.to_start_of_line()

        with patch.object(input_box, 'redraw'):
            input_box.cursor_right()

        assert input_box.text.column_ptr == 1


class TestInputBoxEditOperations:
    """Test InputBox text editing operations."""

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_insert_character_at_cursor(self, mock_window_curses, mock_textbox_curses):
        """Test inserting character at cursor."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True

        with patch.object(input_box, 'redraw'):
            input_box.insert_character_at_cursor('a')

        assert 'a' in str(input_box.text)

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_replace_character_at_cursor(self, mock_window_curses, mock_textbox_curses):
        """Test replacing character at cursor."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("test")
        input_box.text.to_start_of_line()

        with patch.object(input_box, 'redraw'):
            input_box.replace_character_at_cursor('X')

        assert 'X' in str(input_box.text)

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_handle_backspace(self, mock_window_curses, mock_textbox_curses):
        """Test backspace removes character."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("test")

        with patch.object(input_box, 'redraw'):
            input_box.handle_backspace()

        assert str(input_box.text).strip() == "tes"


class TestInputBoxHistory:
    """Test InputBox history management."""

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_append_history(self, mock_window_curses, mock_textbox_curses):
        """Test appending text to history."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("test command")

        input_box.append_history()

        assert len(input_box._history) == 1

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_history_scroll_up_with_empty_history(self, mock_window_curses, mock_textbox_curses):
        """Test history scroll up with empty history does nothing."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        current_text = str(input_box.text)

        input_box.history_scroll_up()

        # Text should be unchanged
        assert str(input_box.text) == current_text

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_history_scroll_up_saves_short_term_memory(self, mock_window_curses, mock_textbox_curses):
        """Test history scroll up saves current text to short term memory."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("current")
        input_box.append_history()
        input_box.text.set_text_to_str("new text")

        with patch.object(input_box, 'redraw'):
            input_box.history_scroll_up()

        assert input_box._history.has_short_term_memory() is True

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_history_scroll_up_retrieves_previous_entry(self, mock_window_curses, mock_textbox_curses):
        """Test history scroll up retrieves previous history entry."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("command1")
        input_box.append_history()
        input_box.text.set_text_to_str("command2")
        input_box.append_history()
        input_box.text.set_text_to_str("current")

        with patch.object(input_box, 'redraw'):
            input_box.history_scroll_up()

        assert "command2" in str(input_box.text)

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_history_scroll_down_at_present(self, mock_window_curses, mock_textbox_curses):
        """Test history scroll down when at present does nothing."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("current")
        current_text = str(input_box.text)

        input_box.history_scroll_down()

        assert str(input_box.text) == current_text

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_history_scroll_down_retrieves_next_entry(self, mock_window_curses, mock_textbox_curses):
        """Test history scroll down retrieves next history entry."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("command1")
        input_box.append_history()
        input_box.text.set_text_to_str("command2")
        input_box.append_history()
        input_box.text.set_text_to_str("current")

        with patch.object(input_box, 'redraw'):
            # Go back twice
            input_box.history_scroll_up()
            input_box.history_scroll_up()
            # Then forward once
            input_box.history_scroll_down()

        assert "command2" in str(input_box.text)


class TestInputBoxWordNavigation:
    """Test InputBox word-based navigation."""

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_word_forward(self, mock_window_curses, mock_textbox_curses):
        """Test word_forward moves to next word."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("hello world test")
        input_box.text.to_start_of_line()

        with patch.object(input_box, 'redraw'):
            input_box.word_forward()

        # Should move to start of "world"
        assert input_box.text.column_ptr > 0

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_word_backward(self, mock_window_curses, mock_textbox_curses):
        """Test word_backward moves to previous word."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("hello world test")

        with patch.object(input_box, 'redraw'):
            input_box.word_backward()

        # Should move backward
        assert input_box.text.column_ptr < len("hello world test")


class TestInputBoxLineNavigation:
    """Test InputBox line navigation methods."""

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_end_of_line(self, mock_window_curses, mock_textbox_curses):
        """Test end_of_line moves to end of line."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("test line")
        input_box.text.to_start_of_line()

        with patch.object(input_box, 'redraw'):
            input_box.end_of_line()

        assert input_box.text.column_ptr == len("test line")

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_start_of_line(self, mock_window_curses, mock_textbox_curses):
        """Test start_of_line moves to start of line."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("test line")

        with patch.object(input_box, 'redraw'):
            input_box.start_of_line()

        assert input_box.text.column_ptr == 0


class TestInputBoxProperties:
    """Test InputBox property accessors."""

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_text_property(self, mock_window_curses, mock_textbox_curses):
        """Test text property returns Text object."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True

        assert isinstance(input_box.text, Text)

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_edit_mode_property_getter(self, mock_window_curses, mock_textbox_curses):
        """Test edit_mode property getter."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.edit_mode = True

        assert input_box.edit_mode is True

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_edit_mode_property_setter(self, mock_window_curses, mock_textbox_curses):
        """Test edit_mode property setter."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True

        input_box.edit_mode = False

        assert input_box.text.edit_mode is False

    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.window.curses')
    def test_character_at_cursor_property(self, mock_window_curses, mock_textbox_curses):
        """Test character_at_cursor property."""
        mock_window_curses.LINES = 24
        mock_window_curses.COLS = 80
        mock_textbox_curses.color_pair.return_value = 0

        mock_parent_window = MagicMock(spec=Window)
        mock_local_window = MagicMock()
        mock_local_window.height = 5
        mock_local_window.width = 80
        mock_parent_window.create_new_window.return_value = mock_local_window
        bbox = BoundingBox(0, 0, 5, 80)

        input_box = InputBox("test", mock_parent_window, bbox)
        input_box.text.edit_mode = True
        input_box.text.insert("test")
        input_box.text.to_start_of_line()

        # char_at_cursor returns a TextSegment, check its text attribute
        assert str(input_box.text.char_at_cursor) == 't'

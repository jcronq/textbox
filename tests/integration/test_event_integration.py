"""Integration tests for event system with Text and Workspace."""

import pytest
from unittest.mock import MagicMock, patch
import curses

from textbox.core.text import Text
from textbox.core.events import EventBus, TextChangedEvent, ModeChangedEvent
from textbox.utils.box_types import Position
from textbox.ui.workspace import InputOutputWorkspace, INPUT_MODE
from textbox.ui.window import Window
from textbox.ui.input_manager import AsyncInputManager


def create_mock_window():
    """Create a properly mocked Window for testing."""
    from textbox.utils.box_types import BoundingBox, Dimensions

    mock_window = MagicMock(spec=Window)
    mock_window.height = 24
    mock_window.width = 80
    mock_window.dimensions = Dimensions(24, 80)
    mock_window.position = Position(0, 0)
    mock_window.bounding_box = BoundingBox(0, 0, 24, 80)

    def create_subwindow(box):
        sub = MagicMock(spec=Window)
        sub.height = box.height
        sub.width = box.width
        sub.dimensions = Dimensions(box.height, box.width)
        sub.position = Position(box.lineno, box.colno)
        sub.bounding_box = box
        return sub

    mock_window.create_new_window.side_effect = create_subwindow
    return mock_window


def setup_curses_mocks(*mocks):
    """Setup curses mocks with common configuration."""
    for mock_curses in mocks:
        mock_curses.curs_set = MagicMock()
        mock_curses.color_pair = MagicMock(return_value=1)
        mock_curses.error = curses.error
        mock_curses.A_NORMAL = 0
        mock_curses.A_BOLD = 1
        mock_curses.A_REVERSE = 2


class TestTextEventIntegration:
    """Test Text class event publishing."""

    def test_text_insert_publishes_event(self):
        """Test that Text.insert() publishes TextChangedEvent."""
        event_bus = EventBus()
        text = Text("", event_bus=event_bus)

        events = []

        def handler(event):
            events.append(event)

        event_bus.subscribe(TextChangedEvent, handler)

        # Insert text
        text.edit_mode = True
        text.insert("hello")

        # Should have published one event
        assert len(events) == 1
        assert isinstance(events[0], TextChangedEvent)
        assert events[0].change_type == "insert"
        assert events[0].text is text

    def test_text_backspace_publishes_event(self):
        """Test that Text.backspace() publishes TextChangedEvent."""
        event_bus = EventBus()
        text = Text("hello", event_bus=event_bus)

        events = []

        def handler(event):
            events.append(event)

        event_bus.subscribe(TextChangedEvent, handler)

        # Move to end and backspace
        text.edit_mode = True
        text.to_end_of_text()
        text.backspace()

        # Should have published one event
        assert len(events) == 1
        assert isinstance(events[0], TextChangedEvent)
        assert events[0].change_type == "delete"

    def test_text_replace_publishes_event(self):
        """Test that Text.replace_character() publishes TextChangedEvent."""
        event_bus = EventBus()
        text = Text("hello", event_bus=event_bus)

        events = []

        def handler(event):
            events.append(event)

        event_bus.subscribe(TextChangedEvent, handler)

        # Replace a character
        text.edit_mode = True
        text.to_start_of_text()
        text.replace_character("H")

        # Should have published one event
        assert len(events) == 1
        assert isinstance(events[0], TextChangedEvent)
        assert events[0].change_type == "replace"

    def test_text_without_event_bus_doesnt_crash(self):
        """Test that Text operations work without event bus."""
        text = Text("hello")  # No event_bus

        # These should not crash
        text.edit_mode = True
        text.insert(" world")
        text.backspace()
        text.replace_character("!")

        # After insert " world", backspace, replace "!", result should be "hell worl!"
        assert "hell worl!" == str(text)


class TestWorkspaceEventIntegration:
    """Test Workspace class event publishing."""

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_workspace_mode_changes_publish_events(
        self, mock_workspace_curses, mock_textbox_curses, mock_window_curses
    ):
        """Test that workspace mode changes publish ModeChangedEvents."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)
        event_bus = EventBus()

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr, event_bus=event_bus)

        events = []

        def handler(event):
            events.append(event)

        event_bus.subscribe(ModeChangedEvent, handler)

        # Initial mode is COMMAND, so no event yet
        assert len(events) == 0

        # Enter insert mode
        workspace.enter_insert_mode()
        assert len(events) == 1
        assert events[0].old_mode == INPUT_MODE.COMMAND
        assert events[0].new_mode == INPUT_MODE.INSERT

        # Enter command mode
        workspace.enter_command_mode()
        assert len(events) == 2
        assert events[1].old_mode == INPUT_MODE.INSERT
        assert events[1].new_mode == INPUT_MODE.COMMAND

        # Enter visual mode
        workspace.enter_visual_mode()
        assert len(events) == 3
        assert events[2].old_mode == INPUT_MODE.COMMAND
        assert events[2].new_mode == INPUT_MODE.VISUAL

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_workspace_i_key_publishes_mode_change(
        self, mock_workspace_curses, mock_textbox_curses, mock_window_curses
    ):
        """Test that pressing 'i' in command mode publishes ModeChangedEvent."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)
        event_bus = EventBus()

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr, event_bus=event_bus)

        events = []

        def handler(event):
            events.append(event)

        event_bus.subscribe(ModeChangedEvent, handler)

        # Press 'i' to enter insert mode
        await workspace.handle_keypress(ord('i'))

        assert len(events) == 1
        assert events[0].new_mode == INPUT_MODE.INSERT


class TestEventSystemUseCases:
    """Test real-world use cases for the event system."""

    def test_word_count_listener(self):
        """Test implementing a word count listener using events."""
        event_bus = EventBus()
        text = Text("", event_bus=event_bus)

        word_counts = []

        def on_text_changed(event):
            # Count words in the text
            text_str = str(event.text)
            word_count = len(text_str.split())
            word_counts.append(word_count)

        event_bus.subscribe(TextChangedEvent, on_text_changed)

        # Insert some text
        text.edit_mode = True
        text.insert("hello")
        assert word_counts[-1] == 1

        text.insert(" world")
        assert word_counts[-1] == 2

        text.insert(" foo bar")
        assert word_counts[-1] == 4

    def test_auto_save_listener(self):
        """Test implementing an auto-save listener using events."""
        event_bus = EventBus()
        text = Text("", event_bus=event_bus)

        save_calls = []

        def on_text_changed(event):
            # Simulate auto-save
            text_content = str(event.text)
            save_calls.append(text_content)

        event_bus.subscribe(TextChangedEvent, on_text_changed)

        # Make some changes
        text.edit_mode = True
        text.insert("draft")
        assert len(save_calls) == 1
        assert "draft" in save_calls[-1]

        text.insert(" content")
        assert len(save_calls) == 2
        assert "draft content" in save_calls[-1]

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_mode_indicator_listener(
        self, mock_workspace_curses, mock_textbox_curses, mock_window_curses
    ):
        """Test implementing a custom mode indicator using events."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)
        event_bus = EventBus()

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr, event_bus=event_bus)

        mode_log = []

        def on_mode_changed(event):
            mode_log.append({
                'from': event.old_mode.name,
                'to': event.new_mode.name
            })

        event_bus.subscribe(ModeChangedEvent, on_mode_changed)

        # Simulate mode changes
        workspace.enter_insert_mode()
        assert mode_log[-1] == {'from': 'COMMAND', 'to': 'INSERT'}

        workspace.enter_visual_mode()
        assert mode_log[-1] == {'from': 'INSERT', 'to': 'VISUAL'}

        workspace.enter_command_mode()
        assert mode_log[-1] == {'from': 'VISUAL', 'to': 'COMMAND'}

    @pytest.mark.asyncio
    @patch('textbox.ui.window.curses')
    @patch('textbox.ui.text_box.curses')
    @patch('textbox.ui.workspace.curses')
    async def test_command_execution_publishes_event(
        self, mock_workspace_curses, mock_textbox_curses, mock_window_curses
    ):
        """Test that executing commands publishes CommandExecutedEvent."""
        setup_curses_mocks(mock_workspace_curses, mock_textbox_curses, mock_window_curses)

        mock_window = create_mock_window()
        mock_input_mgr = MagicMock(spec=AsyncInputManager)
        event_bus = EventBus()

        workspace = InputOutputWorkspace(mock_window, mock_input_mgr, event_bus=event_bus)

        from textbox.core.events import CommandExecutedEvent
        events = []

        def handler(event):
            events.append(event)

        event_bus.subscribe(CommandExecutedEvent, handler)

        # Execute a command
        workspace.execute_command("help")

        assert len(events) == 1
        assert events[0].command_name == "help"
        assert events[0].args == "help"

    def test_text_events_propagate_from_workspace_boxes(self):
        """Test that text events from user_box/output_box are published."""
        from textbox.core.events import TextChangedEvent
        from textbox.ui.window import Window
        from textbox.ui.input_manager import AsyncInputManager
        from textbox.utils.box_types import BoundingBox, Dimensions

        # Create a real Window for this test
        with patch('textbox.ui.window.curses') as mock_curses, \
             patch('textbox.ui.text_box.curses') as mock_tb_curses, \
             patch('textbox.ui.workspace.curses') as mock_ws_curses:

            setup_curses_mocks(mock_curses, mock_tb_curses, mock_ws_curses)

            mock_window = create_mock_window()
            mock_input_mgr = MagicMock(spec=AsyncInputManager)
            event_bus = EventBus()

            workspace = InputOutputWorkspace(mock_window, mock_input_mgr, event_bus=event_bus)

            events = []

            def handler(event):
                events.append(event)

            event_bus.subscribe(TextChangedEvent, handler)

            # Insert text in user_box
            workspace.user_box.text.edit_mode = True
            workspace.user_box.text.insert("test")

            # Should have published event
            assert len(events) == 1
            assert events[0].change_type == "insert"

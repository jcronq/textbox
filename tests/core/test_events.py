"""Tests for event system (pub/sub pattern)."""

import pytest
import time
from textbox.core.events import (
    Event,
    EventBus,
    TextChangedEvent,
    ModeChangedEvent,
    CommandExecutedEvent,
)
from textbox.core.text import Text
from textbox.utils.box_types import Position


class TestEvent:
    """Test base Event class."""

    def test_event_has_timestamp(self):
        """Test that events have automatic timestamps."""
        event = Event()
        assert event.timestamp is not None
        assert isinstance(event.timestamp, float)
        assert event.timestamp <= time.time()

    def test_event_timestamp_can_be_provided(self):
        """Test that custom timestamp can be provided."""
        custom_time = 123456.789
        event = Event(timestamp=custom_time)
        assert event.timestamp == custom_time


class TestTextChangedEvent:
    """Test TextChangedEvent."""

    def test_text_changed_event_has_required_fields(self):
        """Test that TextChangedEvent has all required fields."""
        text = Text("hello")
        position = Position(0, 0)
        event = TextChangedEvent(
            text=text, change_type="insert", position=position
        )

        assert event.text is text
        assert event.change_type == "insert"
        assert event.position == position
        assert event.timestamp is not None

    def test_text_changed_event_supports_all_change_types(self):
        """Test that all change types are supported."""
        text = Text("test")
        position = Position(0, 0)

        for change_type in ["insert", "delete", "replace"]:
            event = TextChangedEvent(
                text=text, change_type=change_type, position=position
            )
            assert event.change_type == change_type


class TestModeChangedEvent:
    """Test ModeChangedEvent."""

    def test_mode_changed_event_has_required_fields(self):
        """Test that ModeChangedEvent has all required fields."""
        from textbox.ui.workspace import INPUT_MODE

        event = ModeChangedEvent(
            old_mode=INPUT_MODE.COMMAND, new_mode=INPUT_MODE.INSERT
        )

        assert event.old_mode == INPUT_MODE.COMMAND
        assert event.new_mode == INPUT_MODE.INSERT
        assert event.timestamp is not None


class TestCommandExecutedEvent:
    """Test CommandExecutedEvent."""

    def test_command_executed_event_has_required_fields(self):
        """Test that CommandExecutedEvent has all required fields."""
        event = CommandExecutedEvent(command_name="test", args="arg1 arg2")

        assert event.command_name == "test"
        assert event.args == "arg1 arg2"
        assert event.timestamp is not None


class TestEventBus:
    """Test EventBus pub/sub functionality."""

    def test_eventbus_can_be_created(self):
        """Test that EventBus can be instantiated."""
        bus = EventBus()
        assert bus is not None

    def test_subscribe_to_event_type(self):
        """Test subscribing to an event type."""
        bus = EventBus()
        called = []

        def handler(event):
            called.append(event)

        bus.subscribe(Event, handler)

        # Publish event
        event = Event()
        bus.publish(event)

        assert len(called) == 1
        assert called[0] is event

    def test_multiple_subscribers_called(self):
        """Test that multiple subscribers are all called."""
        bus = EventBus()
        called1 = []
        called2 = []

        def handler1(event):
            called1.append(event)

        def handler2(event):
            called2.append(event)

        bus.subscribe(Event, handler1)
        bus.subscribe(Event, handler2)

        event = Event()
        bus.publish(event)

        assert len(called1) == 1
        assert len(called2) == 1
        assert called1[0] is event
        assert called2[0] is event

    def test_different_event_types_separated(self):
        """Test that different event types don't interfere."""
        bus = EventBus()
        text_events = []
        mode_events = []

        def text_handler(event):
            text_events.append(event)

        def mode_handler(event):
            mode_events.append(event)

        bus.subscribe(TextChangedEvent, text_handler)
        bus.subscribe(ModeChangedEvent, mode_handler)

        # Publish text event
        text = Text("test")
        text_event = TextChangedEvent(
            text=text, change_type="insert", position=Position(0, 0)
        )
        bus.publish(text_event)

        assert len(text_events) == 1
        assert len(mode_events) == 0

        # Publish mode event
        from textbox.ui.workspace import INPUT_MODE

        mode_event = ModeChangedEvent(
            old_mode=INPUT_MODE.COMMAND, new_mode=INPUT_MODE.INSERT
        )
        bus.publish(mode_event)

        assert len(text_events) == 1
        assert len(mode_events) == 1

    def test_handler_exceptions_dont_stop_other_handlers(self):
        """Test that exception in one handler doesn't prevent others from running."""
        bus = EventBus()
        called_before = []
        called_after = []

        def handler_before(event):
            called_before.append(event)

        def handler_error(event):
            raise ValueError("Test error")

        def handler_after(event):
            called_after.append(event)

        bus.subscribe(Event, handler_before)
        bus.subscribe(Event, handler_error)
        bus.subscribe(Event, handler_after)

        event = Event()
        bus.publish(event)

        # Both handlers that don't throw should be called
        assert len(called_before) == 1
        assert len(called_after) == 1

    def test_publish_with_no_subscribers_doesnt_error(self):
        """Test that publishing with no subscribers doesn't cause error."""
        bus = EventBus()
        event = Event()
        bus.publish(event)  # Should not raise

    def test_unsubscribe_from_events(self):
        """Test that handlers can be unsubscribed."""
        bus = EventBus()
        called = []

        def handler(event):
            called.append(event)

        bus.subscribe(Event, handler)

        # Publish - should be called
        event1 = Event()
        bus.publish(event1)
        assert len(called) == 1

        # Unsubscribe
        bus.unsubscribe(Event, handler)

        # Publish again - should not be called
        event2 = Event()
        bus.publish(event2)
        assert len(called) == 1  # Still 1, not 2

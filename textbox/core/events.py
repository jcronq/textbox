"""Event system for textbox library.

Provides a simple pub/sub event system for extensibility and reactive features.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Any, Optional
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Base event class with automatic timestamp."""

    timestamp: Optional[float] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = time.time()


class TextChangedEvent(Event):
    """Fired when text changes.

    Attributes:
        text: The Text object that changed
        change_type: Type of change ('insert', 'delete', 'replace')
        position: Position where change occurred
        timestamp: Event timestamp
    """

    def __init__(self, text: Any, change_type: str, position: Any, timestamp: Optional[float] = None):
        """Initialize TextChangedEvent.

        Args:
            text: The Text object that changed
            change_type: Type of change ('insert', 'delete', 'replace')
            position: Position where change occurred
            timestamp: Optional timestamp (auto-generated if not provided)
        """
        super().__init__(timestamp=timestamp)
        self.text = text
        self.change_type = change_type
        self.position = position


class ModeChangedEvent(Event):
    """Fired when input mode changes.

    Attributes:
        old_mode: Previous INPUT_MODE
        new_mode: New INPUT_MODE
        timestamp: Event timestamp
    """

    def __init__(self, old_mode: Any, new_mode: Any, timestamp: Optional[float] = None):
        """Initialize ModeChangedEvent.

        Args:
            old_mode: Previous INPUT_MODE
            new_mode: New INPUT_MODE
            timestamp: Optional timestamp (auto-generated if not provided)
        """
        super().__init__(timestamp=timestamp)
        self.old_mode = old_mode
        self.new_mode = new_mode


class CommandExecutedEvent(Event):
    """Fired when a command is executed.

    Attributes:
        command_name: Name of the command executed
        args: Command arguments as string
        timestamp: Event timestamp
    """

    def __init__(self, command_name: str, args: str, timestamp: Optional[float] = None):
        """Initialize CommandExecutedEvent.

        Args:
            command_name: Name of the command executed
            args: Command arguments as string
            timestamp: Optional timestamp (auto-generated if not provided)
        """
        super().__init__(timestamp=timestamp)
        self.command_name = command_name
        self.args = args


class EventBus:
    """Simple pub/sub event system.

    Example:
        >>> bus = EventBus()
        >>> def on_text_change(event):
        ...     print(f"Text changed: {event.change_type}")
        >>> bus.subscribe(TextChangedEvent, on_text_change)
        >>> bus.publish(TextChangedEvent(...))
    """

    def __init__(self):
        """Initialize the event bus."""
        self._subscribers: Dict[type, List[Callable]] = {}

    def subscribe(self, event_type: type, handler: Callable) -> None:
        """Subscribe to events of a specific type.

        Args:
            event_type: The class of events to subscribe to
            handler: Callable that takes the event as parameter
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed {handler.__name__} to {event_type.__name__}")

    def unsubscribe(self, event_type: type, handler: Callable) -> None:
        """Unsubscribe a handler from events of a specific type.

        Args:
            event_type: The class of events to unsubscribe from
            handler: The handler to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Unsubscribed {handler.__name__} from {event_type.__name__}")
            except ValueError:
                # Handler wasn't subscribed, that's okay
                pass

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers.

        Args:
            event: The event to publish

        Note:
            If a handler raises an exception, it is logged but does not
            prevent other handlers from being called.
        """
        event_type = type(event)
        if event_type in self._subscribers:
            logger.debug(f"Publishing {event_type.__name__} to {len(self._subscribers[event_type])} subscribers")
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(
                        f"Event handler error in {handler.__name__}: {e}",
                        exc_info=True
                    )

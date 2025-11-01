# Event System

Textbox includes a powerful pub/sub event system that enables reactive programming, plugins, and extensibility.

## Table of Contents

- [Overview](#overview)
- [Event Types](#event-types)
- [EventBus](#eventbus)
- [Subscribing to Events](#subscribing-to-events)
- [Event Propagation](#event-propagation)
- [Use Cases](#use-cases)
- [Complete Examples](#complete-examples)
- [Best Practices](#best-practices)

---

## Overview

The event system allows you to react to changes in your application without tightly coupling components. When text changes, modes switch, or commands execute, events are published to subscribers.

### Key Benefits

- **Decouple components** - Event publishers don't know about subscribers
- **Enable plugins** - External code can subscribe to events
- **Reactive features** - Auto-save, word count, live preview, etc.
- **Debug and monitor** - Log all events for debugging
- **Optional** - Event system is opt-in, doesn't affect existing code

---

## Event Types

Textbox provides three built-in event types:

### TextChangedEvent

Published when text is modified in any Text object.

**Attributes:**
- `text: Text` - The Text object that changed
- `change_type: str` - Type of change: `"insert"`, `"delete"`, or `"replace"`
- `position: Position` - Cursor position where change occurred
- `timestamp: float` - Event timestamp (seconds since epoch)

**When Published:**
- After `Text.insert()` completes
- After `Text.backspace()` completes
- After `Text.replace_character()` completes

### ModeChangedEvent

Published when the input mode changes.

**Attributes:**
- `old_mode: INPUT_MODE` - Previous mode
- `new_mode: INPUT_MODE` - New mode
- `timestamp: float` - Event timestamp

**When Published:**
- After any mode transition:
  - COMMAND ↔ INSERT
  - COMMAND ↔ VISUAL
  - COMMAND → COMMAND_ENTRY
  - COMMAND → SEARCH_ENTRY
  - And all other transitions

### CommandExecutedEvent

Published when a command is executed.

**Attributes:**
- `command_name: str` - Name of the command (e.g., "help", "quit")
- `args: str` - Full command string including command name
- `timestamp: float` - Event timestamp

**When Published:**
- After `workspace.execute_command()` is called
- Includes both built-in commands (`:q`) and custom commands

---

## EventBus

The `EventBus` class implements the pub/sub pattern.

### Creating an EventBus

```python
from textbox.core.events import EventBus

event_bus = EventBus()
```

### EventBus Methods

#### `subscribe(event_type, handler)`

Subscribe a handler function to an event type.

**Parameters:**
- `event_type: type` - Event class to subscribe to
- `handler: Callable[[Event], None]` - Function that receives event

**Example:**
```python
def on_text_change(event):
    print(f"Text changed: {event.change_type}")

event_bus.subscribe(TextChangedEvent, on_text_change)
```

#### `unsubscribe(event_type, handler)`

Remove a handler from an event type.

**Parameters:**
- `event_type: type` - Event class
- `handler: Callable` - Handler to remove

**Example:**
```python
event_bus.unsubscribe(TextChangedEvent, on_text_change)
```

#### `publish(event)`

Publish an event to all subscribers.

**Parameters:**
- `event: Event` - Event instance to publish

**Note:** This is typically called internally by Textbox, not by users.

**Example:**
```python
from textbox.core.events import CommandExecutedEvent

event = CommandExecutedEvent(command_name="test", args="test arg")
event_bus.publish(event)
```

---

## Subscribing to Events

### Basic Subscription

```python
from textbox.core.events import EventBus, TextChangedEvent

event_bus = EventBus()

def on_text_change(event):
    print(f"Text changed via {event.change_type} at {event.position}")

event_bus.subscribe(TextChangedEvent, on_text_change)
```

### Multiple Subscribers

Multiple handlers can subscribe to the same event type:

```python
def handler1(event):
    print("Handler 1:", event.change_type)

def handler2(event):
    print("Handler 2:", event.change_type)

event_bus.subscribe(TextChangedEvent, handler1)
event_bus.subscribe(TextChangedEvent, handler2)

# Both handlers will be called when event is published
```

### Subscribing to Multiple Event Types

```python
from textbox.core.events import TextChangedEvent, ModeChangedEvent

def on_text_change(event):
    print(f"Text: {event.change_type}")

def on_mode_change(event):
    print(f"Mode: {event.old_mode.name} -> {event.new_mode.name}")

event_bus.subscribe(TextChangedEvent, on_text_change)
event_bus.subscribe(ModeChangedEvent, on_mode_change)
```

### Error Handling

If a handler raises an exception, it's logged but doesn't prevent other handlers from running:

```python
def buggy_handler(event):
    raise ValueError("Oops!")

def working_handler(event):
    print("This still runs")

event_bus.subscribe(TextChangedEvent, buggy_handler)
event_bus.subscribe(TextChangedEvent, working_handler)

# buggy_handler exception is logged, working_handler still executes
```

---

## Event Propagation

Events automatically propagate through the component hierarchy.

### Workspace Integration

When you create a workspace with an EventBus, it's passed to all components:

```python
from textbox.ui.workspace import InputOutputWorkspace
from textbox.core.events import EventBus

event_bus = EventBus()
workspace = InputOutputWorkspace(window, input_manager, event_bus=event_bus)

# The event_bus is now used by:
# - workspace.user_box.text
# - workspace.output_box.text
# - workspace.command_box.text
# - Any Text objects created by these boxes
```

### Text Object Integration

Create Text objects with an EventBus:

```python
from textbox import Text
from textbox.core.events import EventBus, TextChangedEvent

event_bus = EventBus()

# Subscribe before creating text
def on_change(event):
    print(f"Changed: {event.change_type}")

event_bus.subscribe(TextChangedEvent, on_change)

# Create text with event bus
text = Text("hello", event_bus=event_bus)

# Events will be published
text.edit_mode = True
text.insert(" world")  # Publishes TextChangedEvent
```

### App Integration

When using the `App` class, an EventBus is automatically created:

```python
import textbox

app = textbox.App()

# Access the event bus
from textbox.core.events import ModeChangedEvent

def on_mode_change(event):
    print(f"Mode changed to {event.new_mode.name}")

# Subscribe before starting
# Note: You need to access workspace after app starts
# See complete example below
```

---

## Use Cases

### 1. Word Count Tracker

Track word count as user types:

```python
from textbox.core.events import EventBus, TextChangedEvent

event_bus = EventBus()
word_count = [0]  # Use list to modify in closure

def update_word_count(event):
    text_str = str(event.text)
    word_count[0] = len(text_str.split())
    print(f"Word count: {word_count[0]}")

event_bus.subscribe(TextChangedEvent, update_word_count)
```

### 2. Auto-Save

Automatically save drafts when text changes:

```python
import json
from textbox.core.events import TextChangedEvent

def auto_save(event):
    text_content = str(event.text)
    with open("draft.txt", "w") as f:
        f.write(text_content)
    print("Draft saved")

event_bus.subscribe(TextChangedEvent, auto_save)
```

### 3. Mode Indicator

Display current mode in a custom way:

```python
from textbox.core.events import ModeChangedEvent

mode_log = []

def track_modes(event):
    mode_log.append({
        'from': event.old_mode.name,
        'to': event.new_mode.name,
        'time': event.timestamp
    })

event_bus.subscribe(ModeChangedEvent, track_modes)
```

### 4. Command Logging

Log all executed commands:

```python
from textbox.core.events import CommandExecutedEvent
import logging

logger = logging.getLogger("commands")

def log_command(event):
    logger.info(f"Command executed: {event.command_name} ({event.args})")

event_bus.subscribe(CommandExecutedEvent, log_command)
```

### 5. Live Character Count

Display character count with color coding:

```python
from textbox.core.events import TextChangedEvent

def character_count(event):
    char_count = len(str(event.text))
    if char_count > 280:
        print(f"Characters: {char_count} (over limit!)")
    else:
        print(f"Characters: {char_count}")

event_bus.subscribe(TextChangedEvent, character_count)
```

---

## Complete Examples

### Example 1: Enhanced Echo App with Events

```python
import textbox
from textbox.core.events import TextChangedEvent, ModeChangedEvent, CommandExecutedEvent

app = textbox.App()

# Statistics tracking
stats = {
    'edits': 0,
    'mode_changes': 0,
    'commands': 0
}

def on_text_change(event):
    stats['edits'] += 1

def on_mode_change(event):
    stats['mode_changes'] += 1

def on_command(event):
    stats['commands'] += 1

@app.on_submit
def handle_input(text):
    app.print(f"You said: {text}")

@app.command("stats", help="Show statistics")
def show_stats(cmd):
    app.print(f"Edits: {stats['edits']}")
    app.print(f"Mode changes: {stats['mode_changes']}")
    app.print(f"Commands: {stats['commands']}")

@app.command("quit", help="Exit")
def quit_app(cmd):
    app.stop()

if __name__ == "__main__":
    # Subscribe to events after app is created
    # The workspace (which has the event_bus) is created in app.start()
    # So we need a way to access it

    # For now, you'd need to access app.workspace.event_bus after start
    # Or pass event_bus to App (future enhancement)

    app.start()
```

### Example 2: Text with Event Bus

```python
from textbox import Text
from textbox.core.events import EventBus, TextChangedEvent

# Create event bus
event_bus = EventBus()

# Track changes
changes = []

def track_changes(event):
    changes.append({
        'type': event.change_type,
        'position': event.position,
        'timestamp': event.timestamp
    })

event_bus.subscribe(TextChangedEvent, track_changes)

# Create text with event bus
text = Text("hello", event_bus=event_bus)
text.edit_mode = True

# Make changes - all will be tracked
text.insert(" world")
text.to_end_of_text()
text.backspace()
text.backspace()

print(f"Total changes: {len(changes)}")
for change in changes:
    print(f"  {change['type']} at {change['position']}")
```

### Example 3: Multiple Event Handlers

```python
from textbox import Text
from textbox.core.events import EventBus, TextChangedEvent

event_bus = EventBus()

# Handler 1: Log to file
def log_to_file(event):
    with open("changes.log", "a") as f:
        f.write(f"{event.change_type} at {event.timestamp}\n")

# Handler 2: Update UI indicator
ui_state = {'last_change': None}

def update_ui(event):
    ui_state['last_change'] = event.change_type

# Handler 3: Trigger auto-save after 5 edits
edit_count = [0]

def auto_save_trigger(event):
    edit_count[0] += 1
    if edit_count[0] >= 5:
        print("Auto-saving...")
        edit_count[0] = 0

# Subscribe all handlers
event_bus.subscribe(TextChangedEvent, log_to_file)
event_bus.subscribe(TextChangedEvent, update_ui)
event_bus.subscribe(TextChangedEvent, auto_save_trigger)

# Create text - all handlers will be called
text = Text("", event_bus=event_bus)
text.edit_mode = True
text.insert("test")
```

---

## Best Practices

### 1. Subscribe Early

Subscribe to events before the components that will publish them are created:

```python
# Good
event_bus = EventBus()
event_bus.subscribe(TextChangedEvent, my_handler)
text = Text("", event_bus=event_bus)

# Also works, but might miss early events
text = Text("", event_bus=event_bus)
event_bus.subscribe(TextChangedEvent, my_handler)
```

### 2. Keep Handlers Fast

Event handlers are called synchronously. Keep them fast to avoid blocking:

```python
# Good - quick operation
def good_handler(event):
    state.counter += 1

# Bad - slow operation
def bad_handler(event):
    time.sleep(1)  # Blocks everything!
    save_to_database(event)  # Slow I/O

# Better - queue slow work
import queue
work_queue = queue.Queue()

def queue_handler(event):
    work_queue.put(event)  # Fast, non-blocking

# Process queue in background thread/task
```

### 3. Unsubscribe When Done

If you temporarily need an event subscription, unsubscribe when finished:

```python
def temporary_handler(event):
    print(event)

# Subscribe
event_bus.subscribe(TextChangedEvent, temporary_handler)

# Do work...

# Unsubscribe when done
event_bus.unsubscribe(TextChangedEvent, temporary_handler)
```

### 4. Handle Exceptions

Always handle potential exceptions in your handlers:

```python
def safe_handler(event):
    try:
        # Your code that might fail
        risky_operation(event)
    except Exception as e:
        logger.error(f"Handler error: {e}")
```

### 5. Don't Modify Event Objects

Events should be treated as read-only. Don't modify them:

```python
# Bad - modifying event
def bad_handler(event):
    event.timestamp = 0  # Don't do this!

# Good - read only
def good_handler(event):
    timestamp = event.timestamp
    process(timestamp)
```

### 6. Use Type Hints

Make your handlers type-safe:

```python
from textbox.core.events import TextChangedEvent

def my_handler(event: TextChangedEvent) -> None:
    text_content: str = str(event.text)
    change_type: str = event.change_type
```

---

## Integration with Vim Features

Events work seamlessly with vim operations:

### Visual Mode Events

```python
# Visual mode delete publishes TextChangedEvent("delete")
# Visual mode change publishes TextChangedEvent("delete") then mode change

def on_visual_operation(event):
    if event.change_type == "delete":
        print("Visual delete performed")

event_bus.subscribe(TextChangedEvent, on_visual_operation)
```

### Undo/Redo Events

```python
# Undo/redo operations publish appropriate TextChangedEvent

def track_undo_redo(event):
    # Both undo and redo publish text changed events
    # You can infer undo/redo from the pattern of changes
    pass
```

### Search Events

Search doesn't publish events currently, but mode changes do:

```python
def on_search_mode(event):
    if event.new_mode == INPUT_MODE.SEARCH_ENTRY:
        print("User started search")

event_bus.subscribe(ModeChangedEvent, on_search_mode)
```

---

## Future Enhancements

Potential future event types:

- `SearchExecutedEvent` - When search is performed
- `RegisterChangedEvent` - When register contents change
- `UndoEvent` / `RedoEvent` - Explicit undo/redo events
- `SelectionChangedEvent` - When visual selection changes
- `CursorMovedEvent` - When cursor moves

---

## Related Documentation

- [Vim Mode](vim-mode.md) - Learn about vim operations that publish events
- [API Reference](api-reference.md) - Complete event system API
- [Advanced Topics](advanced-topics.md) - Building plugins with events
- [Examples](examples.md) - Complete applications using events

---

## Troubleshooting

### Events Not Being Published

**Problem:** Handler never called

**Solutions:**
1. Verify EventBus was passed to Text/Workspace
2. Check that you subscribed to correct event type
3. Ensure subscription happened before events were published

```python
# Make sure event_bus is passed
text = Text("", event_bus=event_bus)  # ✓
text = Text("")  # ✗ No events published
```

### Handler Exceptions

**Problem:** Handler raises exception

**Solution:** EventBus logs exceptions but continues. Check logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Exceptions will be logged
```

### Memory Leaks

**Problem:** Subscribers not garbage collected

**Solution:** Unsubscribe handlers when done:

```python
event_bus.unsubscribe(TextChangedEvent, my_handler)
```

---

The event system enables powerful, reactive features while keeping your code decoupled and maintainable. Experiment with different use cases to see how it can enhance your applications!

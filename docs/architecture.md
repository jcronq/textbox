# Architecture & Internals

Understanding how Textbox works under the hood.

## Table of Contents

- [Overview](#overview)
- [Component Architecture](#component-architecture)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Text Rendering](#text-rendering)
- [Input Processing](#input-processing)
- [Event System](#event-system)
- [Extending Textbox](#extending-textbox)

---

## Overview

Textbox is built on top of Python's `curses` library and provides a high-level API for building terminal user interfaces with rich text support.

### Design Principles

1. **Simplicity**: Easy-to-use API for common use cases
2. **Flexibility**: Extensible for advanced scenarios
3. **Async-first**: Built with asyncio for responsive applications
4. **Separation of concerns**: Clear separation between display, input, and logic

### Technology Stack

- **Python 3.7+**: Core language
- **curses**: Terminal handling
- **asyncio**: Asynchronous I/O
- **Type hints**: For better IDE support and code clarity

---

## Component Architecture

```
┌─────────────────────────────────────────────┐
│                    App                      │
│  (High-level application interface)         │
└─────────────────┬───────────────────────────┘
                  │
                  ├── Event callbacks
                  │   ├── on_submit
                  │   └── commands
                  │
                  ├── Workspace management
                  │
┌─────────────────▼───────────────────────────┐
│          InputOutputWorkspace               │
│  (Split-screen layout manager)              │
└─────────┬───────────────────────┬───────────┘
          │                       │
┌─────────▼──────────┐  ┌────────▼──────────┐
│     InputBox       │  │     TextBox       │
│  (User input)      │  │  (Output display) │
└─────────┬──────────┘  └────────┬──────────┘
          │                      │
          └──────────┬───────────┘
                     │
          ┌──────────▼──────────┐
          │       Window        │
          │  (Curses wrapper)   │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │   AsyncInputManager │
          │  (Keyboard input)   │
          └─────────────────────┘
```

### Layer Responsibilities

1. **App Layer**: User-facing API, event management
2. **Workspace Layer**: Layout and coordination
3. **Box Layer**: Text display and input handling
4. **Window Layer**: Curses abstraction
5. **Input Layer**: Async keyboard handling

---

## Core Components

### 1. App Class

**Location**: `textbox/__init__.py`

**Purpose**: Main application interface

**Key Responsibilities**:
- Application lifecycle management
- Event callback registration
- Command registration and dispatch
- Convenient print interface

**Key Methods**:
```python
class App:
    def start()           # Start synchronously
    async def astart()    # Start asynchronously
    def print()           # Print to output
    def on_submit()       # Register submit callback
    def command()         # Register command
    def stop()            # Stop application
```

### 2. InputOutputWorkspace

**Location**: `textbox/input_output_workspace.py`

**Purpose**: Manages split-screen layout

**Key Responsibilities**:
- Layout calculation (output box vs input box)
- Focus management
- Mode switching (insert, normal, command)
- Coordinating input and output boxes

**Layout**:
```
┌─────────────────────────┐
│                         │
│    Output Box          │
│    (TextBox)           │
│                         │
├─────────────────────────┤
│    Input Box           │
│    (InputBox)          │
└─────────────────────────┘
```

### 3. TextBox

**Location**: `textbox/text_box.py`

**Purpose**: Display text output

**Key Responsibilities**:
- Rendering text with colors
- Scrolling
- Line wrapping
- Text buffer management

### 4. InputBox

**Location**: `textbox/input_box.py`

**Purpose**: Handle user text input

**Key Responsibilities**:
- Text editing
- Cursor management
- Submit handling
- Command detection

### 5. Text Hierarchy

**Locations**: `textbox/text.py`, `textbox/text_line.py`, `textbox/text_segment.py`

**Purpose**: Rich text representation

**Hierarchy**:
```python
Text                    # Document (multiple lines)
  └── TextLine[]        # Lines (no newlines)
      └── TextSegment[] # Colored segments
          └── str       # Raw text + color
```

### 6. Window

**Location**: `textbox/window.py`

**Purpose**: Curses abstraction

**Key Responsibilities**:
- Terminal initialization
- Color pair management
- Screen refresh
- Terminal size handling

### 7. AsyncInputManager

**Location**: `textbox/input_manager.py`

**Purpose**: Asynchronous keyboard input

**Key Responsibilities**:
- Non-blocking input reading
- Key event queue
- Input loop management

---

## Data Flow

### Startup Sequence

```
1. User calls app.start()
   │
2. curses_wrapper initializes terminal
   │
3. Window object created from stdscr
   │
4. AsyncInputManager started
   │
5. InputOutputWorkspace created
   │
6. InputBox and TextBox initialized
   │
7. Event loop starts
   │
8. Application ready for input
```

### Input Processing Flow

```
1. User types character
   │
2. AsyncInputManager captures key
   │
3. InputManager puts key in queue
   │
4. InputBox receives key
   │
5. InputBox updates internal Text
   │
6. InputBox refreshes display
   │
7. If Enter pressed:
   │
8. Submit callback invoked
   │
9. User's on_submit handler called
```

### Output Flow

```
1. User code calls app.print(text)
   │
2. App validates application is running
   │
3. Text converted to appropriate format
   │
4. Workspace.output_box.add_*() called
   │
5. TextBox appends to internal buffer
   │
6. TextBox calculates visible lines
   │
7. TextBox renders to curses window
   │
8. Window refreshes display
```

---

## Text Rendering

### Color System

Textbox uses curses color pairs:

```python
# Color pair initialization
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
# ... etc

# Usage in rendering
window.addstr("text", curses.color_pair(1))
```

**ColorCode** maps friendly names to color pair numbers:

```python
class ColorCode:
    WHITE = 0
    DARK_BLUE = 5
    # ... etc
```

### Rendering Pipeline

```
Text object
   │
   ├─ Apply max_line_width
   │  └─ Split into display lines
   │
   ├─ Apply color_pair defaults
   │
   └─ Convert to SegmentedTextLine[]
      │
      └─ For each segment:
         ├─ Get text string
         ├─ Get color pair
         └─ Call curses.addstr(text, color_pair)
```

### Line Wrapping

```python
# In TextLine.split_on_width()
def split_on_width(self, width):
    lines = []
    current_line = SegmentedTextLine()
    current_width = 0
    
    for segment in self._text.segments:
        if current_width + len(segment) > width:
            # Split segment and create new line
            # ...
        else:
            current_line.add_segment(segment)
            current_width += len(segment)
    
    return lines
```

---

## Input Processing

### Keyboard Handling

The `AsyncInputManager` uses a background thread to read input:

```python
class AsyncInputManager:
    def __init__(self, window):
        self._key_queue = asyncio.Queue()
        self._stop_event = threading.Event()
    
    def _input_thread(self):
        """Runs in background thread"""
        while not self._stop_event.is_set():
            key = self._window.get_key()
            asyncio.run_coroutine_threadsafe(
                self._key_queue.put(key),
                self._loop
            )
    
    async def get_key(self):
        """Async method to get next key"""
        return await self._key_queue.get()
```

### Key State Machine

**Location**: `textbox/key_state_machine.py`

Handles vim-like key sequences:

```
Normal mode:
  'i' → Insert mode
  ':' → Command mode
  'h', 'j', 'k', 'l' → Movement

Insert mode:
  ESC → Normal mode
  Characters → Insert
  
Command mode:
  ESC → Cancel
  Enter → Execute
```

---

## Event System

### Callback Registration

```python
class App:
    def __init__(self):
        self._submit_callbacks = []
        self._user_defined_commands = {}
    
    def on_submit(self, func):
        """Decorator to register submit handler"""
        self._submit_callbacks.append(func)
        return func
    
    def command(self, name, *alt_names, help=None):
        """Decorator to register command"""
        def decorator(func):
            self._user_defined_commands[name] = func
            for alt_name in alt_names:
                self._user_defined_commands[alt_name] = func
            return func
        return decorator
```

### Event Dispatch

```python
def _submit_callback(self, text):
    """Called when user submits text"""
    for func in self._submit_callbacks:
        func(text)

def _command_callback(self, command_str):
    """Called when user enters command"""
    command = command_str.split(" ")[0]
    if command in self._user_defined_commands:
        self._user_defined_commands[command](command_str)
```

---

## Extending Textbox

### Creating Custom Box Types

```python
from textbox.text_box import TextBox

class CustomBox(TextBox):
    """Custom box with special rendering"""
    
    def render_line(self, line, y_position):
        """Override rendering"""
        # Custom rendering logic
        super().render_line(line, y_position)
```

### Custom Input Handlers

```python
from textbox.input_box import InputBox

class CustomInputBox(InputBox):
    """Input box with autocomplete"""
    
    async def handle_key(self, key):
        """Override key handling"""
        if key == '\t':  # Tab
            self.autocomplete()
        else:
            await super().handle_key(key)
    
    def autocomplete(self):
        """Custom autocomplete logic"""
        pass
```

### Plugin System

```python
class Plugin:
    """Base plugin class"""
    def __init__(self, app):
        self.app = app
    
    def register(self):
        """Register plugin hooks"""
        raise NotImplementedError

class AutosavePlugin(Plugin):
    """Auto-save user input"""
    
    def __init__(self, app, filename):
        super().__init__(app)
        self.filename = filename
    
    def register(self):
        @self.app.on_submit
        def save_input(text):
            with open(self.filename, 'a') as f:
                f.write(str(text) + '\n')

# Usage
app = App()
autosave = AutosavePlugin(app, 'history.txt')
autosave.register()
```

---

## Performance Considerations

### Rendering Optimization

1. **Lazy rendering**: Only render visible lines
2. **Dirty flag**: Only refresh when content changes
3. **Batch updates**: Accumulate changes, then render

### Memory Management

1. **Circular buffer**: Limit output history
2. **Line pooling**: Reuse TextLine objects
3. **Segment merging**: Merge adjacent same-color segments

### Input Processing

1. **Async I/O**: Non-blocking input reading
2. **Event queue**: Decouple input from processing
3. **Throttling**: Limit update rate

---

## Testing Architecture

### Unit Testing

```python
# Mock curses for testing
import unittest
from unittest.mock import Mock

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.app.workspace = Mock()
    
    def test_command_registration(self):
        @self.app.command("test")
        def test_cmd(cmd):
            pass
        
        self.assertIn("test", self.app._user_defined_commands)
```

### Integration Testing

```python
# Test full application flow
async def test_full_flow():
    app = App()
    results = []
    
    @app.on_submit
    def capture(text):
        results.append(str(text))
    
    # Simulate user input
    app._submit_callback("test input")
    
    assert "test input" in results
```

---

## Debugging

### Logging Points

Key places to add logging:

1. **Input events**: Log each key press
2. **Rendering**: Log what's being rendered
3. **State changes**: Log mode changes, focus changes
4. **Callbacks**: Log when callbacks are invoked

### Debug Mode

```python
import logging

logging.basicConfig(
    filename='textbox_debug.log',
    level=logging.DEBUG
)

# Internal components will log if logger is configured
```

---

## Future Architecture Considerations

### Potential Improvements

1. **Widget system**: Reusable UI components
2. **Layout engine**: Flexible layouts (not just split)
3. **Theme system**: Customizable color schemes
4. **Plugin API**: Formalized plugin interface
5. **Event hooks**: More granular event system

### Scalability

For large-scale applications:

1. **Virtual scrolling**: Render only visible portion
2. **Lazy loading**: Load content on demand
3. **Background processing**: Offload heavy work to threads
4. **Caching**: Cache rendered output

---

## See Also

- [API Reference](api-reference.md) - Public API documentation
- [Advanced Topics](advanced-topics.md) - Advanced usage patterns

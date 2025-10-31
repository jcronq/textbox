# Advanced Topics

Advanced techniques and patterns for building sophisticated terminal applications with Textbox.

## Table of Contents

- [Async Integration](#async-integration)
- [Custom Input Handling](#custom-input-handling)
- [Workspace Management](#workspace-management)
- [State Management](#state-management)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)
- [Testing Textbox Applications](#testing-textbox-applications)
- [Building Plugins](#building-plugins)
- [Advanced Text Manipulation](#advanced-text-manipulation)

---

## Async Integration

Textbox supports asyncio for building responsive applications with background tasks.

### Using astart()

```python
import asyncio
import textbox

app = textbox.App()

@app.on_submit
def on_submit(text):
    app.print(f"You said: {text}")

async def main():
    await app.astart()

if __name__ == "__main__":
    asyncio.run(main())
```

### Running Background Tasks

```python
import asyncio
import textbox
from datetime import datetime

app = textbox.App()
running = True

async def clock():
    """Background task that updates time"""
    while running:
        await asyncio.sleep(1)
        if app.workspace:
            current_time = datetime.now().strftime("%H:%M:%S")
            # Note: Printing from background tasks can interfere with input
            # Consider using a status line instead

@app.command("quit")
def quit_app(cmd):
    global running
    running = False
    app.stop()

async def main():
    # Run app and background task concurrently
    await asyncio.gather(
        app.astart(),
        clock(),
        return_exceptions=True
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Async Event Handlers

While `on_submit` handlers are synchronous, you can dispatch async work:

```python
import asyncio
import textbox

app = textbox.App()

async def process_async(message):
    """Simulate async processing"""
    await asyncio.sleep(1)
    return f"Processed: {message}"

@app.on_submit
def on_submit(text):
    message = str(text)
    app.print(f"Processing '{message}'...")
    
    # Create task to run async processing
    async def handle():
        result = await process_async(message)
        if app.workspace:
            app.print(result)
    
    # Note: This won't work directly - need to run in event loop
    # Better to use thread or queue pattern
```

### Queue-Based Async Pattern

```python
import asyncio
import textbox
from asyncio import Queue

app = textbox.App()
message_queue = Queue()

@app.on_submit
def on_submit(text):
    # Put message in queue for async processing
    asyncio.create_task(message_queue.put(str(text)))

async def message_processor():
    """Process messages from queue"""
    while True:
        message = await message_queue.get()
        
        # Simulate async work
        await asyncio.sleep(0.5)
        
        if app.workspace:
            app.print(f"Processed: {message}")
        
        message_queue.task_done()

async def main():
    await asyncio.gather(
        app.astart(),
        message_processor(),
        return_exceptions=True
    )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Custom Input Handling

Access lower-level input management for custom behavior.

### Accessing the Workspace

```python
app = textbox.App()

@app.on_submit
def on_submit(text):
    # Access workspace components
    workspace = app.workspace
    
    # Input box
    input_box = workspace.input_box
    
    # Output box
    output_box = workspace.output_box
    
    # Focused box
    focused = workspace.focused_box
```

### Direct Window Access

For advanced use cases, access the curses window:

```python
from textbox import App
from textbox.window import Window
from textbox.input_manager import AsyncInputManager
from textbox.input_output_workspace import InputOutputWorkspace
import asyncio

async def custom_main():
    @curses_wrapper
    async def main(stdscr):
        window = Window(stdscr)
        async with AsyncInputManager(window) as input_manager:
            workspace = InputOutputWorkspace(window, input_manager)
            
            # Custom initialization
            workspace.enter_insert_mode()
            window.refresh()
            
            # Your custom logic here
            await asyncio.sleep(10)
    
    await main()
```

---

## Workspace Management

Understanding and controlling the input/output workspace.

### Workspace Layout

The workspace consists of:
- **Output box**: Display area (top)
- **Input box**: User input area (bottom)
- **Separator**: Divider between boxes

```python
@app.on_submit
def on_submit(text):
    workspace = app.workspace
    
    # Check if workspace is initialized
    if workspace is None:
        return
    
    # Access bounding boxes
    output_bounds = workspace.output_bounding_box
    input_bounds = workspace.input_bounding_box
```

### Mode Management

The workspace has different modes:

```python
# Insert mode - default, for typing
workspace.enter_insert_mode()

# Command mode - for entering commands
workspace.enter_command_mode()

# Normal mode - for navigation (vim-like)
workspace.enter_normal_mode()
```

---

## State Management

Patterns for managing application state.

### Singleton State Pattern

```python
import textbox

class AppState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.data = {}
            cls._instance.user = None
        return cls._instance

app = textbox.App()
state = AppState()

@app.on_submit
def on_submit(text):
    # Access shared state
    state.data[len(state.data)] = str(text)
    app.print(f"Stored item #{len(state.data)}")

@app.command("state")
def show_state(cmd):
    app.print(f"Items in state: {len(state.data)}")
```

### Class-Based Application

```python
import textbox
from textbox import ColorCode

class ChatApplication:
    def __init__(self):
        self.app = textbox.App()
        self.messages = []
        self.username = "User"
        
        # Register handlers
        self.app.on_submit(self.on_message)
        self.app.command("username", help="Set username")(self.set_username)
        self.app.command("quit")(self.quit)
    
    def on_message(self, text):
        message = str(text)
        self.messages.append((self.username, message))
        
        text.to_start_of_text()
        text.edit_mode = True
        text.insert(f"{self.username}: ")
        text.edit_mode = False
        text.color_pair = ColorCode.LIGHT_BLUE
        self.app.print(text)
    
    def set_username(self, cmd):
        parts = cmd.split(" ", 1)
        if len(parts) > 1:
            self.username = parts[1]
            self.app.print(f"Username set to: {self.username}")
    
    def quit(self, cmd):
        self.app.print(f"Total messages: {len(self.messages)}")
        self.app.stop()
    
    def run(self):
        self.app.start()

if __name__ == "__main__":
    chat = ChatApplication()
    chat.run()
```

### Context Manager Pattern

```python
import textbox
from contextlib import contextmanager

@contextmanager
def with_color(app, color):
    """Temporarily set output color"""
    # Save current state
    # ... (would need to save workspace state)
    
    try:
        yield
    finally:
        # Restore state
        pass

app = textbox.App()

@app.command("test")
def test(cmd):
    with with_color(app, ColorCode.LIGHT_BLUE):
        app.print("This is blue")
    app.print("This is normal")
```

---

## Error Handling

Robust error handling strategies.

### Graceful Error Recovery

```python
import textbox
from textbox import ColorCode

app = textbox.App()

def safe_execute(func, *args, **kwargs):
    """Execute function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        app.print(
            f"Error: {type(e).__name__}: {str(e)}",
        )
        return None

@app.on_submit
def on_submit(text):
    safe_execute(process_input, text)

def process_input(text):
    # This can raise exceptions
    value = int(str(text))
    app.print(f"Number: {value * 2}")
```

### Logging Integration

```python
import textbox
import logging

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = textbox.App()

@app.on_submit
def on_submit(text):
    try:
        logger.info(f"User input: {text}")
        # Process input
        app.print(f"Processed: {text}")
    except Exception as e:
        logger.exception("Error processing input")
        app.print(f"An error occurred. Check logs.")
```

### Validation Patterns

```python
import textbox

app = textbox.App()

def validate_input(text):
    """Validate user input"""
    errors = []
    
    if len(text) == 0:
        errors.append("Input cannot be empty")
    
    if len(text) > 100:
        errors.append("Input too long (max 100 characters)")
    
    return errors

@app.on_submit
def on_submit(text):
    errors = validate_input(str(text))
    
    if errors:
        app.print("Validation errors:")
        for error in errors:
            app.print(f"  - {error}")
    else:
        app.print(f"Valid input: {text}")
```

---

## Performance Optimization

Tips for optimizing Textbox applications.

### Minimize Printing

```python
# ✗ Bad - prints each item separately
for i in range(100):
    app.print(f"Item {i}")

# ✓ Good - batch into one print
output = "\n".join(f"Item {i}" for i in range(100))
app.print(output)
```

### Lazy Text Construction

```python
from textbox import Text

# ✓ Good - construct text before printing
text = Text()
text.text = "\n".join(lines)
app.print(text)

# ✗ Less efficient - multiple operations
for line in lines:
    text = Text(line)
    app.print(text)
```

### Limit Output History

```python
# Keep track of output and limit it
max_lines = 1000
output_history = []

@app.on_submit
def on_submit(text):
    output_history.append(str(text))
    
    # Keep only recent history
    if len(output_history) > max_lines:
        output_history.pop(0)
    
    app.print(text)
```

---

## Testing Textbox Applications

Strategies for testing terminal applications.

### Unit Testing Commands

```python
import unittest
import textbox

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = textbox.App()
        self.outputs = []
        
        # Mock print to capture output
        self.original_print = self.app.print
        self.app.print = lambda x: self.outputs.append(str(x))
    
    def tearDown(self):
        self.app.print = self.original_print
    
    def test_command_registration(self):
        @self.app.command("test")
        def test_cmd(cmd):
            self.app.print("test executed")
        
        # Manually invoke command callback
        self.app._command_callback(":test")
        
        self.assertIn("test executed", self.outputs)

if __name__ == "__main__":
    unittest.test()
```

### Integration Testing

```python
import textbox
from unittest.mock import Mock, patch

def test_app_flow():
    app = textbox.App()
    results = []
    
    @app.on_submit
    def on_submit(text):
        results.append(str(text))
    
    # Simulate user input
    app._submit_callback("test input")
    
    assert "test input" in results
```

---

## Building Plugins

Create reusable components for Textbox applications.

### Plugin System

```python
import textbox

class Plugin:
    """Base plugin class"""
    def __init__(self, app):
        self.app = app
    
    def register(self):
        """Register plugin commands and handlers"""
        raise NotImplementedError

class HistoryPlugin(Plugin):
    """Plugin that adds command history"""
    def __init__(self, app):
        super().__init__(app)
        self.history = []
    
    def register(self):
        @self.app.on_submit
        def track_history(text):
            self.history.append(str(text))
        
        @self.app.command("history", help="Show command history")
        def show_history(cmd):
            self.app.print("=== History ===")
            for i, item in enumerate(self.history, 1):
                self.app.print(f"{i}. {item}")

# Usage
app = textbox.App()
history = HistoryPlugin(app)
history.register()

app.start()
```

### Mixin Pattern

```python
import textbox

class LoggingMixin:
    """Add logging capability to app"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs = []
    
    def log(self, level, message):
        self.logs.append((level, message))
        self.print(f"[{level}] {message}")

class MyApp(LoggingMixin):
    def __init__(self):
        self.app = textbox.App()
        self.logs = []
    
    def print(self, text):
        self.app.print(text)
```

---

## Advanced Text Manipulation

Complex text processing techniques.

### Rich Text Builder

```python
from textbox import Text, TextLine
from textbox.colored import dark_blue, light_purple

class RichTextBuilder:
    """Builder for complex rich text"""
    def __init__(self):
        self.lines = []
    
    def add_header(self, text):
        self.lines.append(TextLine([dark_blue(text)]))
        return self
    
    def add_body(self, text):
        self.lines.append(TextLine(text))
        return self
    
    def add_footer(self, text):
        self.lines.append(TextLine([light_purple(text)]))
        return self
    
    def add_separator(self):
        self.lines.append(TextLine("-" * 40))
        return self
    
    def build(self):
        return self.lines

# Usage
builder = RichTextBuilder()
output = (builder
    .add_header("Important Message")
    .add_separator()
    .add_body("This is the message content")
    .add_body("With multiple lines")
    .add_separator()
    .add_footer("End of message")
    .build())

for line in output:
    app.print(line)
```

### Text Templates

```python
from textbox import TextLine
from textbox.colored import dark_blue, light_purple

class Template:
    @staticmethod
    def user_message(username, message):
        return TextLine([
            dark_blue(f"{username}: "),
            light_purple(message)
        ])
    
    @staticmethod
    def system_message(message):
        return TextLine([
            dark_blue("System: "),
            message
        ])
    
    @staticmethod
    def error_message(message):
        from textbox import ColorCode
        return TextLine(
            f"Error: {message}",
            default_color_pair=ColorCode.DARK_RED
        )

# Usage
app.print(Template.user_message("Alice", "Hello!"))
app.print(Template.system_message("User Alice joined"))
app.print(Template.error_message("Connection timeout"))
```

### Text Transformations

```python
from textbox import Text

class TextTransform:
    @staticmethod
    def uppercase(text: Text) -> Text:
        """Convert text to uppercase"""
        new_text = text.copy()
        new_text.text = str(text).upper()
        return new_text
    
    @staticmethod
    def word_count(text: Text) -> int:
        """Count words in text"""
        return len(str(text).split())
    
    @staticmethod
    def truncate(text: Text, max_length: int) -> Text:
        """Truncate text to max length"""
        content = str(text)
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        new_text = Text(content)
        return new_text

# Usage
@app.on_submit
def on_submit(text):
    word_count = TextTransform.word_count(text)
    app.print(f"Words: {word_count}")
    
    if word_count > 10:
        text = TextTransform.truncate(text, 50)
    
    app.print(text)
```

---

## Best Practices Summary

### 1. Structure Applications Well

```python
# ✓ Good - organized class-based structure
class Application:
    def __init__(self):
        self.app = textbox.App()
        self.state = {}
        self._setup_handlers()
    
    def _setup_handlers(self):
        self.app.on_submit(self.on_submit)
        # ... register other handlers
    
    def run(self):
        self.app.start()
```

### 2. Handle Errors Gracefully

```python
# ✓ Good - comprehensive error handling
@app.on_submit
def on_submit(text):
    try:
        process(text)
    except ValueError as e:
        app.print(f"Invalid input: {e}")
    except Exception as e:
        app.print(f"Unexpected error occurred")
        logger.exception(e)
```

### 3. Use Type Hints

```python
from textbox import App, Text
from typing import List

def format_messages(messages: List[str], app: App) -> None:
    for msg in messages:
        app.print(msg)
```

### 4. Document Commands

```python
@app.command("process", help="Process data (usage: :process <type> <value>)")
def process_cmd(cmd: str):
    """
    Process command with type and value
    
    Args:
        cmd: Full command string
    """
    # Implementation
    pass
```

---

## See Also

- [API Reference](api-reference.md) - Complete API documentation
- [Examples](examples.md) - Example applications
- [Text Handling](text-handling.md) - Working with text objects
- [Getting Started](getting-started.md) - Basic concepts

# Color Support

Learn how to add colors to your terminal applications with Textbox.

## Table of Contents

- [Introduction](#introduction)
- [ColorCode Class](#colorcode-class)
- [Using Color Helper Functions](#using-color-helper-functions)
- [Applying Colors](#applying-colors)
- [Creating Colored TextSegments](#creating-colored-textsegments)
- [Colored TextLines](#colored-textlines)
- [Setting Default Colors](#setting-default-colors)
- [Advanced Color Techniques](#advanced-color-techniques)

---

## Introduction

Textbox provides built-in color support for terminal applications using curses color pairs. Colors can be applied at different levels:

1. **TextSegment level**: Individual text segments with their own colors
2. **TextLine level**: Default color for an entire line
3. **Text level**: Default color for a document

---

## ColorCode Class

The `ColorCode` class provides predefined color constants.

### Available Colors

```python
from textbox import ColorCode

ColorCode.WHITE         # White text
ColorCode.GREY          # Grey text
ColorCode.DARK_RED      # Dark red text
ColorCode.GREEN         # Green text
ColorCode.YELLOW        # Yellow text
ColorCode.DARK_BLUE     # Dark blue text
ColorCode.DARK_PURPLE   # Dark purple text
ColorCode.LIGHT_BLUE    # Light blue text
ColorCode.LIGHT_PURPLE  # Light purple text
ColorCode.OFF_WHITE     # Off-white text
ColorCode.DEFAULT       # Default terminal color (None)
```

### Using ColorCode

```python
from textbox import Text, ColorCode

text = Text("This text is blue")
text.color_pair = ColorCode.LIGHT_BLUE
```

---

## Using Color Helper Functions

Textbox provides helper functions for creating colored text segments easily.

### Available Helper Functions

```python
from textbox.colored import (
    dark_blue,      # Dark blue text
    light_blue,     # Light blue text
    dark_purple,    # Dark purple text
    light_purple,   # Light purple text
)
```

### Creating Colored Segments

```python
from textbox.colored import dark_blue, light_purple

# Create colored segments
blue_text = dark_blue("This is blue")
purple_text = light_purple("This is purple")

# These return TextSegment objects
print(type(blue_text))  # <class 'TextSegment'>
```

---

## Applying Colors

### Method 1: Using Helper Functions (Recommended)

```python
from textbox import TextLine
from textbox.colored import dark_blue, light_purple

# Create a line with multiple colored segments
line = TextLine([
    dark_blue("User: "),
    light_purple("Hello, World!")
])

app.print(line)
```

### Method 2: Using TextSegment Directly

```python
from textbox import TextSegment, TextLine, ColorCode

# Create colored segments
prefix = TextSegment("User: ", ColorCode.DARK_BLUE)
message = TextSegment("Hello!", ColorCode.LIGHT_PURPLE)

# Combine into a line
line = TextLine([prefix, message])
app.print(line)
```

### Method 3: Setting Default Color

```python
from textbox import TextLine, ColorCode

# Entire line in one color
line = TextLine("This line is blue", default_color_pair=ColorCode.LIGHT_BLUE)
app.print(line)
```

---

## Creating Colored TextSegments

### Basic TextSegment Creation

```python
from textbox import TextSegment, ColorCode

# Plain segment (default color)
plain = TextSegment("Normal text")

# Colored segment
colored = TextSegment("Colored text", ColorCode.LIGHT_BLUE)

# Using helper
from textbox.colored import dark_blue
helper_colored = dark_blue("Helper colored")
```

### Combining TextSegments

```python
from textbox.colored import dark_blue, light_purple

# Segments must have same color to combine
seg1 = dark_blue("Hello ")
seg2 = dark_blue("World")
combined = seg1 + seg2  # TextSegment("Hello World", DARK_BLUE)

# Different colors cannot be combined directly
seg3 = light_purple("!")
# seg2 + seg3  # ValueError! Different colors
```

---

## Colored TextLines

### Creating Multi-Colored Lines

```python
from textbox import TextLine
from textbox.colored import dark_blue, light_purple, light_blue

# Mix multiple colors in one line
line = TextLine([
    dark_blue("INFO"),
    " | ",
    light_blue("Module: "),
    light_purple("auth"),
])

app.print(line)
```

### List of Colored Lines

```python
from textbox import TextLine
from textbox.colored import dark_blue, light_purple

lines = [
    TextLine([dark_blue("User 1: "), light_purple("Hello!")]),
    TextLine([dark_blue("User 2: "), light_purple("Hi there!")]),
    TextLine(),  # Empty line
]

app.print(lines)
```

---

## Setting Default Colors

### For Text Objects

```python
from textbox import Text, ColorCode

text = Text("This entire text is blue")
text.color_pair = ColorCode.LIGHT_BLUE

# When printed, all lines inherit this color
app.print(text)
```

### For TextLine Objects

```python
from textbox import TextLine, ColorCode

line = TextLine("Status: OK", default_color_pair=ColorCode.GREEN)
app.print(line)
```

### In Submit Handlers

```python
@app.on_submit
def on_submit(text):
    # User input text object
    text.color_pair = ColorCode.LIGHT_BLUE
    app.print(text)
```

---

## Advanced Color Techniques

### Conditional Coloring

```python
from textbox import TextLine, ColorCode
from textbox.colored import dark_blue, light_purple

def format_status(status, message):
    if status == "error":
        color = ColorCode.DARK_RED
        prefix = "ERROR"
    elif status == "warning":
        color = ColorCode.YELLOW
        prefix = "WARN"
    else:
        color = ColorCode.GREEN
        prefix = "INFO"
    
    return TextLine(
        f"{prefix}: {message}",
        default_color_pair=color
    )

app.print(format_status("error", "Connection failed"))
app.print(format_status("info", "All systems operational"))
```

### Syntax Highlighting

```python
from textbox import TextLine
from textbox.colored import dark_blue, light_purple

def highlight_code(code):
    """Simple syntax highlighting"""
    # Split into tokens (simplified)
    parts = []
    
    if "def" in code:
        parts.append(dark_blue("def "))
        parts.append(light_purple(code.replace("def ", "")))
    else:
        parts.append(code)
    
    return TextLine(parts)

app.print(highlight_code("def hello():"))
```

### Colored Tables

```python
from textbox import TextLine
from textbox.colored import dark_blue, light_blue

def print_table(headers, rows):
    # Header row
    header_line = TextLine([
        dark_blue(h.ljust(15)) for h in headers
    ])
    app.print(header_line)
    
    # Separator
    app.print("-" * (15 * len(headers)))
    
    # Data rows
    for row in rows:
        row_line = TextLine([
            light_blue(str(cell).ljust(15)) for cell in row
        ])
        app.print(row_line)

print_table(
    ["Name", "Age", "City"],
    [
        ["Alice", 30, "NYC"],
        ["Bob", 25, "LA"],
    ]
)
```

### Message Types

```python
from textbox import TextLine, ColorCode
from textbox.colored import dark_blue, light_purple, dark_purple

class MessageFormatter:
    @staticmethod
    def user_message(text):
        return TextLine([
            dark_blue("You: "),
            light_purple(text)
        ])
    
    @staticmethod
    def system_message(text):
        return TextLine([
            dark_purple("System: "),
            text
        ], default_color_pair=ColorCode.GREY)
    
    @staticmethod
    def error_message(text):
        return TextLine(
            f"Error: {text}",
            default_color_pair=ColorCode.DARK_RED
        )

app.print(MessageFormatter.user_message("Hello!"))
app.print(MessageFormatter.system_message("Welcome to the chat"))
app.print(MessageFormatter.error_message("Connection lost"))
```

---

## Complete Examples

### Example 1: Colored Chat Interface

```python
import textbox
from textbox import ColorCode
from textbox.colored import dark_blue, light_purple, dark_purple

app = textbox.App()

@app.on_submit
def on_message(text):
    # Format user message
    text.to_start_of_text()
    text.edit_mode = True
    text.insert(dark_blue("You: "))
    text.edit_mode = False
    text.color_pair = ColorCode.LIGHT_BLUE
    app.print(text)
    
    # Simulate bot response
    app.print(textbox.TextLine([
        dark_purple("Bot: "),
        light_purple("I received your message!")
    ]))
    app.print("")  # Empty line

if __name__ == "__main__":
    app.print(dark_blue("=== Chat Started ==="))
    app.print("")
    app.start()
```

### Example 2: Log Viewer

```python
import textbox
from textbox import TextLine, ColorCode

app = textbox.App()

def log(level, message):
    """Log a message with appropriate color"""
    colors = {
        "DEBUG": ColorCode.GREY,
        "INFO": ColorCode.LIGHT_BLUE,
        "WARNING": ColorCode.YELLOW,
        "ERROR": ColorCode.DARK_RED,
    }
    
    color = colors.get(level, ColorCode.DEFAULT)
    line = TextLine(
        f"[{level:8}] {message}",
        default_color_pair=color
    )
    app.print(line)

@app.on_submit
def on_command(text):
    log("INFO", f"Command received: {text}")

@app.command("error", help="Test error logging")
def test_error(cmd):
    log("ERROR", "This is a test error")

@app.command("warn", help="Test warning logging")
def test_warning(cmd):
    log("WARNING", "This is a test warning")

if __name__ == "__main__":
    log("INFO", "Application started")
    log("DEBUG", "Debug mode enabled")
    app.start()
```

### Example 3: Status Dashboard

```python
import textbox
from textbox import TextLine, ColorCode
from textbox.colored import dark_blue, light_blue, light_purple

app = textbox.App()

def print_status(service, status):
    """Print service status with color"""
    if status == "running":
        color = ColorCode.GREEN
        symbol = "✓"
    elif status == "stopped":
        color = ColorCode.DARK_RED
        symbol = "✗"
    else:
        color = ColorCode.YELLOW
        symbol = "?"
    
    app.print(TextLine([
        dark_blue(f"{service:20} "),
        TextLine(f"[{symbol}] {status}", default_color_pair=color)
    ]))

@app.command("status", help="Show service status")
def show_status(cmd):
    app.print("")
    app.print(dark_blue("=== Service Status ==="))
    print_status("Web Server", "running")
    print_status("Database", "running")
    print_status("Cache", "stopped")
    print_status("Queue", "running")
    app.print("")

if __name__ == "__main__":
    show_status("")
    app.start()
```

---

## Best Practices

### 1. Use Helper Functions for Readability

```python
# ✓ Good - clear and concise
from textbox.colored import dark_blue
line = TextLine([dark_blue("Label: "), "value"])

# ✗ Less readable
from textbox import TextSegment, ColorCode
line = TextLine([TextSegment("Label: ", ColorCode.DARK_BLUE), "value"])
```

### 2. Be Consistent with Colors

```python
# ✓ Good - consistent color scheme
USER_COLOR = ColorCode.LIGHT_BLUE
BOT_COLOR = ColorCode.LIGHT_PURPLE
ERROR_COLOR = ColorCode.DARK_RED

# Use throughout your app
```

### 3. Create Color Constants

```python
# ✓ Good - define once, use everywhere
class Colors:
    HEADER = ColorCode.DARK_BLUE
    BODY = ColorCode.LIGHT_BLUE
    ERROR = ColorCode.DARK_RED
    SUCCESS = ColorCode.GREEN

line = TextLine("Success!", default_color_pair=Colors.SUCCESS)
```

### 4. Don't Overuse Colors

```python
# ✓ Good - strategic use of color
line = TextLine([dark_blue("Status: "), "OK"])

# ✗ Too many colors - hard to read
from textbox.colored import dark_blue, light_blue, dark_purple, light_purple
line = TextLine([
    dark_blue("S"),
    light_blue("t"),
    dark_purple("a"),
    light_purple("t"),
    # ...
])
```

---

## Terminal Compatibility

### Color Support

Not all terminals support all colors. Textbox uses curses color pairs which should work on most modern terminals.

**Supported terminals:**
- Most Linux terminals (GNOME Terminal, KDE Konsole, etc.)
- macOS Terminal
- iTerm2
- Windows Terminal
- tmux/screen with 256 color support

**Testing colors:**

```bash
# Check color support
python examples/print_colors.py
```

---

## See Also

- [Text Handling](text-handling.md) - Working with text objects
- [API Reference](api-reference.md) - Complete API documentation
- [Examples](examples.md) - More color examples

# API Reference

Complete reference for all public APIs in the Textbox library.

## Table of Contents

- [App Class](#app-class)
- [Text Class](#text-class)
- [TextLine Class](#textline-class)
- [TextSegment Class](#textsegment-class)
- [ColorCode Class](#colorcode-class)
- [Colored Helper Functions](#colored-helper-functions)

---

## App Class

The main application class for creating terminal UIs.

### Constructor

```python
App()
```

Creates a new Textbox application instance.

**Example:**
```python
from textbox import App
app = App()
```

### Methods

#### `start()`

Starts the application synchronously.

**Signature:**
```python
def start() -> None
```

**Example:**
```python
app.start()
```

#### `astart()`

Starts the application asynchronously. Use this when integrating with async code.

**Signature:**
```python
async def astart() -> None
```

**Example:**
```python
await app.astart()
```

#### `print(text, end="\n")`

Prints text to the output box.

**Signature:**
```python
def print(
    text: Union[str, Text, List[SegmentedTextLine]], 
    end: str = "\n"
) -> None
```

**Parameters:**
- `text`: The text to print. Can be:
  - `str`: Plain string
  - `Text`: Rich text object
  - `List[SegmentedTextLine]`: List of colored text lines
  - `List[TextLine]`: List of text lines
- `end`: String to append after text (default: `"\n"`)

**Raises:**
- `ValueError`: If the application is not running or text type is invalid

**Example:**
```python
app.print("Hello, World!")
app.print(Text("Formatted text"))
app.print([TextLine("Line 1"), TextLine("Line 2")])
```

#### `stop()`

Stops the application and exits.

**Signature:**
```python
def stop() -> None
```

**Raises:**
- `WindowQuit`: Signal to terminate the application

**Example:**
```python
@app.command("quit")
def quit_command(cmd):
    app.stop()
```

### Decorators

#### `@app.on_submit`

Registers a callback function to handle text submissions.

**Signature:**
```python
def on_submit(func: Callable[[Text], None]) -> Callable
```

**Parameters:**
- `func`: Callback function that takes a `Text` object

**Returns:**
- The original function (for chaining)

**Example:**
```python
@app.on_submit
def handle_input(text):
    app.print(f"You said: {text}")
```

#### `@app.command(name, *alt_names, help=None)`

Registers a command that users can invoke with `:commandname`.

**Signature:**
```python
def command(
    name: str, 
    *alt_names: str, 
    help: str = None
) -> Callable
```

**Parameters:**
- `name`: Primary command name
- `*alt_names`: Alternative names for the command
- `help`: Help text displayed in `:help` command

**Returns:**
- Decorator function

**Example:**
```python
@app.command("quit", "q", help="Exit the application")
def quit_cmd(command_str):
    app.stop()

@app.command("echo", help="Echo text")
def echo_cmd(command_str):
    parts = command_str.split(" ", 1)
    if len(parts) > 1:
        app.print(parts[1])
```

### Properties

#### `workspace`

Access to the input/output workspace. Only available after `start()` or `astart()` is called.

**Type:** `InputOutputWorkspace | None`

**Example:**
```python
# After app.start()
if app.workspace:
    # Access workspace properties
    pass
```

---

## Text Class

Rich text object with cursor manipulation and editing capabilities.

### Constructor

```python
Text(text: str = "", max_line_width: int = None)
```

**Parameters:**
- `text`: Initial text content (default: `""`)
- `max_line_width`: Maximum width for line wrapping (default: `None`)

**Example:**
```python
from textbox import Text

text = Text("Hello, World!")
text_wrapped = Text("Long text...", max_line_width=80)
```

### Properties

#### `text`

Get or set the text content.

**Type:** `str`

**Setter accepts:**
- `str`: Plain string
- `List[str]`: List of strings (one per line)
- `List[TextLine]`: List of TextLine objects
- `List[SegmentedTextLine]`: List of SegmentedTextLine objects

**Example:**
```python
text = Text()
text.text = "Hello\nWorld"
print(text.text)  # "Hello\nWorld"
```

#### `edit_mode`

Whether the text is in edit mode. In edit mode, cursor can be positioned after the last character.

**Type:** `bool`

**Example:**
```python
text = Text("Hello")
text.edit_mode = True
text.insert(" World")
```

#### `color_pair`

Default color pair for the text.

**Type:** `int | None`

**Example:**
```python
from textbox import Text, ColorCode

text = Text("Colored text")
text.color_pair = ColorCode.LIGHT_BLUE
```

#### `cursor_position`

Current cursor position with line wrapping considered.

**Type:** `Position` (namedtuple with `lineno` and `colno`)

**Read-only**

**Example:**
```python
pos = text.cursor_position
print(f"Line: {pos.lineno}, Column: {pos.colno}")
```

#### `line_ptr`

Current line number (0-indexed).

**Type:** `int`

**Read-only**

#### `column_ptr`

Current column number (0-indexed).

**Type:** `int`

**Read-only**

#### `lines`

Rendered lines with wrapping applied.

**Type:** `List[TextLine]`

**Read-only**

**Example:**
```python
text = Text("Hello\nWorld", max_line_width=80)
for line in text.lines:
    print(line)
```

#### `max_line_width`

Maximum line width for wrapping.

**Type:** `int | None`

**Example:**
```python
text.max_line_width = 80
```

#### `line_count`

Total number of lines with wrapping.

**Type:** `int`

**Read-only**

### Methods

#### `copy()`

Creates a deep copy of the text.

**Returns:** `Text`

**Example:**
```python
original = Text("Hello")
copy = original.copy()
```

#### `insert(text: str)`

Inserts text at the cursor position. Requires `edit_mode = True`.

**Parameters:**
- `text`: Text to insert

**Raises:**
- `RuntimeError`: If not in edit mode

**Example:**
```python
text = Text("Hello")
text.to_end_of_text()
text.edit_mode = True
text.insert(" World")
```

#### `backspace()`

Deletes the character before the cursor.

**Example:**
```python
text.backspace()
```

#### `erase()`

Clears all text and resets cursor to start.

**Example:**
```python
text.erase()
```

#### Cursor Movement Methods

##### `to_start_of_text()`
Move cursor to the beginning of text.

##### `to_end_of_text()`
Move cursor to the end of text.

##### `to_start_of_line()`
Move cursor to the beginning of current line.

##### `to_end_of_line()`
Move cursor to the end of current line.

##### `to_first_line()`
Move cursor to the first line.

##### `to_last_line()`
Move cursor to the last line.

##### `increment_line_ptr()`
Move cursor down one line.

##### `decrement_line_ptr()`
Move cursor up one line.

##### `increment_column_ptr()`
Move cursor right one character.

##### `decrement_column_ptr()`
Move cursor left one character.

##### `goto(position: Position)`
Move cursor to specific position.

**Parameters:**
- `position`: Position object with `lineno` and `colno`

**Example:**
```python
from textbox.box_types import Position

text = Text("Hello\nWorld")
text.to_end_of_text()
text.edit_mode = True
text.insert("!")

# Move to specific position
text.goto(Position(0, 0))
```

#### `start_of_next_word()`

Find the position of the next word.

**Returns:** `Position | None`

#### `start_of_previous_word()`

Find the position of the previous word.

**Returns:** `Position | None`

#### Text Manipulation Methods

##### `break_line()`
Break the current line at cursor position.

##### `insert_newline()`
Insert a newline at cursor position.

##### `delete_line()`
Delete the current line.

##### `replace_character(ch: str)`
Replace character at cursor with `ch`.

### Magic Methods

```python
str(text)      # Convert to string
len(text)      # Total character count
text[lineno]   # Get line by index
text in lineno # Check if line exists
```

---

## TextLine Class

Represents a single line of text (no newlines).

### Constructor

```python
TextLine(
    text: Union[str, TextSegment, List[TextSegment], SegmentedTextLine] = "",
    default_color_pair: int = ColorCode.DEFAULT
)
```

**Parameters:**
- `text`: Initial text content
- `default_color_pair`: Default color for the line

**Example:**
```python
from textbox import TextLine
from textbox.colored import dark_blue

# Plain text line
line1 = TextLine("Hello, World!")

# Colored text line
line2 = TextLine([dark_blue("Hello"), " World!"])

# With default color
line3 = TextLine("Colored", default_color_pair=ColorCode.LIGHT_BLUE)
```

### Properties

#### `text`

Get or set the line text.

**Type:** `SegmentedTextLine`

#### `default_color_pair`

Default color pair for the line.

**Type:** `int`

### Methods

#### `copy()`

Create a copy of the TextLine.

**Returns:** `TextLine`

#### `cursor_position(column_ptr: int, width: int = None)`

Get cursor position with wrapping.

**Parameters:**
- `column_ptr`: Column position
- `width`: Max width for wrapping

**Returns:** `Position`

#### `line_count(width: int)`

Number of lines this would take with given width.

**Parameters:**
- `width`: Maximum line width

**Returns:** `int`

#### `split_on_width(width: int)`

Split line into multiple lines at given width.

**Parameters:**
- `width`: Maximum line width

**Returns:** `List[SegmentedTextLine]`

#### `start_of_next_word(column_ptr: int, in_white_space: bool)`

Find start of next word.

**Returns:** `int | None`

#### `start_of_previous_word(column_ptr: int)`

Find start of previous word.

**Returns:** `int | None`

---

## TextSegment Class

A segment of text with a single color.

### Constructor

```python
TextSegment(text: str = None, color_pair: int = ColorCode.DEFAULT)
```

**Parameters:**
- `text`: Text content
- `color_pair`: Color code

**Example:**
```python
from textbox import TextSegment, ColorCode

segment = TextSegment("Hello", ColorCode.LIGHT_BLUE)
```

### Properties

#### `color_pair`

Color code for this segment.

**Type:** `int`

### Methods

#### `copy()`

Create a copy of the segment.

**Returns:** `TextSegment`

#### `split(split_str: str)`

Split segment by string.

**Returns:** `List[TextSegment]`

### Magic Methods

```python
str(segment)           # Convert to string
len(segment)           # Character count
segment[0]             # Index/slice access
segment1 + segment2    # Concatenate segments
segment1 == segment2   # Equality comparison
```

---

## ColorCode Class

Predefined color codes for terminal output.

### Color Constants

```python
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
ColorCode.DEFAULT       # Default terminal color
```

**Example:**
```python
from textbox import Text, ColorCode

text = Text("Hello")
text.color_pair = ColorCode.LIGHT_BLUE
```

---

## Colored Helper Functions

Helper functions to create colored TextSegments.

### `dark_blue(text: str)`

Create a dark blue text segment.

**Returns:** `TextSegment`

### `light_blue(text: str)`

Create a light blue text segment.

**Returns:** `TextSegment`

### `dark_purple(text: str)`

Create a dark purple text segment.

**Returns:** `TextSegment`

### `light_purple(text: str)`

Create a light purple text segment.

**Returns:** `TextSegment`

**Example:**
```python
from textbox import TextLine
from textbox.colored import dark_blue, light_purple

line = TextLine([
    dark_blue("User: "),
    light_purple("Hello, World!")
])
app.print(line)
```

---

## Type Definitions

### Position

Named tuple representing a position in text.

```python
Position = namedtuple('Position', ['lineno', 'colno'])
```

**Fields:**
- `lineno`: Line number (0-indexed)
- `colno`: Column number (0-indexed)

**Example:**
```python
from textbox.box_types import Position

pos = Position(lineno=5, colno=10)
```

---

## Exceptions

### `WindowQuit`

Signal exception raised when the application should terminate.

**Usage:**
```python
from textbox.signals import WindowQuit

# Raised by app.stop()
app.stop()  # Raises WindowQuit internally
```

---

## Module Exports

The main `textbox` module exports:

```python
from textbox import (
    App,           # Main application class
    Text,          # Rich text object
    TextLine,      # Single line of text
    TextSegment,   # Colored text segment
    ColorCode,     # Color constants
    InputBox,      # Input box component
    TextBox,       # Text box component
)
```

---

## Advanced Usage

### Custom Input Handling

For more control, you can access the workspace directly:

```python
app = App()

# After start(), workspace is available
# app.workspace.input_box  # Access input
# app.workspace.output_box # Access output
```

### Async Integration

```python
import asyncio
from textbox import App

app = App()

async def background_task():
    while True:
        await asyncio.sleep(1)
        if app.workspace:
            app.print("Tick")

async def main():
    await asyncio.gather(
        app.astart(),
        background_task()
    )

asyncio.run(main())
```

---

## See Also

- [Getting Started Guide](getting-started.md)
- [Text Handling](text-handling.md)
- [Color Support](color-support.md)
- [Examples](examples.md)
- [Advanced Topics](advanced-topics.md)

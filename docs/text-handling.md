# Text Handling

A comprehensive guide to manipulating and displaying text with Textbox.

## Table of Contents

- [Text Hierarchy](#text-hierarchy)
- [The Text Class](#the-text-class)
- [The TextLine Class](#the-textline-class)
- [The TextSegment Class](#the-textsegment-class)
- [Working with Text](#working-with-text)
- [Cursor Management](#cursor-management)
- [Text Manipulation](#text-manipulation)
- [Line Wrapping](#line-wrapping)

---

## Text Hierarchy

Textbox uses a hierarchical structure for text:

```
Text                    # Multi-line text document
└── TextLine[]          # Array of lines (no newlines within)
    └── TextSegment[]   # Array of colored segments
        └── str         # Raw text + color_pair
```

### Understanding the Layers

1. **TextSegment**: Smallest unit - a string with a single color
2. **TextLine**: A single line composed of one or more TextSegments
3. **Text**: A document composed of one or more TextLines

---

## The Text Class

The `Text` class represents a multi-line document with cursor manipulation capabilities.

### Creating Text Objects

```python
from textbox import Text

# Empty text
text = Text()

# From string
text = Text("Hello, World!")

# Multi-line from string
text = Text("Line 1\nLine 2\nLine 3")

# With line wrapping
text = Text("Very long line...", max_line_width=80)
```

### Basic Properties

```python
text = Text("Hello\nWorld")

# Get text as string
print(text.text)  # "Hello\nWorld"

# Get individual lines
for line in text.lines:
    print(line)  # TextLine objects

# Character count
print(len(text))  # 11 (including newline)

# Line count
print(text.line_count)  # 2
```

### Edit Mode

Edit mode determines whether the cursor can be positioned *after* the last character:

```python
text = Text("Hello")
text.to_end_of_text()

# In normal mode, cursor is on 'o' (last character)
print(text.column_ptr)  # 4

# In edit mode, cursor can be after 'o'
text.edit_mode = True
print(text.column_ptr)  # 5 (can insert here)
```

**When to use edit mode:**
- When inserting text: `edit_mode = True`
- When just navigating: `edit_mode = False`

---

## The TextLine Class

Represents a single line of text (guaranteed no newlines).

### Creating TextLines

```python
from textbox import TextLine
from textbox.colored import dark_blue, light_purple

# Plain text line
line1 = TextLine("Hello, World!")

# Colored segments
line2 = TextLine([
    dark_blue("User: "),
    light_purple("Hello!")
])

# With default color
from textbox import ColorCode
line3 = TextLine("Info", default_color_pair=ColorCode.LIGHT_BLUE)
```

### Working with TextLines

```python
line = TextLine("Hello, World!")

# Get text
print(str(line))  # "Hello, World!"

# Length
print(len(line))  # 13

# Copy
line_copy = line.copy()

# Line wrapping
wrapped_lines = line.split_on_width(5)
# Returns multiple SegmentedTextLine objects
```

---

## The TextSegment Class

Represents a string with a single color.

### Creating TextSegments

```python
from textbox import TextSegment, ColorCode

# Plain segment
seg1 = TextSegment("Hello")

# Colored segment
seg2 = TextSegment("Error", ColorCode.DARK_RED)

# Using helper functions
from textbox.colored import dark_blue
seg3 = dark_blue("Info: ")
```

### TextSegment Operations

```python
from textbox import TextSegment, ColorCode

seg = TextSegment("Hello, World!", ColorCode.LIGHT_BLUE)

# String conversion
print(str(seg))  # "Hello, World!"

# Length
print(len(seg))  # 13

# Indexing
print(seg[0])  # TextSegment("H", LIGHT_BLUE)

# Slicing
print(seg[0:5])  # TextSegment("Hello", LIGHT_BLUE)

# Concatenation (same color only)
seg1 = TextSegment("Hello ", ColorCode.GREEN)
seg2 = TextSegment("World", ColorCode.GREEN)
combined = seg1 + seg2  # TextSegment("Hello World", GREEN)
```

---

## Working with Text

### Setting Text Content

The `text` property accepts multiple formats:

```python
from textbox import Text, TextLine
from textbox.colored import dark_blue

text = Text()

# From string
text.text = "Hello\nWorld"

# From list of strings
text.text = ["Line 1", "Line 2", "Line 3"]

# From TextLine objects
text.text = [
    TextLine("Plain line"),
    TextLine([dark_blue("Colored"), " line"])
]
```

### Reading Text

```python
text = Text("Line 1\nLine 2\nLine 3")

# As string
full_text = text.text  # "Line 1\nLine 2\nLine 3"

# As lines
for line in text.lines:
    print(line)  # TextLine objects

# Get specific line
first_line = text[0]  # "Line 1"

# Current line
text.to_first_line()
current = text.current_line  # TextLine object
```

---

## Cursor Management

The `Text` class provides extensive cursor manipulation.

### Cursor Position

```python
text = Text("Hello\nWorld")

# Current position
pos = text.cursor_position
print(f"Line {pos.lineno}, Column {pos.colno}")

# Individual pointers
print(text.line_ptr)    # Current line number
print(text.column_ptr)  # Current column number
```

### Moving the Cursor

#### Line Movement

```python
text = Text("Line 1\nLine 2\nLine 3")

# Jump to lines
text.to_first_line()    # Move to line 0
text.to_last_line()     # Move to last line

# Increment/decrement
text.increment_line_ptr()  # Move down one line
text.decrement_line_ptr()  # Move up one line
```

#### Column Movement

```python
text = Text("Hello, World!")

# Jump within line
text.to_start_of_line()  # Column 0
text.to_end_of_line()    # Last character

# Increment/decrement
text.increment_column_ptr()  # Move right
text.decrement_column_ptr()  # Move left
```

#### Absolute Movement

```python
text = Text("Line 1\nLine 2\nLine 3")

# Jump anywhere
text.to_start_of_text()  # Beginning of document
text.to_end_of_text()    # End of document

# Jump to specific position
from textbox.box_types import Position
text.goto(Position(lineno=1, colno=5))
```

#### Word Movement

```python
text = Text("The quick brown fox")

# Find next word
pos = text.start_of_next_word()
if pos:
    text.goto(pos)

# Find previous word
pos = text.start_of_previous_word()
if pos:
    text.goto(pos)
```

---

## Text Manipulation

### Inserting Text

```python
text = Text("Hello")
text.to_end_of_text()
text.edit_mode = True
text.insert(" World")
print(text.text)  # "Hello World"

# Insert at specific position
text.goto(Position(0, 5))
text.edit_mode = True
text.insert(",")
print(text.text)  # "Hello, World"
```

### Deleting Text

```python
text = Text("Hello, World!")

# Backspace (delete before cursor)
text.to_end_of_text()
text.backspace()
print(text.text)  # "Hello, World"

# Delete entire line
text.delete_line()

# Clear all text
text.erase()
```

### Replacing Text

```python
text = Text("Hello")
text.to_start_of_text()
text.replace_character("h")  # Replace 'H' with 'h'
print(text.text)  # "hello"
```

### Line Manipulation

```python
text = Text("Hello World")
text.goto(Position(0, 5))

# Break line at cursor
text.break_line()
print(text.text)  # "Hello\n World"

# Insert newline
text.insert_newline()
```

---

## Line Wrapping

Control how text wraps with `max_line_width`.

### Setting Line Width

```python
text = Text("This is a very long line that needs to be wrapped")
text.max_line_width = 20

# Text wraps automatically when accessed via .lines
for line in text.lines:
    print(f"'{line}'")
# Output:
# 'This is a very long '
# 'line that needs to '
# 'be wrapped'
```

### Dynamic Wrapping

```python
text = Text("Short line\nAnother short line")

# No wrapping initially
print(text.line_count)  # 2

# Enable wrapping
text.max_line_width = 10
print(text.line_count)  # May be more if lines wrap

# Disable wrapping
text.max_line_width = None
print(text.line_count)  # Back to 2
```

### Cursor with Wrapping

When wrapping is enabled, cursor positions account for wrapped lines:

```python
text = Text("This is a long line", max_line_width=10)
text.to_end_of_text()

# Cursor position considers wrapping
pos = text.cursor_position
print(f"Visual position: Line {pos.lineno}, Col {pos.colno}")

# But actual line pointer doesn't change
print(f"Actual line: {text.line_ptr}")  # Still 0 (first line)
```

---

## Practical Examples

### Building a Message with Color

```python
from textbox import Text, TextLine, ColorCode
from textbox.colored import dark_blue, light_purple

# Create colored message
text = Text()
text.text = [
    TextLine([dark_blue("INFO: "), light_purple("System started")]),
    TextLine([dark_blue("TIME: "), light_purple("2024-01-01 12:00:00")]),
]

# Add to it
text.to_end_of_text()
text.edit_mode = True
text.insert("\nReady for input")
```

### Processing User Input

```python
@app.on_submit
def process_input(text):
    # text is already a Text object
    
    # Add prefix
    text.to_start_of_text()
    text.edit_mode = True
    text.insert(dark_blue("User: "))
    text.edit_mode = False
    
    # Optionally set color
    text.color_pair = ColorCode.LIGHT_BLUE
    
    # Print
    app.print(text)
```

### Building Multi-line Output

```python
from textbox import TextLine
from textbox.colored import dark_blue, light_purple

def format_message(sender, message):
    return [
        TextLine([dark_blue(f"{sender}: "), light_purple(message)]),
        TextLine(),  # Empty line
    ]

app.print(format_message("Alice", "Hello!"))
app.print(format_message("Bob", "Hi there!"))
```

### Text Navigation

```python
text = Text("The quick brown fox jumps over the lazy dog")

# Navigate by words
text.to_start_of_text()
while True:
    pos = text.start_of_next_word()
    if pos is None:
        break
    text.goto(pos)
    print(f"Word starts at column {pos.colno}")
```

---

## Best Practices

### 1. Use Edit Mode Appropriately

```python
# ✓ Good
text.edit_mode = True
text.insert("new text")
text.edit_mode = False

# ✗ Bad - will raise RuntimeError
text.insert("new text")  # edit_mode is False by default
```

### 2. Create TextLines for Colored Output

```python
from textbox import TextLine
from textbox.colored import dark_blue

# ✓ Good - mixing colored segments
line = TextLine([dark_blue("Label: "), "value"])

# ✗ Less flexible - single color
line = TextLine("Label: value", default_color_pair=ColorCode.DARK_BLUE)
```

### 3. Handle Empty Text

```python
text = Text()

# ✓ Good - check before accessing
if text.line_count > 0:
    current = text.current_line

# Handle empty text gracefully
if len(text) == 0:
    text.text = "Default content"
```

### 4. Copy Before Modifying

```python
# ✓ Good - preserve original
original = Text("Important data")
modified = original.copy()
modified.edit_mode = True
modified.insert(" - modified")

# ✗ Bad - modifies original
text.edit_mode = True
text.insert(" - oops")
```

### 5. Use Position Objects

```python
from textbox.box_types import Position

# ✓ Good - explicit and clear
pos = Position(lineno=2, colno=5)
text.goto(pos)

# ✗ Less clear - accessing private attributes
# text._line_ptr = 2
# text._column_ptr = 5
```

---

## Common Pitfalls

### 1. Forgetting Edit Mode

```python
text = Text("Hello")
text.to_end_of_text()
# Forgot: text.edit_mode = True
text.insert(" World")  # RuntimeError!
```

### 2. Modifying While Iterating

```python
# ✗ Bad - modifying while iterating
for line in text.lines:
    text.backspace()  # Undefined behavior!

# ✓ Good - copy first
lines = text.lines.copy()
for line in lines:
    # Safe to modify text now
    pass
```

### 3. Assuming Line Count

```python
# ✗ Bad - assuming single line
text = Text("Multiple\nLines")
print(text[0])  # Only gets first line!

# ✓ Good - check line count
for i in range(text.line_count):
    if i in text:
        print(text[i])
```

---

## See Also

- [API Reference](api-reference.md) - Complete API documentation
- [Color Support](color-support.md) - Working with colors
- [Examples](examples.md) - Complete example applications
- [Advanced Topics](advanced-topics.md) - Complex text manipulation

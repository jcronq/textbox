# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`textbox` is a Python library for formatting and displaying text in a terminal using the curses library. It provides a vim-like terminal user interface with multiple input modes, text rendering, and rich text support.

## Development Commands

### Installation
```bash
pip install -e .
```

### Running Examples
```bash
python3 examples/main.py          # Basic terminal interface
python3 examples/llm_interface.py # LLM chat interface example
python3 examples/print_colors.py  # Color rendering demo
```

### Running Tests
Tests use standard Python unittest framework:
```bash
python3 -m unittest discover textbox "*_test.py"
```

Individual test files can be run directly:
```bash
python3 textbox/text_test.py
python3 textbox/text_line_test.py
python3 textbox/box_types_test.py
```

### Code Formatting
The project uses Black with 119 character line length:
```bash
black --line-length 119 textbox/
```

### Version Management
```bash
make all              # Display current version from version.txt
make tag             # Create and push git tag for current version
```

## Architecture

### Core Application Flow

The `App` class in `textbox/__init__.py` is the main entry point:

1. **Initialization**: `App()` creates the application with empty callbacks
2. **Start**: `app.start()` or `app.astart()` initializes uvloop and curses, then calls `app.run()`
3. **Run Loop**: Creates `AsyncInputManager` and `InputOutputWorkspace`, enters insert mode, and begins event loop
4. **User Interaction**: `InputOutputWorkspace` handles keypresses and manages three boxes (input, output, command)
5. **Callbacks**: User-defined callbacks are invoked on submit or command entry

### Component Hierarchy

```
App (textbox/__init__.py)
├── Window (textbox/window.py)
│   └── Wraps curses.window with position/dimension tracking
│
├── AsyncInputManager (textbox/input_manager.py)
│   └── Async keyboard input handling
│
└── InputOutputWorkspace (textbox/input_output_workspace.py)
    ├── command_box (InputBox) - Status/command line at bottom
    ├── user_box (InputBox) - User input area (5 lines tall)
    └── output_box (TextBox) - Scrollable output area
```

### Text Abstraction Layers

The library uses a layered text abstraction system (from low to high level):

1. **TextSegment** (`textbox/text_segment.py`): A string with color/style attributes
2. **SegmentedTextLine** (`textbox/segmented_text_line.py`): A line composed of multiple TextSegments
3. **TextLine** (`textbox/text_line.py`): Single line of text with no newlines, supports cursor operations
4. **Text** (`textbox/text.py`): Multi-line text block with line/column pointers and edit operations

Each layer adds functionality:
- TextSegment: styling
- SegmentedTextLine: combines segments
- TextLine: cursor movement, word navigation, character operations
- Text: multi-line editing, insert/replace modes, text wrapping

### Box Types and Positioning

`textbox/box_types.py` defines coordinate system primitives:
- **Position**: (lineno, colno) - A point in terminal space
- **Dimensions**: (height, width) - Size specification
- **BoundingBox**: (lineno, colno, height, width) - Rectangular area
- **LineSpan**: (first_lineno, last_lineno) - Range of lines

### Input Modes

The workspace operates in vim-like modes (`INPUT_MODE` enum in `input_output_workspace.py:23`):

- **INSERT**: Edit text, cursor visible, characters insert at cursor
- **REPLACE**: Edit text, cursor visible, characters replace at cursor
- **COMMAND**: Navigate with vim keys (hjkl), cursor visible
- **COMMAND_ENTRY**: Entering commands with `:` prefix
- **READ_ONLY**: Viewing output box, cursor hidden

### Command System

The App provides a decorator-based command system:

```python
app = App()

@app.command("greet", "hello", help="Say hello")
def greet_command(cmd_str):
    app.print("Hello!")
```

Commands are triggered by typing `:command` in COMMAND_ENTRY mode. A default "help" command is automatically created from registered commands.

### Logging

The library uses Python's logging module extensively. Key loggers:
- Main logger configured in `input_output_workspace.py:16` writes to `textbox.log`
- Examples may write to `log.txt`
- Use `logger.info()`, `logger.debug()`, and `logger.exception()` for debugging

### Color System

Colors are defined in `textbox/color_code.py` and use curses color pairs. The `ColorCode` enum provides named constants for different text colors (WHITE, GREY, OUTPUT_TEXT, etc.).

## Key Implementation Details

### Async Architecture
- Uses `uvloop` for faster async event loop
- `AsyncInputManager` runs keyboard input in background task
- Curses operations remain synchronous but are called from async context

### Cursor Management
- Text objects maintain internal pointers (`_line_ptr`, `_column_ptr`)
- In edit mode, cursor can be at position `len(line)` (after last character)
- In command mode, cursor is bounded to `len(line) - 1`
- The `edit_mode` property enforces this constraint

### Window Resizing
- Terminal resize events trigger `curses.KEY_RESIZE`
- `InputOutputWorkspace.resize()` recalculates all box boundaries
- Uses `curses.update_lines_cols()` and `curses.resize_term()` to handle terminal changes

### Error Handling
- Curses errors are often caught and ignored (`except curses.error: pass`)
- This prevents crashes when writing to edge positions
- `WindowQuit` signal is raised to cleanly exit the application

## Common Patterns

### Creating an Application
```python
from textbox import App, Text, TextSegment, ColorCode

app = App()

@app.on_submit
def handle_input(text: str):
    app.print(f"You said: {text}")

@app.command("quit", "q", help="Exit application")
def quit_cmd(cmd):
    app.stop()

app.start()
```

### Rich Text Output
```python
# String output
app.print("Simple text")

# Text object with color
text = Text([TextLine([TextSegment("Colored", ColorCode.BLUE)])])
app.print(text)

# Multiple lines
app.print(["Line 1", "Line 2", "Line 3"])
```

## Repository Structure

- `textbox/` - Main library source code
- `examples/` - Usage examples and demos
- `textbox.bck/` - Legacy/backup code (not used)
- `version.txt` - Current version number
- `setup.py` - Package installation configuration
- `requirements.txt` - Dependencies: termcolor, pyyaml, uvloop

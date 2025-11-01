# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`textbox` is a Python library for formatting and displaying text in a terminal using the curses library. It provides a vim-like terminal user interface with multiple input modes, text rendering, and rich text support.

**Current Version**: 0.1.0
**Test Coverage**: 82.38% (329 tests passing)
**Status**: Production-ready foundation, actively developing v0.2.0 features

## Documentation Structure

### For Quick Context
- **DOCUMENTATION_GUIDE.md** - Navigation hub for all documentation
- **docs/PROJECT_HISTORY.md** - Consolidated project history and current state

### For Development Planning
- **claude-output/plan-v2/** - Current development plan
  - IMPROVEMENT_SUMMARY.md - Executive summary (start here)
  - IMPROVEMENT_PLAN.md - Detailed implementation guide
  - ROADMAP.md - Version planning and progress tracking

### For Historical Reference
- **archive/** - Historical progress reports and old reviews (reference only)

**IMPORTANT**: When creating new progress reports, plans, or summaries:
- Use `claude-output/plan-v2/` for current planning documents
- Update `docs/PROJECT_HISTORY.md` for major milestones
- Update `claude-output/plan-v2/ROADMAP.md` for progress tracking
- DO NOT create new progress reports in `docs/progress-reports/` (archived)
- DO NOT create standalone reports (consolidate into existing documents)

## Development Process - TDD (Test-Driven Development)

**CRITICAL**: Always use TDD principles when developing new features or improvements:

### TDD Workflow (Red-Green-Refactor)
1. **Write Tests First** (Red)
   - Write tests that describe the intended behavior
   - Tests should fail initially (red)
   - Tests document what the code should do

2. **Implement Code** (Green)
   - Write minimal code to make tests pass
   - Focus on making it work, not perfect
   - All tests should pass (green)

3. **Refactor** (if needed)
   - Clean up the code
   - Improve structure and readability
   - Tests must still pass

### Example TDD Session
```python
# Step 1: Write failing test
def test_window_resize_validates_dimensions():
    window = Window(...)
    with pytest.raises(ValueError) as exc:
        window.resize(BoundingBox(0, 0, -1, 80))
    assert "negative" in str(exc.value).lower()

# Step 2: Run test (should fail)
# pytest tests/ui/test_window.py::test_window_resize_validates_dimensions

# Step 3: Implement validation in Window.resize()
def resize(self, box: BoundingBox):
    if box.height < 0 or box.width < 0:
        raise ValueError(f"Dimensions cannot be negative")
    # ... rest of implementation

# Step 4: Run test (should pass)
# Step 5: Refactor if needed
```

### Why TDD for This Project
- **Prevents regressions**: Tests catch breaking changes
- **Documents behavior**: Tests show how code should work
- **Better design**: Writing tests first leads to better APIs
- **Confidence**: Refactor freely knowing tests will catch issues
- **High coverage**: Currently at 82%+ coverage, maintain this standard

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
Tests use pytest framework:
```bash
pytest tests/                          # Run all tests
pytest tests/ -v                       # Verbose output
pytest tests/ --cov=textbox           # With coverage report
pytest tests/ --cov=textbox --cov-report=html  # HTML coverage report
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
2. **Start**: `app.start()` or `app.astart()` initializes asyncio and curses, then calls `app.run()`
3. **Run Loop**: Creates `AsyncInputManager` and `InputOutputWorkspace`, enters insert mode, and begins event loop
4. **User Interaction**: `InputOutputWorkspace` handles keypresses and manages three boxes (input, output, command)
5. **Callbacks**: User-defined callbacks are invoked on submit or command entry

### Component Hierarchy

```
App (textbox/__init__.py)
├── Window (textbox/ui/window.py)
│   └── Wraps curses.window with position/dimension tracking
│
├── AsyncInputManager (textbox/ui/input_manager.py)
│   └── Async keyboard input handling
│
└── InputOutputWorkspace (textbox/ui/workspace.py)
    ├── command_box (InputBox) - Status/command line at bottom
    ├── user_box (InputBox) - User input area (5 lines tall)
    └── output_box (TextBox) - Scrollable output area
```

### Package Structure

The codebase is organized into three subpackages:

**textbox/core/** - Text abstraction layers (low to high level):
1. **TextSegment** - A string with color/style attributes
2. **SegmentedTextLine** - A line composed of multiple TextSegments
3. **TextLine** - Single line with cursor operations, word navigation
4. **Text** - Multi-line text with insert/replace modes, wrapping
5. **TextList** - Collection of Text objects

**textbox/ui/** - User interface components:
- **Window** - Curses window wrapper
- **TextBox** - Scrollable text display
- **InputBox** - Text input with history
- **InputManager** - Async keyboard input handling
- **Workspace** - Main UI coordinator with vim modes

**textbox/utils/** - Utility modules:
- **box_types.py** - Position, Dimensions, BoundingBox, LineSpan
- **color_code.py** - ColorCode IntEnum for colors
- **colors.py** - Color helper functions
- **curses_utils.py** - Curses initialization and cleanup
- **signals.py** - WindowQuit and DelayedRedraw signals

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
- Uses standard `asyncio` for event loop
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

```
textbox/
├── textbox/              # Main library source code
│   ├── core/            # Text abstraction layers
│   ├── ui/              # User interface components
│   └── utils/           # Utility modules
├── tests/               # Test suite (pytest)
│   ├── core/           # Core module tests
│   ├── ui/             # UI component tests
│   └── utils/          # Utility tests
├── examples/            # Usage examples and demos
├── docs/               # User documentation
│   └── PROJECT_HISTORY.md  # Consolidated project history
├── claude-output/      # Development planning
│   └── plan-v2/        # Current development plan
├── archive/            # Historical documentation (reference only)
├── pyproject.toml      # Package configuration
├── requirements.txt    # Dependencies: pyyaml
└── CLAUDE.md          # This file
```

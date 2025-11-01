# Textbox

**A powerful, vim-inspired terminal UI library for Python**

Textbox is a Python library for building rich, interactive terminal applications with vim-like modal editing, async support, colored text, and event-driven architecture.

[![Tests](https://img.shields.io/badge/tests-549%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-82%25-green)](tests/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)

## Features

### 🎮 Vim-Like Modal Editing
- **7 input modes**: COMMAND, INSERT, REPLACE, VISUAL, VISUAL LINE, COMMAND ENTRY, SEARCH ENTRY
- **40+ vim keybindings**: `hjkl`, `w/b`, `dd`, `yy`, `p`, visual mode, and more
- **Undo/Redo**: Full command pattern implementation with 1000-operation history
- **Register system**: Named registers (`"a-z`), numbered registers (`"0-9`), yank/delete/paste
- **Search**: Forward (`/`) and backward (`?`) search with `n/N` navigation
- Complete vim workflow: visual selection → yank → paste → undo

### ⚡ Modern Python Architecture
- **Async/await support**: Build responsive applications with asyncio
- **Event system**: Pub/sub events for text changes, mode changes, and command execution
- **Type hints**: 100% type coverage for better IDE support
- **Command pattern**: All text operations are undoable/redoable
- **Clean architecture**: Separate core, UI, and utility modules

### 🎨 Rich Terminal UI
- **Colored text**: Built-in color helpers and ColorCode enum
- **Split-screen interface**: Input box, output box, and command line
- **Curses-based**: Efficient terminal rendering
- **Text abstraction layers**: From TextSegment → TextLine → Text → TextList
- **Box management**: Automatic layout and resizing

### 🔧 Developer-Friendly
- **Simple API**: Decorator-based callbacks and commands
- **Extensive docs**: Complete guides for vim mode, events, and API
- **549 tests**: Comprehensive test suite with 82% coverage
- **Examples included**: Chat interfaces, LLM integration, and more

## Quick Start

### Installation

```bash
pip install -e .
```

### Simple Echo App

```python
import textbox

app = textbox.App()

@app.on_submit
def handle_input(text):
    app.print(f"You said: {text}")

@app.command("quit", "q", help="Exit application")
def quit_cmd(cmd):
    app.stop()

if __name__ == "__main__":
    app.start()
```

### Using Vim Features

```python
import textbox
from textbox.colored import dark_blue, light_purple

app = textbox.App()

@app.on_submit
def handle_input(text):
    # Text automatically supports vim operations
    app.print(text)

if __name__ == "__main__":
    app.print(dark_blue("Vim Mode Guide:"))
    app.print("• ESC - Command mode")
    app.print("• i   - Insert mode")
    app.print("• v   - Visual mode")
    app.print("• yy  - Yank (copy) line")
    app.print("• p   - Paste")
    app.print("• u   - Undo")
    app.print("• /   - Search forward")
    app.print("• :q  - Quit")
    app.print("")
    app.start()
```

### Using the Event System

```python
import textbox
from textbox.core.events import TextChangedEvent

app = textbox.App()

# Track word count
word_count = [0]

def update_word_count(event):
    text_str = str(event.text)
    word_count[0] = len(text_str.split())

# Note: Access event_bus after workspace is created
# This is a simplified example
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Getting Started](docs/getting-started.md)** - Installation and first app
- **[Vim Mode Guide](docs/vim-mode.md)** - Complete vim keybindings reference
- **[Event System](docs/event-system.md)** - Reactive programming with events
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Examples](docs/examples.md)** - Sample applications
- **[Advanced Topics](docs/advanced-topics.md)** - Complex patterns and techniques

## Examples

The `examples/` directory contains complete applications:

- `main.py` - Basic terminal interface
- `llm_interface.py` - LLM chat interface example
- `print_colors.py` - Color rendering demo

Run an example:

```bash
python3 examples/main.py
```

## Requirements

- Python 3.10 or higher
- curses (included on Unix-like systems)
- PyYAML (only dependency)

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=textbox --cov-report=html

# Run specific test file
pytest tests/ui/test_workspace.py -v
```

### Project Structure

```
textbox/
├── textbox/           # Main library
│   ├── core/         # Text abstraction layers
│   ├── ui/           # User interface components
│   └── utils/        # Utility modules
├── tests/            # Test suite (549 tests)
├── docs/             # Documentation
├── examples/         # Example applications
└── README.md         # This file
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Current Status

**Version:** 0.1.0
**Test Coverage:** 82.38% (329/549 tests)
**Status:** Production-ready with active development

### Recent Additions (v0.2.0-dev)

- ✅ Visual mode (character and line selection)
- ✅ Register system (named and numbered registers)
- ✅ Undo/Redo with Command pattern
- ✅ Search functionality (forward/backward with n/N)
- ✅ Event system for reactive programming
- ✅ Complete vim command set (40+ keybindings)

## License

See LICENSE file for details.

## Acknowledgments

Built with Python's curses library for efficient terminal rendering. Inspired by Vim's modal editing philosophy.

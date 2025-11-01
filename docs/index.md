# Textbox

**A powerful, vim-inspired terminal UI library for Python**

Textbox is a Python library for building rich, interactive terminal applications with vim-like modal editing, async support, colored text, and event-driven architecture.

<div class="grid cards" markdown>

-   :material-keyboard:{ .lg .middle } __Vim-Like Editing__

    ---

    7 input modes, 40+ keybindings, visual mode, registers, undo/redo, and search

    [:octicons-arrow-right-24: Learn vim mode](vim-mode.md)

-   :material-flash:{ .lg .middle } __Modern Architecture__

    ---

    Async/await support, event system, type hints, and clean separation of concerns

    [:octicons-arrow-right-24: See architecture](architecture.md)

-   :material-palette:{ .lg .middle } __Rich Terminal UI__

    ---

    Colored text, split-screen interface, and efficient curses-based rendering

    [:octicons-arrow-right-24: Color support](color-support.md)

-   :material-code-tags:{ .lg .middle } __Developer Friendly__

    ---

    Simple API, extensive docs, 556 tests, and 82% coverage

    [:octicons-arrow-right-24: Get started](getting-started.md)

</div>

## Features

### :material-gamepad: Vim-Like Modal Editing

- **7 input modes**: COMMAND, INSERT, REPLACE, VISUAL, VISUAL LINE, COMMAND ENTRY, SEARCH ENTRY
- **40+ vim keybindings**: `hjkl`, `w/b`, `dd`, `yy`, `p`, visual mode, and more
- **Undo/Redo**: Full command pattern implementation with 1000-operation history
- **Register system**: Named registers (`"a-z`), numbered registers (`"0-9`), yank/delete/paste
- **Search**: Forward (`/`) and backward (`?`) search with `n/N` navigation
- Complete vim workflow: visual selection → yank → paste → undo

### :material-lightning-bolt: Modern Python Architecture

- **Async/await support**: Build responsive applications with asyncio
- **Event system**: Pub/sub events for text changes, mode changes, and command execution
- **Type hints**: 100% type coverage for better IDE support
- **Command pattern**: All text operations are undoable/redoable
- **Clean architecture**: Separate core, UI, and utility modules

### :material-monitor: Rich Terminal UI

- **Colored text**: Built-in color helpers and ColorCode enum
- **Split-screen interface**: Input box, output box, and command line
- **Curses-based**: Efficient terminal rendering
- **Text abstraction layers**: From TextSegment → TextLine → Text → TextList
- **Box management**: Automatic layout and resizing

### :material-wrench: Developer-Friendly

- **Simple API**: Decorator-based callbacks and commands
- **Extensive docs**: Complete guides for vim mode, events, and API
- **556 tests**: Comprehensive test suite with 82% coverage
- **Examples included**: Chat interfaces, LLM integration, and more

## Quick Start

### Installation

```bash
pip install textbox
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
from textbox.colored import dark_blue

app = textbox.App()

@app.on_submit
def handle_input(text):
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
    app.start()
```

## Status

| Metric | Value |
|--------|-------|
| Version | 0.2.0 |
| Tests | 556 passing |
| Coverage | 82.38% |
| Status | Production-ready |

### Recent Additions (v0.2.0)

- ✅ Visual mode (character and line selection)
- ✅ Register system (named and numbered registers)
- ✅ Undo/Redo with Command pattern
- ✅ Search functionality (forward/backward with n/N)
- ✅ Event system for reactive programming
- ✅ Complete vim command set (40+ keybindings)
- ✅ Debug mode with overlay and logging
- ✅ Comprehensive documentation

## Next Steps

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __[Getting Started](getting-started.md)__

    Installation and your first application

-   :material-book-open-variant:{ .lg .middle } __[Vim Mode](vim-mode.md)__

    Complete reference for all keybindings

-   :material-code-json:{ .lg .middle } __[API Reference](api-reference.md)__

    Complete API documentation

-   :material-school:{ .lg .middle } __[Examples](examples.md)__

    Sample applications and patterns

</div>

## Requirements

- Python 3.10 or higher
- curses (included on Unix-like systems)
- PyYAML (only dependency)

## License

MIT License - see [LICENSE](https://github.com/jasoncronquist/textbox/blob/main/LICENSE) for details.

## Acknowledgments

Built with Python's curses library for efficient terminal rendering. Inspired by Vim's modal editing philosophy.

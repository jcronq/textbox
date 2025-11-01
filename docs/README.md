# Textbox Documentation

Welcome to the Textbox library documentation! Textbox is a Python library for building rich terminal user interfaces with curses, featuring async support, colored text, and vim-like editing capabilities.

## Table of Contents

### Getting Started
1. [Getting Started](getting-started.md) - Installation and first application
2. [Quick Start Guide](quick-start.md) - Quick examples to get running

### Core Features
3. [Vim Mode Reference](vim-mode.md) - **NEW!** Complete vim keybindings, modes, and features
4. [Event System](event-system.md) - **NEW!** Reactive programming with pub/sub events
5. [Text Handling](text-handling.md) - Working with Text objects
6. [Color Support](color-support.md) - Adding colors to your terminal UI

### Reference
7. [API Reference](api-reference.md) - Complete API documentation
8. [Examples](examples.md) - Sample applications
9. [Advanced Topics](advanced-topics.md) - Complex patterns and techniques
10. [Troubleshooting](troubleshooting.md) - Common issues and solutions

## What is Textbox?

Textbox is a terminal UI framework that provides:

- **Rich Text Support**: Display colored, segmented text in your terminal applications
- **Async/Await Support**: Build responsive applications with async input handling
- **Vim-like Editing**: Built-in text editing with familiar keyboard shortcuts
- **Input/Output Workspace**: Split-screen interface with input and output boxes
- **Command System**: Easy-to-use command registration and handling
- **Event Callbacks**: React to user input with submit and command callbacks

## Key Features

### 🎨 Colored Text
Create beautiful terminal UIs with built-in color support:
```python
from textbox import App, TextLine
from textbox.colored import dark_blue, light_purple

app = App()
app.print(TextLine([dark_blue("User: "), light_purple("Hello!")]))
```

### ⚡ Async Support
Build responsive applications with async/await:
```python
app = App()

@app.on_submit
def handle_input(text):
    app.print(f"You said: {text}")

app.start()  # Synchronous
# or
await app.astart()  # Asynchronous
```

### 🎯 Command System
Register custom commands with ease:
```python
@app.command("quit", "q", help="Exit the application")
def quit_command(command_str):
    app.stop()
```

### 📝 Rich Text Objects
Manipulate text with a powerful API:
```python
from textbox import Text

text = Text("Hello, World!")
text.to_end_of_text()
text.edit_mode = True
text.insert(" Welcome to Textbox!")
```

## Quick Example

Here's a simple chat-like application:

```python
import textbox
from textbox import ColorCode
from textbox.colored import dark_blue, light_purple

app = textbox.App()

@app.on_submit
def on_submit(text):
    # Add user prefix
    text.to_start_of_text()
    text.edit_mode = True
    text.insert(dark_blue("User: "))
    text.edit_mode = False
    text.color_pair = ColorCode.LIGHT_BLUE
    
    # Print user message
    app.print(text)
    
    # Print AI response
    app.print([
        textbox.TextLine([dark_purple("AI: "), light_purple("Hello!")]),
        textbox.TextLine(),
    ])

@app.command("quit", help="Exit the application")
def quit_cmd(command_str):
    app.print("Goodbye!")
    app.stop()

if __name__ == "__main__":
    app.start()
```

## Installation

```bash
pip install textbox
```

Or for development:

```bash
git clone https://github.com/yourusername/textbox.git
cd textbox
pip install -e .
```

## Requirements

- Python 3.7+
- curses (included in most Unix-like systems)
- asyncio

## Getting Help

- Read the [Getting Started Guide](getting-started.md)
- Check out [Examples](examples.md)
- Review the [API Reference](api-reference.md)

## License

See the LICENSE file in the repository root.

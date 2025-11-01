# Getting Started with Textbox

This guide will walk you through installing and using Textbox in your Python applications.

## Installation

### Using pip

```bash
pip install textbox
```

### From Source

```bash
git clone https://github.com/yourusername/textbox.git
cd textbox
pip install -e .
```

### Requirements

Textbox requires:
- Python 3.7 or higher
- curses library (pre-installed on most Unix-like systems)
- asyncio (included in Python 3.7+)

## Your First Textbox Application

Let's create a simple application that echoes user input:

```python
import textbox

# Create the application
app = textbox.App()

# Define what happens when user submits text
@app.on_submit
def handle_input(text):
    app.print(f"You said: {text}")

# Start the application
if __name__ == "__main__":
    app.start()
```

Save this as `hello.py` and run it:

```bash
python hello.py
```

You'll see a terminal interface with an input box at the bottom. Type some text and press Enter to see it echoed back.

## Understanding the Basics

### The App Class

The `App` class is the core of every Textbox application. It manages:
- The terminal window
- Input/output workspace
- Event callbacks
- Commands

```python
from textbox import App

app = App()
```

### Starting the Application

There are two ways to start your application:

1. **Synchronous** (recommended for most cases):
```python
app.start()
```

2. **Asynchronous** (when you need to integrate with other async code):
```python
await app.astart()
```

### Handling User Input

Use the `@app.on_submit` decorator to handle text submissions:

```python
@app.on_submit
def on_submit(text):
    # text is a Text object
    app.print(f"Received: {text}")
```

The `text` parameter is a `Text` object that you can manipulate before printing.

### Printing Output

The `app.print()` method accepts multiple types:

```python
# Print a string
app.print("Hello, World!")

# Print a Text object
from textbox import Text
text = Text("Formatted text")
app.print(text)

# Print TextLine objects
from textbox import TextLine
app.print([TextLine("Line 1"), TextLine("Line 2")])

# Print SegmentedTextLine objects (colored text)
from textbox import TextLine
from textbox.colored import dark_blue
app.print(TextLine([dark_blue("Colored text")]))
```

### Creating Commands

Commands are special inputs that start with `:` (like vim). Register them with the `@app.command` decorator:

```python
@app.command("quit", "q", help="Exit the application")
def quit_command(command_str):
    app.print("Goodbye!")
    app.stop()

@app.command("echo", help="Echo the arguments")
def echo_command(command_str):
    # command_str is ":echo hello world"
    parts = command_str.split(" ", 1)
    if len(parts) > 1:
        app.print(parts[1])
```

Users can type `:quit` or `:q` to quit, or `:echo hello world` to echo text.

## Basic Terminal Controls

While the application is running:

### Insert Mode (default)
- Type to enter text
- `Enter`: Submit text
- `Backspace`: Delete character
- `Ctrl+C`: Exit application

### Command Mode
- `:`: Enter command mode
- Type command name and arguments
- `Enter`: Execute command
- `ESC`: Cancel command

### Built-in Commands
- `:help`: Show available commands

## Next Steps

Now that you understand the basics:

1. Learn about [Text Handling](text-handling.md) to manipulate rich text
2. Explore [Color Support](color-support.md) to add colors to your output
3. Check out [Examples](examples.md) for complete applications
4. Dive into the [API Reference](api-reference.md) for detailed documentation
5. Read [Advanced Topics](advanced-topics.md) for complex use cases

## Common Patterns

### Echo Application

```python
import textbox

app = textbox.App()

@app.on_submit
def echo(text):
    app.print(text)

if __name__ == "__main__":
    app.start()
```

### Chat-like Interface

```python
import textbox
from textbox.colored import dark_blue, light_purple

app = textbox.App()

@app.on_submit
def on_message(text):
    text.to_start_of_text()
    text.edit_mode = True
    text.insert(dark_blue("User: "))
    text.edit_mode = False
    app.print(text)

if __name__ == "__main__":
    app.start()
```

### Command-based Application

```python
import textbox

app = textbox.App()

@app.command("greet", help="Greet someone")
def greet(command_str):
    parts = command_str.split(" ")
    if len(parts) > 1:
        name = parts[1]
        app.print(f"Hello, {name}!")
    else:
        app.print("Hello!")

@app.command("quit", help="Exit")
def quit_app(command_str):
    app.stop()

if __name__ == "__main__":
    app.start()
```

## Troubleshooting

### Terminal Not Displaying Correctly

If the terminal display is corrupted:
- Make sure your terminal supports curses
- Try resizing the terminal window
- Ensure you're not printing to stdout/stderr outside of `app.print()`

### Application Not Responding

- Check that you're using `app.start()` or `await app.astart()`
- Ensure your event handlers don't block for long periods
- Use async/await for long-running operations

### Import Errors

```python
# Correct imports
from textbox import App, Text, TextLine, TextSegment, ColorCode

# Not recommended (imports internal classes)
from textbox.input_output_workspace import InputOutputWorkspace
```

## Tips

1. **Always use `app.print()`** instead of regular `print()` when the app is running
2. **Commands start with `:`** - users type `:quit` not just `quit`
3. **Text objects are mutable** - manipulate them before printing
4. **The workspace is created on start** - don't access `app.workspace` before calling `app.start()`
5. **Edit mode matters** - enable `text.edit_mode = True` before inserting text

## Example: Complete Mini Application

```python
#!/usr/bin/env python3
"""
A simple note-taking application with Textbox
"""
import textbox
from textbox import ColorCode
from textbox.colored import dark_blue, light_purple

app = textbox.App()
notes = []

@app.on_submit
def add_note(text):
    # Store the note
    note_text = str(text)
    notes.append(note_text)
    
    # Display confirmation
    text.to_start_of_text()
    text.edit_mode = True
    text.insert(dark_blue("Note added: "))
    text.edit_mode = False
    text.color_pair = ColorCode.LIGHT_BLUE
    app.print(text)

@app.command("list", help="List all notes")
def list_notes(command_str):
    if not notes:
        app.print("No notes yet!")
    else:
        app.print(dark_blue("Your notes:"))
        for i, note in enumerate(notes, 1):
            app.print(f"{i}. {note}")

@app.command("clear", help="Clear all notes")
def clear_notes(command_str):
    notes.clear()
    app.print(light_purple("All notes cleared!"))

@app.command("quit", "q", help="Exit the application")
def quit_app(command_str):
    app.print(f"You created {len(notes)} notes. Goodbye!")
    app.stop()

if __name__ == "__main__":
    app.print(dark_blue("Welcome to Notes!"))
    app.print("Type notes and press Enter to save them.")
    app.print("Type :list to see your notes, :clear to delete all, :quit to exit.")
    app.print("")
    app.start()
```

You're now ready to build terminal applications with Textbox! Continue to the other documentation sections to learn more advanced features.

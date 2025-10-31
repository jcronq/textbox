# Quick Start Guide

Get up and running with Textbox in 5 minutes.

## Installation

```bash
pip install textbox
```

## Your First App (30 seconds)

Create a file called `hello.py`:

```python
import textbox

app = textbox.App()

@app.on_submit
def on_submit(text):
    app.print(f"You said: {text}")

if __name__ == "__main__":
    app.start()
```

Run it:

```bash
python hello.py
```

Type something and press Enter!

## Add Colors (1 minute)

```python
import textbox
from textbox.colored import dark_blue, light_purple

app = textbox.App()

@app.on_submit
def on_submit(text):
    app.print(textbox.TextLine([
        dark_blue("You: "),
        light_purple(str(text))
    ]))

if __name__ == "__main__":
    app.start()
```

## Add Commands (2 minutes)

```python
import textbox
from textbox.colored import dark_blue, light_purple

app = textbox.App()

@app.on_submit
def on_submit(text):
    app.print(textbox.TextLine([
        dark_blue("You: "),
        light_purple(str(text))
    ]))

@app.command("quit", "q", help="Exit the application")
def quit_app(cmd):
    app.print("Goodbye!")
    app.stop()

@app.command("clear", help="Clear the screen")
def clear_screen(cmd):
    app.print("\n" * 50)  # Simple clear

if __name__ == "__main__":
    app.print(dark_blue("Welcome! Type :help for commands."))
    app.start()
```

## Complete Example (5 minutes)

Here's a complete chat-style application:

```python
#!/usr/bin/env python3
import textbox
from textbox import TextLine, ColorCode
from textbox.colored import dark_blue, light_purple, dark_purple

app = textbox.App()
messages = []

@app.on_submit
def on_message(text):
    # Store message
    message = str(text)
    messages.append(("user", message))
    
    # Display user message
    text.to_start_of_text()
    text.edit_mode = True
    text.insert(dark_blue("You: "))
    text.edit_mode = False
    text.color_pair = ColorCode.LIGHT_BLUE
    app.print(text)
    
    # Simple bot response
    response = "I understand!" if len(message) > 5 else "Tell me more!"
    messages.append(("bot", response))
    
    # Display bot message
    app.print(TextLine([
        dark_purple("Bot: "),
        light_purple(response)
    ]))
    app.print("")  # Blank line

@app.command("history", help="Show conversation history")
def show_history(cmd):
    app.print(dark_blue("=== Chat History ==="))
    for speaker, msg in messages:
        if speaker == "user":
            app.print(f"You: {msg}")
        else:
            app.print(f"Bot: {msg}")
    app.print("")

@app.command("clear", help="Clear chat history")
def clear_history(cmd):
    count = len(messages)
    messages.clear()
    app.print(light_purple(f"Cleared {count} messages"))

@app.command("quit", "q", help="Exit the chat")
def quit_chat(cmd):
    app.print(f"Total messages: {len(messages)}. Goodbye!")
    app.stop()

if __name__ == "__main__":
    app.print(dark_blue("=== Welcome to ChatBox ==="))
    app.print("Type your messages and press Enter")
    app.print("Use :history, :clear, or :quit")
    app.print("")
    app.start()
```

Save as `chatbox.py` and run:

```bash
python chatbox.py
```

## Next Steps

You're now ready to build terminal applications with Textbox!

**Learn More:**
- [Getting Started Guide](getting-started.md) - Detailed tutorial
- [API Reference](api-reference.md) - Complete documentation
- [Examples](examples.md) - More example applications
- [Text Handling](text-handling.md) - Working with rich text
- [Color Support](color-support.md) - Adding colors
- [Advanced Topics](advanced-topics.md) - Complex patterns

## Common Tasks

### Echo user input
```python
@app.on_submit
def echo(text):
    app.print(text)
```

### Create a command
```python
@app.command("hello", help="Say hello")
def hello(cmd):
    app.print("Hello, World!")
```

### Print colored text
```python
from textbox.colored import dark_blue
app.print(dark_blue("This is blue!"))
```

### Stop the application
```python
@app.command("quit")
def quit_app(cmd):
    app.stop()
```

### Print multiple lines
```python
app.print("Line 1\nLine 2\nLine 3")
# or
for line in ["Line 1", "Line 2", "Line 3"]:
    app.print(line)
```

## Cheat Sheet

### Basic Structure
```python
import textbox

app = textbox.App()

@app.on_submit
def on_submit(text):
    # Handle user input
    pass

@app.command("cmd", help="Description")
def command(cmd):
    # Handle command
    pass

if __name__ == "__main__":
    app.start()
```

### Common Imports
```python
import textbox
from textbox import App, Text, TextLine, TextSegment, ColorCode
from textbox.colored import dark_blue, light_blue, dark_purple, light_purple
```

### Print Types
```python
app.print("string")                    # Plain string
app.print(Text("text object"))         # Text object
app.print(TextLine("line"))            # Single line
app.print([TextLine("l1"), TextLine("l2")])  # Multiple lines
```

### Colors
```python
from textbox import ColorCode
from textbox.colored import dark_blue

# Using color code
text = Text("colored")
text.color_pair = ColorCode.LIGHT_BLUE

# Using helper
segment = dark_blue("blue text")
app.print(TextLine([segment, " normal text"]))
```

## Tips

1. **Always use `app.print()`** when the app is running
2. **Commands start with `:`** - users type `:quit` not `quit`
3. **Enable edit mode** before inserting text: `text.edit_mode = True`
4. **Exit cleanly** with `app.stop()` in your quit command
5. **Test in terminal** - not all features work in all terminals

## Troubleshooting

**App doesn't start:**
- Check you called `app.start()` or `await app.astart()`
- Ensure you're not running in an unsupported environment

**Colors don't show:**
- Check your terminal supports colors
- Try the `examples/print_colors.py` script

**Input not working:**
- Make sure terminal has focus
- Try `Ctrl+C` to exit if stuck

**Import errors:**
```python
# ✓ Correct
from textbox import App

# ✗ Wrong
from textbox.app import App  # Internal import
```

## Getting Help

- Read the [Getting Started Guide](getting-started.md)
- Check [Examples](examples.md) for working code
- Review [API Reference](api-reference.md) for details

Happy coding with Textbox! 🎉

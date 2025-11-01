# Troubleshooting Guide

Solutions to common issues when using Textbox.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Application Won't Start](#application-wont-start)
- [Display Problems](#display-problems)
- [Input Issues](#input-issues)
- [Color Problems](#color-problems)
- [Performance Issues](#performance-issues)
- [Error Messages](#error-messages)
- [Platform-Specific Issues](#platform-specific-issues)

---

## Installation Issues

### Package Not Found

**Problem:** `pip install textbox` fails or package not found

**Solution:**
```bash
# Make sure you're using the correct package name
pip install textbox

# If that doesn't work, try installing from source
git clone <repository-url>
cd textbox
pip install -e .
```

### Import Errors

**Problem:** `ImportError: cannot import name 'App' from 'textbox'`

**Solution:**
```python
# ✓ Correct import
from textbox import App

# ✗ Wrong - don't import from submodules
from textbox.app import App
```

### Curses Not Available

**Problem:** `ImportError: No module named '_curses'`

**Solution:**

On **macOS/Linux**: Curses should be pre-installed with Python

On **Windows**: 
```bash
# Install windows-curses
pip install windows-curses
```

---

## Application Won't Start

### App Hangs on Start

**Problem:** Application starts but doesn't show interface

**Symptoms:**
- Black screen
- No response to input
- Terminal appears frozen

**Solutions:**

1. **Check you called start():**
```python
# ✓ Correct
if __name__ == "__main__":
    app.start()

# ✗ Missing start() call
if __name__ == "__main__":
    pass  # Forgot to start!
```

2. **Check terminal compatibility:**
```bash
# Test if your terminal supports curses
python -c "import curses; print('Curses OK')"
```

3. **Try resizing the terminal window** - sometimes helps refresh

### Immediate Crash on Start

**Problem:** App crashes immediately with traceback

**Check:**
1. Terminal size is adequate (minimum ~10 lines, 40 columns)
2. You have proper permissions
3. No conflicting print statements outside app.print()

**Debug:**
```python
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    app.start()
except Exception as e:
    logger.exception("Failed to start")
    raise
```

---

## Display Problems

### Corrupted Display

**Problem:** Text appears garbled or in wrong positions

**Symptoms:**
- Overlapping text
- Characters in wrong places
- Screen doesn't clear properly

**Solutions:**

1. **Resize terminal window** to force refresh

2. **Don't mix print types:**
```python
# ✗ Bad - mixing print and app.print
print("Hello")  # Don't do this!
app.print("World")

# ✓ Good - only use app.print
app.print("Hello")
app.print("World")
```

3. **Avoid printing from outside main thread** when app is running

4. **Clear and restart:**
```bash
clear  # or Ctrl+L
python your_app.py
```

### Text Wrapping Issues

**Problem:** Text doesn't wrap correctly

**Solution:**
```python
from textbox import Text

# Set max line width explicitly
text = Text("Long text...", max_line_width=80)
app.print(text)
```

### Cursor Position Wrong

**Problem:** Cursor appears in wrong location

**Check:**
```python
text = Text("Hello")

# Make sure you're using edit mode correctly
text.to_end_of_text()
text.edit_mode = True  # Required for insertion
text.insert(" World")
text.edit_mode = False  # Turn off when done
```

---

## Input Issues

### Can't Type Anything

**Problem:** Keyboard input doesn't work

**Solutions:**

1. **Check terminal has focus** - click on the terminal window

2. **Verify you're in insert mode:**
```python
# The workspace should be in insert mode by default
# But you can ensure it:
if app.workspace:
    app.workspace.enter_insert_mode()
```

3. **Check for infinite loops blocking input:**
```python
# ✗ Bad - blocks input
@app.on_submit
def on_submit(text):
    while True:  # Don't do this!
        pass

# ✓ Good - processes and returns
@app.on_submit
def on_submit(text):
    app.print(text)
```

### Backspace Not Working

**Problem:** Backspace key doesn't delete characters

**Solution:**
This might be a terminal configuration issue. Try:
- Different terminal emulator
- Check terminal key bindings
- Test with examples/main.py to verify it's not your code

### Enter Key Doesn't Submit

**Problem:** Pressing Enter doesn't submit text

**Check:**
1. Make sure you registered a submit handler:
```python
@app.on_submit
def on_submit(text):
    app.print(text)
```

2. Verify the handler isn't raising exceptions:
```python
@app.on_submit
def on_submit(text):
    try:
        # Your code
        app.print(text)
    except Exception as e:
        app.print(f"Error: {e}")
```

---

## Color Problems

### Colors Don't Show

**Problem:** Text appears without colors

**Check:**

1. **Terminal color support:**
```bash
# Check TERM variable
echo $TERM

# Should be something like: xterm-256color
```

2. **Set color explicitly:**
```python
from textbox import ColorCode

text = Text("Hello")
text.color_pair = ColorCode.LIGHT_BLUE  # Explicit color
app.print(text)
```

3. **Use helper functions correctly:**
```python
from textbox.colored import dark_blue

# ✓ Correct
from textbox import TextLine
line = TextLine([dark_blue("Hello")])

# ✗ Wrong - helper returns TextSegment, not string
text = dark_blue("Hello")
app.print(text)  # Won't show properly
```

### Wrong Colors Displayed

**Problem:** Colors appear different than expected

**Cause:** Terminal color scheme differences

**Solution:**
1. Test with `examples/print_colors.py` to see available colors
2. Stick to basic colors for compatibility
3. Document required terminal settings for users

---

## Performance Issues

### Slow Printing

**Problem:** Printing large amounts of text is slow

**Solution:**

1. **Batch print operations:**
```python
# ✗ Slow - many separate prints
for i in range(1000):
    app.print(f"Line {i}")

# ✓ Fast - one batched print
lines = "\n".join(f"Line {i}" for i in range(1000))
app.print(lines)
```

2. **Limit output:**
```python
# Keep only last N lines
MAX_OUTPUT = 1000
if len(output_buffer) > MAX_OUTPUT:
    output_buffer = output_buffer[-MAX_OUTPUT:]
```

### High CPU Usage

**Problem:** Application uses too much CPU

**Check:**

1. **Avoid tight loops:**
```python
# ✗ Bad - tight loop
@app.on_submit
def on_submit(text):
    while some_condition:
        # Process without any sleep/await
        pass

# ✓ Good - use async with sleep
async def background_task():
    while True:
        await asyncio.sleep(0.1)  # Yield control
        # Do work
```

2. **Profile your code:**
```python
import cProfile

cProfile.run('app.start()')
```

### Memory Leaks

**Problem:** Memory usage grows over time

**Solution:**

1. **Clean up old data:**
```python
# Limit stored history
MAX_HISTORY = 1000
if len(history) > MAX_HISTORY:
    history = history[-MAX_HISTORY:]
```

2. **Don't store references to Text objects unnecessarily**

---

## Error Messages

### `ValueError: The application is not running`

**Problem:** Trying to print before app started

**Solution:**
```python
# ✗ Bad - print before start
app.print("Hello")  # Error!
app.start()

# ✓ Good - print after start or in handler
@app.on_submit
def on_submit(text):
    app.print("Hello")  # OK - app is running

app.start()
```

### `RuntimeError: Cannot insert text when not in edit mode`

**Problem:** Trying to insert text without edit mode

**Solution:**
```python
text = Text("Hello")

# ✓ Correct - enable edit mode first
text.edit_mode = True
text.insert(" World")
text.edit_mode = False
```

### `WindowQuit` Exception

**Problem:** Seeing `WindowQuit` in traceback

**Explanation:** This is normal! It's how the app exits.

**If it's a problem:**
```python
from textbox.signals import WindowQuit

try:
    app.start()
except WindowQuit:
    # Normal exit
    print("Application closed normally")
except Exception as e:
    # Actual error
    print(f"Error: {e}")
```

### `AttributeError: 'NoneType' object has no attribute 'output_box'`

**Problem:** Accessing workspace before it's initialized

**Solution:**
```python
# ✗ Bad - workspace not ready yet
app.workspace.output_box  # Error!
app.start()

# ✓ Good - check if workspace exists
if app.workspace:
    box = app.workspace.output_box
```

---

## Platform-Specific Issues

### macOS Issues

**Problem:** Colors don't work in Terminal.app

**Solution:**
- Use iTerm2 instead, or
- Configure Terminal.app to use xterm-256color:
  - Preferences → Profiles → Advanced → Declare terminal as: `xterm-256color`

### Windows Issues

**Problem:** Curses not available

**Solution:**
```bash
pip install windows-curses
```

**Problem:** Colors look wrong in Command Prompt

**Solution:**
- Use Windows Terminal instead
- Or enable ANSI color support in Command Prompt

### Linux Issues

**Problem:** Encoding errors with special characters

**Solution:**
```python
# Ensure UTF-8 encoding
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
```

### SSH/Remote Terminal Issues

**Problem:** Display problems when running over SSH

**Solution:**
1. Set TERM variable correctly:
```bash
export TERM=xterm-256color
```

2. Use `screen` or `tmux` for better compatibility:
```bash
tmux
python your_app.py
```

---

## Debugging Tips

### Enable Logging

```python
import logging

logging.basicConfig(
    filename='textbox_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.on_submit
def on_submit(text):
    logger.debug(f"Received input: {text}")
    # Your code
```

### Test with Examples

Run the included examples to verify your setup:

```bash
# Test basic functionality
python examples/main.py

# Test colors
python examples/print_colors.py

# Test full app
python examples/llm_interface.py
```

### Minimal Reproduction

Create minimal test case:

```python
import textbox

app = textbox.App()

@app.on_submit
def on_submit(text):
    app.print(text)

if __name__ == "__main__":
    app.start()
```

If this works, the problem is in your code. If it doesn't, it's an environment issue.

### Check Terminal Capabilities

```bash
# Check terminal type
echo $TERM

# Check color support
tput colors

# Check terminal size
tput cols
tput lines
```

---

## Common Mistakes

### 1. Forgetting to Start the App

```python
# ✗ Wrong
app = textbox.App()
# ... forgot app.start()

# ✓ Correct
app = textbox.App()
# ... setup ...
app.start()
```

### 2. Using Regular Print

```python
# ✗ Wrong - corrupts display
print("Hello")  # Don't use regular print!

# ✓ Correct
app.print("Hello")
```

### 3. Modifying Text Without Edit Mode

```python
# ✗ Wrong
text.insert("Hello")  # RuntimeError!

# ✓ Correct
text.edit_mode = True
text.insert("Hello")
text.edit_mode = False
```

### 4. Not Handling Exceptions in Callbacks

```python
# ✗ Wrong - exception crashes handler
@app.on_submit
def on_submit(text):
    value = int(str(text))  # May raise ValueError

# ✓ Correct - handle exceptions
@app.on_submit
def on_submit(text):
    try:
        value = int(str(text))
    except ValueError:
        app.print("Please enter a number")
```

### 5. Blocking the Event Loop

```python
# ✗ Wrong - blocks input
@app.on_submit
def on_submit(text):
    time.sleep(10)  # Freezes app!

# ✓ Correct - use async
async def process():
    await asyncio.sleep(10)
```

---

## Getting More Help

If you're still stuck:

1. **Check the examples** in `examples/` directory
2. **Read the API reference** at [api-reference.md](api-reference.md)
3. **Review the documentation**:
   - [Getting Started](getting-started.md)
   - [Advanced Topics](advanced-topics.md)
4. **Check the issue tracker** on GitHub
5. **Ask for help** with:
   - Your code (minimal example)
   - Error messages (full traceback)
   - Your environment (OS, Python version, terminal)

---

## See Also

- [Getting Started](getting-started.md) - Learn the basics
- [API Reference](api-reference.md) - Complete documentation
- [Examples](examples.md) - Working example applications

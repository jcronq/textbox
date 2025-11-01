# Examples

Complete example applications built with Textbox.

## Table of Contents

- [Simple Echo Application](#simple-echo-application)
- [Chat Interface](#chat-interface)
- [Command-Line Tool](#command-line-tool)
- [Note-Taking Application](#note-taking-application)
- [Log Viewer](#log-viewer)
- [Interactive Shell](#interactive-shell)
- [Task Manager](#task-manager)
- [Data Entry Form](#data-entry-form)

---

## Simple Echo Application

The simplest possible Textbox application - echoes user input.

```python
#!/usr/bin/env python3
"""
Simple echo application
"""
import textbox

app = textbox.App()

@app.on_submit
def on_submit(text):
    app.print(f"Echo: {text}")

@app.command("quit", "q", help="Exit the application")
def quit_cmd(cmd):
    app.stop()

if __name__ == "__main__":
    app.start()
```

**Usage:**
1. Type text and press Enter to see it echoed
2. Type `:quit` or `:q` to exit

---

## Chat Interface

A chat-like interface with colored user and bot messages.

```python
#!/usr/bin/env python3
"""
Chat interface with colored messages
"""
import textbox
from textbox import TextLine, ColorCode
from textbox.colored import dark_blue, light_purple, dark_purple

app = textbox.App()
conversation_history = []

@app.on_submit
def on_message(text):
    # Store message
    user_message = str(text)
    conversation_history.append(("user", user_message))
    
    # Format and display user message
    text.to_start_of_text()
    text.edit_mode = True
    text.insert(dark_blue("You: "))
    text.edit_mode = False
    text.color_pair = ColorCode.LIGHT_BLUE
    app.print(text)
    
    # Generate bot response
    bot_response = generate_response(user_message)
    conversation_history.append(("bot", bot_response))
    
    # Display bot message
    app.print(TextLine([
        dark_purple("Bot: "),
        light_purple(bot_response)
    ]))
    app.print("")  # Blank line

def generate_response(message):
    """Simple bot response generator"""
    message_lower = message.lower()
    
    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! How can I help you today?"
    elif "bye" in message_lower:
        return "Goodbye! Have a great day!"
    elif "help" in message_lower:
        return "I'm a simple chatbot. Try saying hello!"
    elif "?" in message:
        return "That's a great question! I'm still learning."
    else:
        return "I understand. Tell me more!"

@app.command("history", help="Show conversation history")
def show_history(cmd):
    app.print(dark_blue("=== Conversation History ==="))
    for speaker, message in conversation_history:
        if speaker == "user":
            app.print(TextLine([dark_blue("You: "), message]))
        else:
            app.print(TextLine([dark_purple("Bot: "), light_purple(message)]))
    app.print("")

@app.command("clear", help="Clear conversation history")
def clear_history(cmd):
    conversation_history.clear()
    app.print(light_purple("History cleared!"))

@app.command("quit", "q", help="Exit the chat")
def quit_chat(cmd):
    app.print(light_purple("Thanks for chatting! Goodbye!"))
    app.stop()

if __name__ == "__main__":
    app.print(dark_blue("=== Welcome to ChatBox ==="))
    app.print("Type your messages and press Enter to send.")
    app.print("Use :history to see conversation, :clear to reset, :quit to exit.")
    app.print("")
    app.start()
```

---

## Command-Line Tool

A command-line style application with multiple commands.

```python
#!/usr/bin/env python3
"""
Command-line tool example with file operations
"""
import textbox
from textbox import ColorCode
from textbox.colored import dark_blue, light_purple
import os

app = textbox.App()
current_dir = os.getcwd()

@app.command("ls", help="List files in current directory")
def list_files(cmd):
    try:
        files = os.listdir(current_dir)
        app.print(dark_blue(f"Contents of {current_dir}:"))
        for f in files:
            if os.path.isdir(os.path.join(current_dir, f)):
                app.print(f"  {f}/", end="")
                app.print("", end="\n")
            else:
                app.print(f"  {f}", end="")
                app.print("", end="\n")
    except Exception as e:
        app.print(f"Error: {e}", end="")
        app.print("", end="\n")

@app.command("pwd", help="Print working directory")
def print_working_dir(cmd):
    app.print(dark_blue(current_dir))

@app.command("cd", help="Change directory (usage: :cd <path>)")
def change_dir(cmd):
    global current_dir
    parts = cmd.split(" ", 1)
    if len(parts) < 2:
        app.print("Usage: :cd <directory>")
        return
    
    path = parts[1]
    try:
        new_dir = os.path.abspath(os.path.join(current_dir, path))
        if os.path.isdir(new_dir):
            current_dir = new_dir
            app.print(dark_blue(f"Changed to: {current_dir}"))
        else:
            app.print(f"Not a directory: {path}")
    except Exception as e:
        app.print(f"Error: {e}")

@app.command("cat", help="Display file contents (usage: :cat <file>)")
def cat_file(cmd):
    parts = cmd.split(" ", 1)
    if len(parts) < 2:
        app.print("Usage: :cat <filename>")
        return
    
    filename = parts[1]
    filepath = os.path.join(current_dir, filename)
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            app.print(dark_blue(f"=== {filename} ==="))
            app.print(content)
            app.print(dark_blue("=" * (len(filename) + 8)))
    except FileNotFoundError:
        app.print(f"File not found: {filename}")
    except Exception as e:
        app.print(f"Error: {e}")

@app.command("quit", "q", "exit", help="Exit the application")
def quit_app(cmd):
    app.print("Goodbye!")
    app.stop()

@app.on_submit
def on_input(text):
    app.print(light_purple(f"Use commands like :ls, :pwd, :cd, :cat"))
    app.print(light_purple(f"Type :help for all commands"))

if __name__ == "__main__":
    app.print(dark_blue("=== File Browser ==="))
    app.print(f"Current directory: {current_dir}")
    app.print("Type :help for available commands")
    app.print("")
    app.start()
```

---

## Note-Taking Application

Keep notes during a session with save/load functionality.

```python
#!/usr/bin/env python3
"""
Note-taking application
"""
import textbox
from textbox import ColorCode
from textbox.colored import dark_blue, light_purple
import json
import os

app = textbox.App()
notes = []
notes_file = "notes.json"

def save_notes():
    """Save notes to file"""
    try:
        with open(notes_file, 'w') as f:
            json.dump(notes, f, indent=2)
        return True
    except Exception as e:
        app.print(f"Error saving: {e}")
        return False

def load_notes():
    """Load notes from file"""
    global notes
    try:
        if os.path.exists(notes_file):
            with open(notes_file, 'r') as f:
                notes = json.load(f)
            return True
    except Exception as e:
        app.print(f"Error loading: {e}")
    return False

@app.on_submit
def add_note(text):
    note_text = str(text)
    notes.append(note_text)
    
    # Confirm addition
    text.to_start_of_text()
    text.edit_mode = True
    text.insert(dark_blue(f"Note #{len(notes)}: "))
    text.edit_mode = False
    text.color_pair = ColorCode.LIGHT_BLUE
    app.print(text)

@app.command("list", "l", help="List all notes")
def list_notes(cmd):
    if not notes:
        app.print(light_purple("No notes yet!"))
    else:
        app.print(dark_blue(f"=== Your Notes ({len(notes)}) ==="))
        for i, note in enumerate(notes, 1):
            app.print(f"{i}. {note}")
        app.print("")

@app.command("delete", "del", help="Delete a note (usage: :delete <number>)")
def delete_note(cmd):
    parts = cmd.split(" ")
    if len(parts) < 2:
        app.print("Usage: :delete <note_number>")
        return
    
    try:
        note_num = int(parts[1])
        if 1 <= note_num <= len(notes):
            deleted = notes.pop(note_num - 1)
            app.print(light_purple(f"Deleted note #{note_num}: {deleted}"))
        else:
            app.print(f"Invalid note number. Use 1-{len(notes)}")
    except ValueError:
        app.print("Please provide a valid number")

@app.command("clear", help="Clear all notes")
def clear_notes(cmd):
    count = len(notes)
    notes.clear()
    app.print(light_purple(f"Cleared {count} notes!"))

@app.command("save", help="Save notes to file")
def save_cmd(cmd):
    if save_notes():
        app.print(light_purple(f"Saved {len(notes)} notes to {notes_file}"))

@app.command("load", help="Load notes from file")
def load_cmd(cmd):
    if load_notes():
        app.print(light_purple(f"Loaded {len(notes)} notes from {notes_file}"))
        list_notes(cmd)

@app.command("search", help="Search notes (usage: :search <term>)")
def search_notes(cmd):
    parts = cmd.split(" ", 1)
    if len(parts) < 2:
        app.print("Usage: :search <search_term>")
        return
    
    search_term = parts[1].lower()
    results = [(i+1, note) for i, note in enumerate(notes) 
               if search_term in note.lower()]
    
    if results:
        app.print(dark_blue(f"=== Search Results for '{search_term}' ==="))
        for num, note in results:
            app.print(f"{num}. {note}")
        app.print("")
    else:
        app.print(light_purple(f"No notes found containing '{search_term}'"))

@app.command("quit", "q", help="Exit the application")
def quit_app(cmd):
    if notes and not os.path.exists(notes_file):
        app.print(light_purple("You have unsaved notes!"))
        app.print(light_purple("Use :save before quitting to keep them."))
    app.print(f"You created {len(notes)} notes this session. Goodbye!")
    app.stop()

if __name__ == "__main__":
    # Try to load existing notes
    if load_notes() and notes:
        app.print(dark_blue(f"Loaded {len(notes)} existing notes"))
    
    app.print(dark_blue("=== Notes Application ==="))
    app.print("Type notes and press Enter to save them.")
    app.print("Commands: :list, :delete <n>, :clear, :save, :load, :search <term>")
    app.print("")
    app.start()
```

---

## Log Viewer

Display and filter log messages with different severity levels.

```python
#!/usr/bin/env python3
"""
Log viewer with filtering
"""
import textbox
from textbox import TextLine, ColorCode
from datetime import datetime

app = textbox.App()
logs = []
log_filter = None  # None = show all

def log(level, message):
    """Add and display a log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "time": timestamp,
        "level": level,
        "message": message
    }
    logs.append(log_entry)
    
    # Display if passes filter
    if log_filter is None or level == log_filter:
        display_log(log_entry)

def display_log(entry):
    """Display a single log entry with color"""
    colors = {
        "DEBUG": ColorCode.GREY,
        "INFO": ColorCode.LIGHT_BLUE,
        "WARNING": ColorCode.YELLOW,
        "ERROR": ColorCode.DARK_RED,
    }
    
    color = colors.get(entry["level"], ColorCode.DEFAULT)
    line = TextLine(
        f"[{entry['time']}] [{entry['level']:8}] {entry['message']}",
        default_color_pair=color
    )
    app.print(line)

@app.on_submit
def on_input(text):
    # Treat input as INFO log
    log("INFO", str(text))

@app.command("debug", help="Log a debug message")
def debug_log(cmd):
    parts = cmd.split(" ", 1)
    msg = parts[1] if len(parts) > 1 else "Debug message"
    log("DEBUG", msg)

@app.command("info", help="Log an info message")
def info_log(cmd):
    parts = cmd.split(" ", 1)
    msg = parts[1] if len(parts) > 1 else "Info message"
    log("INFO", msg)

@app.command("warning", "warn", help="Log a warning message")
def warning_log(cmd):
    parts = cmd.split(" ", 1)
    msg = parts[1] if len(parts) > 1 else "Warning message"
    log("WARNING", msg)

@app.command("error", help="Log an error message")
def error_log(cmd):
    parts = cmd.split(" ", 1)
    msg = parts[1] if len(parts) > 1 else "Error message"
    log("ERROR", msg)

@app.command("filter", help="Filter logs (usage: :filter <level> or :filter clear)")
def filter_logs(cmd):
    global log_filter
    parts = cmd.split(" ")
    
    if len(parts) < 2:
        app.print("Usage: :filter <DEBUG|INFO|WARNING|ERROR|clear>")
        return
    
    level = parts[1].upper()
    
    if level == "CLEAR":
        log_filter = None
        app.print(TextLine("Filter cleared - showing all logs", 
                          default_color_pair=ColorCode.LIGHT_BLUE))
    elif level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        log_filter = level
        app.print(TextLine(f"Now showing only {level} logs", 
                          default_color_pair=ColorCode.LIGHT_BLUE))
    else:
        app.print("Invalid level. Use DEBUG, INFO, WARNING, ERROR, or clear")

@app.command("show", help="Show all logs (respecting current filter)")
def show_logs(cmd):
    app.print(TextLine("=== Log History ===", 
                      default_color_pair=ColorCode.DARK_BLUE))
    count = 0
    for entry in logs:
        if log_filter is None or entry["level"] == log_filter:
            display_log(entry)
            count += 1
    app.print(TextLine(f"=== {count} logs shown ===", 
                      default_color_pair=ColorCode.DARK_BLUE))

@app.command("clear", help="Clear all logs")
def clear_logs(cmd):
    count = len(logs)
    logs.clear()
    app.print(TextLine(f"Cleared {count} logs", 
                      default_color_pair=ColorCode.LIGHT_PURPLE))

@app.command("quit", "q", help="Exit the log viewer")
def quit_app(cmd):
    app.stop()

if __name__ == "__main__":
    app.print(TextLine("=== Log Viewer ===", 
                      default_color_pair=ColorCode.DARK_BLUE))
    app.print("Commands: :debug, :info, :warning, :error, :filter, :show, :clear")
    app.print("")
    
    # Example logs
    log("INFO", "Log viewer started")
    log("DEBUG", "System initialized")
    
    app.start()
```

---

## Interactive Shell

A Python REPL-style interactive shell.

```python
#!/usr/bin/env python3
"""
Interactive Python shell
"""
import textbox
from textbox import TextLine, ColorCode
from textbox.colored import dark_blue, light_purple

app = textbox.App()
namespace = {}

@app.on_submit
def evaluate_code(text):
    code = str(text)
    
    # Display input
    app.print(TextLine([dark_blue(">>> "), code]))
    
    try:
        # Try to eval first (for expressions)
        try:
            result = eval(code, namespace)
            if result is not None:
                app.print(light_purple(str(result)))
        except SyntaxError:
            # If eval fails, try exec (for statements)
            exec(code, namespace)
    except Exception as e:
        app.print(TextLine(
            f"Error: {type(e).__name__}: {e}",
            default_color_pair=ColorCode.DARK_RED
        ))
    
    app.print("")  # Blank line

@app.command("vars", help="Show all variables")
def show_vars(cmd):
    user_vars = {k: v for k, v in namespace.items() 
                 if not k.startswith('__')}
    
    if user_vars:
        app.print(dark_blue("=== Variables ==="))
        for name, value in user_vars.items():
            app.print(f"{name} = {repr(value)}")
        app.print("")
    else:
        app.print("No variables defined yet")

@app.command("clear", help="Clear all variables")
def clear_vars(cmd):
    namespace.clear()
    app.print(light_purple("Variables cleared"))

@app.command("quit", "q", "exit", help="Exit the shell")
def quit_shell(cmd):
    app.print("Goodbye!")
    app.stop()

if __name__ == "__main__":
    app.print(dark_blue("=== Python Shell ==="))
    app.print("Type Python expressions or statements")
    app.print("Commands: :vars, :clear, :quit")
    app.print("")
    app.start()
```

---

## Task Manager

Simple task/todo list manager.

```python
#!/usr/bin/env python3
"""
Task manager / Todo list
"""
import textbox
from textbox import TextLine, ColorCode
from textbox.colored import dark_blue, light_purple

app = textbox.App()
tasks = []

class Task:
    def __init__(self, description):
        self.description = description
        self.completed = False
    
    def toggle(self):
        self.completed = not self.completed
    
    def __str__(self):
        status = "✓" if self.completed else " "
        return f"[{status}] {self.description}"

@app.on_submit
def add_task(text):
    task = Task(str(text))
    tasks.append(task)
    
    app.print(TextLine([
        dark_blue("Added: "),
        light_purple(str(task))
    ]))

@app.command("list", "l", help="List all tasks")
def list_tasks(cmd):
    if not tasks:
        app.print(light_purple("No tasks yet!"))
        return
    
    app.print(dark_blue("=== Your Tasks ==="))
    for i, task in enumerate(tasks, 1):
        color = ColorCode.GREY if task.completed else ColorCode.DEFAULT
        app.print(TextLine(f"{i}. {task}", default_color_pair=color))
    app.print("")

@app.command("done", help="Mark task as done (usage: :done <number>)")
def complete_task(cmd):
    parts = cmd.split(" ")
    if len(parts) < 2:
        app.print("Usage: :done <task_number>")
        return
    
    try:
        task_num = int(parts[1])
        if 1 <= task_num <= len(tasks):
            tasks[task_num - 1].toggle()
            app.print(light_purple(f"Toggled: {tasks[task_num - 1]}"))
        else:
            app.print(f"Invalid task number. Use 1-{len(tasks)}")
    except ValueError:
        app.print("Please provide a valid number")

@app.command("delete", "del", help="Delete a task (usage: :delete <number>)")
def delete_task(cmd):
    parts = cmd.split(" ")
    if len(parts) < 2:
        app.print("Usage: :delete <task_number>")
        return
    
    try:
        task_num = int(parts[1])
        if 1 <= task_num <= len(tasks):
            deleted = tasks.pop(task_num - 1)
            app.print(light_purple(f"Deleted: {deleted}"))
        else:
            app.print(f"Invalid task number. Use 1-{len(tasks)}")
    except ValueError:
        app.print("Please provide a valid number")

@app.command("clear", help="Clear completed tasks")
def clear_completed(cmd):
    before = len(tasks)
    tasks[:] = [t for t in tasks if not t.completed]
    cleared = before - len(tasks)
    app.print(light_purple(f"Cleared {cleared} completed tasks"))

@app.command("quit", "q", help="Exit the task manager")
def quit_app(cmd):
    pending = sum(1 for t in tasks if not t.completed)
    app.print(f"You have {pending} pending tasks. Goodbye!")
    app.stop()

if __name__ == "__main__":
    app.print(dark_blue("=== Task Manager ==="))
    app.print("Type tasks and press Enter to add them")
    app.print("Commands: :list, :done <n>, :delete <n>, :clear, :quit")
    app.print("")
    app.start()
```

---

## See Also

- [Getting Started](getting-started.md) - Learn the basics
- [API Reference](api-reference.md) - Complete API documentation
- [Advanced Topics](advanced-topics.md) - Complex patterns and techniques

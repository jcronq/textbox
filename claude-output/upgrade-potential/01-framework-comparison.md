# Industry Framework Comparison

Comprehensive comparison of textbox against modern TUI frameworks: Rich, Textual, prompt_toolkit, and urwid.

---

## Comparison Matrix

| Feature | textbox | Rich | Textual | prompt_toolkit | urwid |
|---------|---------|------|---------|----------------|-------|
| **Input Handling** | ✅ Full | ❌ None | ✅ Full | ✅ Full | ✅ Full |
| **Async Support** | ✅ Native | ✅ Yes | ✅ Native | ✅ Pluggable | ✅ Pluggable |
| **Vim Keybindings** | ✅ Native | ❌ N/A | ⚠️ Custom | ✅ Built-in | ⚠️ Custom |
| **Text Layers** | ✅ 4 layers | ✅ Segments | ✅ Rich-based | ✅ Buffer/Doc | ⚠️ Basic |
| **Color Support** | ✅ Curses | ✅ Advanced | ✅ CSS-like | ✅ Full | ✅ Full |
| **Layout System** | ⚠️ Manual | ❌ N/A | ✅ CSS Grid | ✅ Containers | ✅ Pile/Grid |
| **Undo/Redo** | ❌ No | ❌ N/A | ⚠️ App-level | ✅ Built-in | ❌ No |
| **Testing Tools** | ⚠️ Basic | ✅ Mock console | ✅ Snapshot | ✅ Mock I/O | ⚠️ Basic |
| **Dependencies** | 3 (2 unused) | 8+ | 20+ | 6+ | 0 |
| **Learning Curve** | Medium | Low | High | High | Medium |
| **Active Development** | Alpha | Very Active | Very Active | Active | Slow |

---

## Rich Library

### Overview
**Purpose:** Terminal output with ANSI styling
**Philosophy:** Render beautiful terminal output, not a TUI framework
**First Release:** 2019
**Stars:** 48k+ GitHub stars

### Architecture

```python
Console (rendering engine)
  ↓
Renderable Protocol (__rich__, __rich_console__, __rich_measure__)
  ↓
Segments (text + style units)
```

### Key Design Patterns

**1. Protocol-Based Extensibility**
```python
class MyClass:
    def __rich__(self) -> RenderableType:
        return Text("My representation", style="bold")

# Any object can be rendered
console.print(MyClass())
```

**2. Composition Over Inheritance**
```python
from rich.table import Table
from rich.panel import Panel

table = Table()
panel = Panel(table)  # Compose renderables
console.print(panel)
```

**3. Measure-Render-Update Cycle**
```python
# 1. Measure: How much space needed?
width = renderable.__rich_measure__(console, options)

# 2. Render: Generate segments
segments = renderable.__rich_console__(console, options)

# 3. Update: Write to terminal
console.file.write(segments_to_ansi(segments))
```

### Comparison with textbox

| Aspect | Rich | textbox | Winner |
|--------|------|---------|--------|
| **Rendering Quality** | Excellent (tables, progress, markdown) | Basic (colored text) | Rich |
| **Input Handling** | None | Full vim-like interface | textbox |
| **Text Abstraction** | Segment-based | 4-layer hierarchy | Tie |
| **Extensibility** | Protocol-based (excellent) | Inheritance-based | Rich |
| **Use Case Fit** | Output-only tools | Interactive editors | textbox |

### Verdict: ❌ DON'T ADOPT

**Reasons:**
- Rich has no input handling at all
- You'd need to rebuild your entire input system
- Your text abstraction is already competitive
- Migration: 100+ hours for no benefit

**What to Learn:**
- ✅ Protocol-based rendering
- ✅ Measure-render-update cycle
- ✅ Composition patterns

---

## Textual Framework

### Overview
**Purpose:** Full-featured async TUI framework
**Philosophy:** "TUI development inspired by modern web development"
**First Release:** 2021
**Stars:** 25k+ GitHub stars
**Built on:** Rich for rendering

### Architecture

```python
App (asyncio event loop)
  ↓
DOM (widget tree)
  ↓
Message Queue (async events)
  ↓
Reactive Attributes (auto-update)
  ↓
CSS Engine (styling)
  ↓
Rich Renderer (output)
```

### Key Design Patterns

**1. Reactive Programming**
```python
class CounterWidget(Widget):
    count = reactive(0)  # Reactive attribute

    def watch_count(self, old, new):
        # Automatically called on change
        self.refresh()

    def on_button_pressed(self):
        self.count += 1  # Triggers watcher
```

**2. Message-Based Events**
```python
class MyApp(App):
    def on_button_pressed(self, event: Button.Pressed):
        # Handle button press message
        self.query_one("#input").focus()
```

**3. CSS for Styling**
```python
# my_app.css
#my-button {
    width: 50%;
    height: 3;
    background: blue;
}
```

**4. Component Composition**
```python
def compose(self) -> ComposeResult:
    yield Header()
    yield Container(
        Input(id="name"),
        Button("Submit"),
    )
    yield Footer()
```

### Comparison with textbox

| Aspect | Textual | textbox | Winner |
|--------|---------|---------|--------|
| **Ease of Use** | Very high (batteries included) | Medium (lower-level) | Textual |
| **Flexibility** | Medium (framework constraints) | High (library approach) | textbox |
| **Vim Support** | Custom only | Native design | textbox |
| **Testing** | Excellent (snapshots, pilot) | Basic | Textual |
| **Styling** | CSS-like (powerful) | Manual colors | Textual |
| **Learning Curve** | Steep (many concepts) | Moderate | textbox |
| **Control** | Framework dictates | Full control | textbox |

### Verdict: ❌ DON'T ADOPT

**Reasons:**
1. **Philosophy Mismatch**
   - Textual: Complete application framework
   - textbox: Library with optional framework wrapper
   - Your users want low-level control

2. **Would Lose Unique Value**
   - Your vim-like interface is custom and excellent
   - Textual's input model is different
   - Hard to replicate your text abstraction layers

3. **Overkill for Use Case**
   - CSS engine: Don't need complex styling
   - DOM/Widget tree: Your flat structure works
   - Message queue: Events are simpler in your case

4. **Migration Cost**
   - Complete rewrite: 200+ hours
   - Learning curve for users
   - Breaking changes to all existing code

**What to Learn:**
- ✅ Snapshot testing approach
- ✅ Pilot API for integration tests
- ✅ Reactive state management patterns
- ✅ Message-based event system

**Example Adoption (Don't rewrite, just borrow pattern):**
```python
# Add optional reactive attributes to textbox
from textbox.reactive import reactive

class MyComponent:
    cursor_pos = reactive(Position(0, 0))

    def watch_cursor_pos(self, old, new):
        self.redraw()  # Auto-refresh on change
```

---

## prompt_toolkit

### Overview
**Purpose:** Building interactive command-line applications
**Philosophy:** Powerful line editing with full-screen capabilities
**First Release:** 2014
**Stars:** 9k+ GitHub stars
**Used by:** IPython, ptpython, AWS CLI

### Architecture

```python
Application (coordinator)
  ├── Layout (UI structure)
  │   ├── Container (VSplit, HSplit, Float)
  │   └── UIControl (BufferControl, FormattedTextControl)
  ├── Buffers (text data + operations)
  ├── KeyBindings (input handling)
  └── Style (colors/formatting)
```

### Key Design Patterns

**1. Buffer/Document Separation**
```python
# Buffer: Mutable text state
buffer = Buffer(document=Document("initial text"))

# Document: Immutable view of text
doc = buffer.document
text_before = doc.text_before_cursor
text_after = doc.text_after_cursor
```

**2. Declarative Key Bindings**
```python
kb = KeyBindings()

@kb.add('c-c')
def _(event):
    event.app.exit()

@kb.add('tab', filter=has_focus('input'))
def _(event):
    event.app.layout.focus_next()
```

**3. Input Processors (Transform Display)**
```python
class HighlightProcessor(Processor):
    def apply_transformation(self, ti):
        # Modify how text is displayed without changing buffer
        return Transformation(fragments=[...])

buffer.control.input_processors = [HighlightProcessor()]
```

**4. Pluggable Event Loops**
```python
# Works with asyncio, Twisted, Tornado, etc.
from prompt_toolkit.eventloop import use_asyncio_event_loop
use_asyncio_event_loop()
```

### Comparison with textbox

| Aspect | prompt_toolkit | textbox | Winner |
|--------|----------------|---------|--------|
| **Line Editing** | Excellent (REPL focus) | Good (multi-line focus) | prompt_toolkit |
| **Vim Mode** | Built-in comprehensive | Custom excellent | Tie |
| **Undo/Redo** | ✅ Built-in | ❌ Missing | prompt_toolkit |
| **Key Bindings** | Registry + filters | Mode-based dispatch | prompt_toolkit |
| **Text Buffer** | Buffer/Document pattern | Text/TextLine hierarchy | Different goals |
| **Layout System** | Container composition | Manual BoundingBox | prompt_toolkit |
| **Dependencies** | Many | Few | textbox |
| **Simplicity** | Complex API | Simpler | textbox |

### Verdict: ~ STUDY BUT DON'T ADOPT

**Reasons:**
1. **Different Primary Use Case**
   - prompt_toolkit: REPLs, prompts, CLI tools
   - textbox: Multi-line text editors

2. **Your Text Abstraction is Already Good**
   - prompt_toolkit's Buffer/Document is optimized for line-editing
   - Your 4-layer hierarchy is better for multi-line documents

3. **Would Lose Simplicity**
   - prompt_toolkit has a complex API
   - Many concepts to learn
   - Your simple App wrapper would be lost

**What to Learn:**
- ✅ **Undo/Redo Implementation** - Study their approach closely
- ✅ **Key Binding Registry** - Better than your mode dispatch
- ✅ **Input Processors** - Transform display without changing data
- ✅ **Mock I/O for Testing** - DummyInput/DummyOutput pattern

**Concrete Borrowings:**

1. **Add Undo/Redo** (16 hours):
```python
# Based on prompt_toolkit's approach
class TextBuffer:
    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def _save_state(self):
        self._undo_stack.append(self.text.copy())
```

2. **Key Binding Registry** (12 hours):
```python
# Instead of mode-based dispatch
@kb.add('ctrl-u')
def undo(event):
    event.app.workspace.undo()

@kb.add('w', filter=in_command_mode)
def word_forward(event):
    event.app.workspace.word_forward()
```

---

## urwid

### Overview
**Purpose:** Console UI library for Python
**Philosophy:** Event-driven widget system
**First Release:** 2004 (20 years old!)
**Stars:** 2.8k GitHub stars
**Status:** Mature but slow development

### Architecture

```python
MainLoop (event dispatcher)
  ├── Display Module (raw, curses, etc.)
  ├── Widget Tree (hierarchical)
  ├── Event Loop (select, asyncio, Twisted, etc.)
  └── Signals (observer pattern)
```

### Key Design Patterns

**1. Widget Hierarchy**
```python
# Widgets compose into tree
pile = urwid.Pile([
    urwid.Text("Header"),
    urwid.Edit("Input: "),
    urwid.Button("Submit"),
])

filler = urwid.Filler(pile, valign='top')
```

**2. Signal System**
```python
button = urwid.Button("Click me")
urwid.connect_signal(button, 'click', on_click)

def on_click(button):
    # Handle click
    pass
```

**3. Canvas-Based Rendering**
```python
class MyWidget(urwid.Widget):
    def render(self, size, focus=False):
        # Return Canvas object
        canvas = urwid.TextCanvas([...])
        return canvas
```

**4. Pluggable Event Loops**
```python
loop = urwid.MainLoop(
    widget,
    event_loop=urwid.AsyncioEventLoop()  # or TwistedEventLoop, etc.
)
```

### Comparison with textbox

| Aspect | urwid | textbox | Winner |
|--------|-------|---------|--------|
| **Maturity** | 20 years | Alpha | urwid |
| **Modern Patterns** | Pre-async era | Async-first | textbox |
| **Widget System** | Comprehensive | Basic components | urwid |
| **Event System** | Signals | None | urwid |
| **Vim Support** | Custom | Native | textbox |
| **Code Style** | Older Python | Modern Python | textbox |
| **Active Development** | Slow | Alpha | Neither |
| **Type Hints** | Minimal | Partial | textbox |

### Verdict: ~ SIMILAR GENERATION, DIFFERENT ERA

**Analysis:**
- urwid is what you might have built 10 years ago
- It's pre-async/await, pre-type hints, pre-modern Python
- Your approach is more modern

**Reasons Not to Adopt:**
1. Older codebase (2004 vs your 2023 code)
2. Less active development
3. You already have equivalent features
4. Your async approach is cleaner

**What to Learn:**
- ✅ **Signal System** - Their observer pattern is clean
- ✅ **Widget Composition** - Pile/Columns/Grid patterns
- ✅ **Canvas Abstraction** - Intermediate representation idea

**Your Approach is Already Better:**
- ✅ Native async/await (urwid: retrofitted)
- ✅ Type hints (urwid: minimal)
- ✅ Modern Python idioms
- ✅ Cleaner architecture

---

## Pattern Adoption Recommendations

### From Rich: Protocol-Based Rendering

**Adopt:** ✅ YES (Medium Priority)

```python
# Add to textbox
from typing import Protocol

class Renderable(Protocol):
    def render(self, width: int) -> List[SegmentedTextLine]:
        ...

# Now any object can be "printed"
class CustomTable:
    def render(self, width: int) -> List[SegmentedTextLine]:
        # Generate table lines
        return lines

app.print(CustomTable())  # Works!
```

**Benefit:** Extensibility, cleaner API
**Effort:** 12 hours
**Breaking Changes:** None (additive)

---

### From Textual: Reactive State

**Adopt:** ⚠️ MAYBE (Low Priority)

```python
# Optional feature, not core
from textbox.reactive import reactive

class MyBox(TextBox):
    scroll_position = reactive(0)

    def watch_scroll_position(self, old, new):
        self.redraw()
```

**Benefit:** Automatic UI updates
**Effort:** 16 hours
**Breaking Changes:** None (opt-in)
**Downside:** Adds complexity

**Verdict:** Nice-to-have, not essential

---

### From Textual: Snapshot Testing

**Adopt:** ✅ YES (High Priority)

```python
# Add testing utilities
def test_app_renders_correctly(snapshot):
    app = App()
    app.print("Hello")
    assert app.capture_output() == snapshot
```

**Benefit:** Visual regression testing
**Effort:** 8 hours
**Breaking Changes:** None

**Verdict:** Essential for quality

---

### From prompt_toolkit: Undo/Redo

**Adopt:** ✅ YES (Critical Priority)

```python
# This is a glaring omission
app = App()
@app.on_submit
def handle(text):
    # User makes mistake... can't undo!
```

**Benefit:** Essential editor feature
**Effort:** 16 hours
**Breaking Changes:** None (additive)

**Verdict:** Must-have feature

---

### From prompt_toolkit: Key Binding Registry

**Adopt:** ✅ YES (High Priority)

Current (mode-based dispatch):
```python
def command_handler(self, key: int):
    if key == ord('j'):
        self.cursor_down()
    elif key == ord('k'):
        self.cursor_up()
    # ... 50 more lines
```

Better (registry):
```python
@workspace.bind('j', mode='COMMAND')
def cursor_down(workspace):
    workspace.cursor_down()

@workspace.bind('k', mode='COMMAND')
def cursor_up(workspace):
    workspace.cursor_up()
```

**Benefit:** Cleaner, extensible, testable
**Effort:** 12 hours
**Breaking Changes:** None (keep both initially)

**Verdict:** Significant improvement

---

### From urwid: Signal System

**Adopt:** ✅ YES (Medium Priority)

```python
# Add event system
from textbox.signals import connect

input_box = InputBox(...)
connect(input_box, 'text_changed', on_text_change)

def on_text_change(sender, new_text):
    # React to changes
    pass
```

**Benefit:** Decoupled components
**Effort:** 12 hours
**Breaking Changes:** None (additive)

**Verdict:** Worthwhile addition

---

## Summary Decision Matrix

| Framework | Adopt Framework? | Borrow Patterns? | Priority Patterns |
|-----------|------------------|------------------|-------------------|
| **Rich** | ❌ No | ✅ Yes | Protocol rendering, Composition |
| **Textual** | ❌ No | ✅ Yes | Snapshot testing, Reactive (optional) |
| **prompt_toolkit** | ❌ No | ✅ Yes | Undo/redo, Key bindings registry |
| **urwid** | ❌ No | ✅ Yes | Signal system |

---

## Final Recommendation

**🎯 Don't switch frameworks. Selectively adopt patterns.**

### Immediate Adoptions (< 1 month)
1. ✅ Undo/redo from prompt_toolkit (16h)
2. ✅ Key binding registry (12h)
3. ✅ Signal/event system (12h)
4. ✅ Snapshot testing (8h)
5. ✅ Protocol-based rendering (12h)

**Total: 60 hours (1.5 weeks)**

### Benefits
- Add industry-standard features
- Improve testability significantly
- Maintain your unique vim-like interface
- Keep low-level control
- No breaking changes

### What You Keep
- ✅ Your excellent text abstraction
- ✅ Vim-like modal interface
- ✅ Library + framework flexibility
- ✅ Custom curses wrapper
- ✅ Async-first design

**This is the winning strategy: Polish what you have, don't rebuild it.**

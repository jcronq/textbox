# Immediate Improvements

Quick wins that can be implemented in < 1 week with high ROI.

---

## Summary

After comparing textbox to industry standards (Rich, Textual, prompt_toolkit, urwid), here are the immediate improvements to make:

**Total Time:** ~40 hours (1 week)
**Impact:** Transform from alpha to production-ready foundation

---

## Day 1: Dependency Cleanup (6 minutes)

### 1. Remove uvloop (5 minutes)

**Why:** <1% performance benefit, breaks Windows compatibility

**Current:**
```python
# textbox/__init__.py:33
uvloop.install()
```

**Action:**
```bash
# 1. Edit textbox/__init__.py
# Remove line 5: import uvloop
# Remove line 33: uvloop.install()

# 2. Edit requirements.txt
# Remove: uvloop

# 3. Edit pyproject.toml if it exists
# Remove uvloop from dependencies

# 4. Test
python -m pytest textbox/
```

**Files to change:**
- `textbox/__init__.py` (remove import and install call)
- `requirements.txt` (remove line)

**Result:** Simpler codebase, Windows compatible

---

### 2. Remove termcolor (1 minute)

**Why:** Not actually used in codebase

**Action:**
```bash
# 1. Verify not used
grep -r "termcolor" textbox/*.py
# Should only find it in textbox.bck/ (backup code)

# 2. Remove from requirements
# Edit requirements.txt, remove: termcolor

# 3. Test
python -m pytest textbox/
```

**Result:** One less dependency to maintain

---

## Day 2: Fix Critical Bugs (3-4 hours)

From the original review, fix all 9 critical bugs:

### Priority Order:

1. **text.py:191** - IndexError in next_line (5 min)
2. **text_line.py:153** - Missing return (5 min)
3. **input_box.py:100** - Getter side effect (5 min)
4. **text_box.py:188** - Wrong type assignment (10 min)
5. **input_output_workspace.py:222** - Strip not assigned (2 min)
6. **window.py:144-157** - State validation (15 min)
7. **curses_utils.py:71** - Assignment operator (2 min)
8. **color_code.py** - Make Enum + fix typo (20 min)
9. **__init__.py:78** - Type hint mismatch (10 min)

See `review/01-critical-bugs.md` for detailed fixes.

**Result:** No more crashes or data corruption

---

## Day 3: Add Type Hints (8 hours)

### Priority: Public API First

**1. App class (2 hours)**
```python
# textbox/__init__.py
from typing import Callable, Union, Optional
from textbox.text import Text

class App:
    def __init__(self) -> None:
        ...

    def start(self) -> None:
        """Start the application in blocking mode."""
        ...

    async def astart(self) -> None:
        """Start the application in async mode."""
        ...

    def on_submit(self, func: Callable[[Text], None]) -> Callable[[Text], None]:
        """Register a submit callback."""
        ...

    def command(
        self,
        name: str,
        *alt_names: str,
        help: Optional[str] = None
    ) -> Callable[[Callable[[str], None]], Callable[[str], None]]:
        """Register a command."""
        ...

    def print(
        self,
        text: Union[str, Text, List[SegmentedTextLine]],
        end: str = "\n"
    ) -> None:
        """Print text to the output box."""
        ...

    def stop(self) -> None:
        """Stop the application."""
        ...
```

**2. Text classes (3 hours)**
```python
# textbox/text.py
from typing import List, Optional, Union
from textbox.text_line import TextLine
from textbox.box_types import Position

class Text:
    def __init__(
        self,
        text: str = "",
        max_line_width: Optional[int] = None
    ) -> None:
        ...

    def copy(self) -> 'Text':
        """Create a deep copy."""
        ...

    def insert(self, text: str) -> None:
        """Insert text at cursor."""
        ...

    def backspace(self) -> None:
        """Delete character before cursor."""
        ...

    def goto(self, position: Position) -> None:
        """Move cursor to position."""
        ...

    @property
    def cursor_position(self) -> Position:
        """Get cursor position with wrapping."""
        ...

    @property
    def lines(self) -> List[TextLine]:
        """Get lines with wrapping applied."""
        ...
```

**3. UI Components (3 hours)**
```python
# textbox/text_box.py, input_box.py, window.py
# Add comprehensive type hints to all public methods
```

**Result:** Better IDE support, catch type errors early

---

## Day 4: Add Protocols (4 hours)

Create interface definitions for duck typing:

```python
# textbox/protocols.py (NEW FILE)
from typing import Protocol, runtime_checkable
from textbox.box_types import Position, BoundingBox

@runtime_checkable
class Renderable(Protocol):
    """Protocol for objects that can be rendered."""

    def render(self, width: int) -> List['SegmentedTextLine']:
        """Render to segmented text lines."""
        ...


@runtime_checkable
class Focusable(Protocol):
    """Protocol for focusable UI elements."""

    @property
    def focused(self) -> bool:
        """Whether this element has focus."""
        ...

    def focus(self) -> None:
        """Give focus to this element."""
        ...

    def blur(self) -> None:
        """Remove focus from this element."""
        ...


@runtime_checkable
class TextEditor(Protocol):
    """Protocol for text editing operations."""

    def insert(self, text: str) -> None:
        """Insert text at cursor."""
        ...

    def delete(self) -> None:
        """Delete character at cursor."""
        ...

    @property
    def cursor_position(self) -> Position:
        """Current cursor position."""
        ...


@runtime_checkable
class Resizable(Protocol):
    """Protocol for resizable objects."""

    def resize(self, new_box: BoundingBox) -> None:
        """Resize to new bounding box."""
        ...

    @property
    def bounding_box(self) -> BoundingBox:
        """Current bounding box."""
        ...
```

**Usage in App.print():**
```python
def print(
    self,
    text: Union[str, Renderable],  # Now any Renderable works!
    end: str = "\n"
) -> None:
    if isinstance(text, str):
        self.workspace.output_box.add_str(text)
    elif isinstance(text, Renderable):
        lines = text.render(self.workspace.output_box.printable_width)
        for line in lines:
            self.workspace.output_box.add_segmented_text_line(line)
```

**Result:** Extensible rendering, cleaner duck typing

---

## Day 5: Add Event System (12 hours)

Create basic event/signal system for component decoupling:

```python
# textbox/events.py (NEW FILE)
from dataclasses import dataclass
from typing import Callable, Dict, List, Any
import time

@dataclass
class Event:
    """Base event class."""
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class TextSubmittedEvent(Event):
    """Fired when text is submitted."""
    text: str


@dataclass
class TextChangedEvent(Event):
    """Fired when text content changes."""
    text: str
    cursor_position: tuple[int, int]


@dataclass
class ModeChangedEvent(Event):
    """Fired when input mode changes."""
    old_mode: str
    new_mode: str


@dataclass
class CommandExecutedEvent(Event):
    """Fired when command is executed."""
    command_name: str
    args: Dict[str, Any]


class EventBus:
    """Simple event bus for pub/sub."""

    def __init__(self):
        self._subscribers: Dict[type, List[Callable]] = {}

    def subscribe(
        self,
        event_type: type[Event],
        handler: Callable[[Event], None]
    ) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def unsubscribe(
        self,
        event_type: type[Event],
        handler: Callable[[Event], None]
    ) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)

    def publish(self, event: Event) -> None:
        """Publish event to all subscribers."""
        event_type = type(event)
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    import logging
                    logging.error(f"Error in event handler: {e}")


# Integration with App
class App:
    def __init__(self):
        self.event_bus = EventBus()
        # ... rest of init

    def on_submit(self, func: Callable[[Text], None]):
        """Decorator for submit handlers."""
        def handler(event: TextSubmittedEvent):
            func(event.text)
        self.event_bus.subscribe(TextSubmittedEvent, handler)
        return func

    # New capability: listen to text changes
    def on_text_changed(self, func: Callable[[str], None]):
        """Listen to text changes."""
        def handler(event: TextChangedEvent):
            func(event.text)
        self.event_bus.subscribe(TextChangedEvent, handler)
        return func
```

**Usage:**
```python
app = App()

@app.on_submit
def handle_submit(text):
    print(f"Submitted: {text}")

@app.on_text_changed
def handle_change(text):
    # Live validation, word count, etc.
    print(f"Text changed: {len(text)} characters")

app.start()
```

**Result:** Extensible, decoupled event handling

---

## Week Summary Progress

### After 1 Week:

**✅ Completed:**
- Removed 2 unnecessary dependencies
- Fixed 9 critical bugs
- Added type hints to all public APIs
- Created Protocol interfaces
- Implemented event system

**📊 Metrics:**
- Dependencies: 3 → 1 (66% reduction)
- Critical bugs: 9 → 0 (100% fixed)
- Type hint coverage: 40% → 75% (+35%)
- Extensibility: Basic → Good (events + protocols)

**💪 Impact:**
- Windows compatible (removed uvloop)
- No crashes/corruption (fixed bugs)
- Better IDE support (type hints)
- Extensible rendering (protocols)
- Decoupled components (events)

---

## Quick Wins Checklist

Copy this to track progress:

```markdown
## Day 1: Cleanup (6 min)
- [ ] Remove uvloop from requirements.txt
- [ ] Remove uvloop import and install() call
- [ ] Remove termcolor from requirements.txt
- [ ] Test that everything still works

## Day 2: Bug Fixes (3-4 hours)
- [ ] Fix text.py:191 - next_line IndexError
- [ ] Fix text_line.py:153 - missing return
- [ ] Fix input_box.py:100 - getter side effect
- [ ] Fix text_box.py:188 - type error
- [ ] Fix input_output_workspace.py:222 - strip
- [ ] Fix window.py:144 - state validation
- [ ] Fix curses_utils.py:71 - assignment
- [ ] Fix color_code.py - Enum + typo
- [ ] Fix __init__.py:78 - type hint
- [ ] Run full test suite

## Day 3: Type Hints (8 hours)
- [ ] Add type hints to App class
- [ ] Add type hints to Text classes
- [ ] Add type hints to UI components
- [ ] Run mypy to verify

## Day 4: Protocols (4 hours)
- [ ] Create textbox/protocols.py
- [ ] Define Renderable protocol
- [ ] Define Focusable protocol
- [ ] Define TextEditor protocol
- [ ] Update App.print() to use Renderable

## Day 5: Events (12 hours)
- [ ] Create textbox/events.py
- [ ] Implement Event base class
- [ ] Implement EventBus
- [ ] Define common event types
- [ ] Integrate with App class
- [ ] Add on_text_changed capability
- [ ] Write example usage
- [ ] Test event system
```

---

## Testing Your Changes

After each day:

```bash
# 1. Run existing tests
python -m pytest textbox/

# 2. Manual smoke test
python examples/llm_interface.py
# - Type some text
# - Try commands
# - Verify no crashes

# 3. Type checking (after Day 3)
mypy textbox/

# 4. Check no regressions
git diff --stat
# Review all changes carefully
```

---

## Expected Outcomes

### Day 1 Outcome:
```bash
$ python -m pip list | grep -E "(uvloop|termcolor)"
# Nothing - dependencies removed

$ python examples/llm_interface.py
# Works on Windows and Linux
```

### Day 2 Outcome:
```bash
$ python -m pytest textbox/
# All tests pass, no critical bugs

$ python examples/llm_interface.py
# No crashes during normal usage
```

### Day 3 Outcome:
```bash
$ mypy textbox/__init__.py textbox/text.py
# Success: no issues found

# IDE shows type hints:
app.print(  # Shows signature with types
```

### Day 4 Outcome:
```python
from textbox.protocols import Renderable

class MyCustomTable:
    def render(self, width: int):
        return [...]

app.print(MyCustomTable())  # Works!
```

### Day 5 Outcome:
```python
@app.on_text_changed
def live_validation(text):
    if len(text) > 100:
        print("Warning: Over 100 characters")

# Now you have reactive capabilities!
```

---

## Next Steps After Week 1

Once immediate improvements are done, proceed to:

1. **Week 2-3:** Add design patterns
   - Command pattern with undo/redo
   - State machine for modes
   - Strategy pattern for rendering
   - See `05-architectural-evolution.md`

2. **Week 4:** Testing infrastructure
   - Snapshot testing
   - Mock terminal backend
   - Integration tests
   - Coverage >80%

3. **Week 5+:** Feature enhancements
   - Visual mode
   - Registers (copy/paste)
   - Search with `/` and `?`
   - More vim commands

---

## Success Criteria

After this 1-week sprint, you should have:

✅ **Zero critical bugs**
✅ **Windows compatibility**
✅ **Type hints on public APIs**
✅ **Extensible rendering** (protocols)
✅ **Event system** (decoupled components)
✅ **1 dependency** (down from 3)
✅ **Foundation for advanced patterns**

**Your codebase will be:**
- More professional
- Easier to maintain
- Better documented (via types)
- More extensible
- Production-ready foundation

**Time to start! Begin with Day 1 cleanup - it only takes 6 minutes.**

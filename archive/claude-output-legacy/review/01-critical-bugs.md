# Critical Bugs - Must Fix Immediately

This document lists all critical bugs found in the textbox library that can cause crashes, data corruption, or undefined behavior.

---

## Bug #1: IndexError in next_line Property 🔥

**File**: `textbox/text.py`
**Line**: 191-193
**Severity**: CRITICAL - Causes crash

### Current Code
```python
@property
def next_line(self):
    if self._line_ptr >= len(self._text_lines):  # BUG: Should be >=  - 1
        return None
    return self._text_lines[self._line_ptr + 1]
```

### Problem
When `_line_ptr` is at the last line, `self._line_ptr + 1` equals `len(self._text_lines)`, which causes IndexError because valid indices are 0 to len-1.

### Impact
- Crashes when trying to access next line while at document end
- Affects any code calling `text.next_line` property
- Can crash during cursor navigation

### Reproduction
```python
from textbox import Text

text = Text("line1\nline2")
text.to_last_line()  # Move to line 1 (index 1)
next_line = text.next_line  # CRASHES with IndexError
```

### Fix
```python
@property
def next_line(self):
    if self._line_ptr >= len(self._text_lines) - 1:  # Fixed
        return None
    return self._text_lines[self._line_ptr + 1]
```

### Testing
```python
def test_next_line_at_end():
    text = Text("line1\nline2")
    text.to_last_line()
    assert text.next_line is None  # Should not crash
```

---

## Bug #2: Missing Return in replace_character 🔥

**File**: `textbox/text_line.py`
**Line**: 153-157
**Severity**: CRITICAL - Causes data corruption

### Current Code
```python
if column_ptr == len(self._text):
    self._text = self._text + ch
self._text = (
    self._text[:column_ptr] + TextSegment(ch, self._text[column_ptr].color_pair) + self._text[column_ptr + 1 :]
)
```

### Problem
Missing `return` statement after line 154. When `column_ptr == len(self._text)`, BOTH blocks execute:
1. First appends character
2. Then tries to replace character at position that now exists but shouldn't

Result: Unpredictable text corruption.

### Impact
- Corrupts text when replacing at end of line
- Unpredictable behavior depending on text content
- Silent data corruption (no error raised)

### Reproduction
```python
from textbox.text_line import TextLine

line = TextLine("hello")
line.replace_character("!", 5)  # Replace at end
# Expect: "hello!"
# Actual: Corrupted text (depends on implementation details)
```

### Fix
```python
if column_ptr == len(self._text):
    self._text = self._text + ch
    return  # ADD THIS LINE
self._text = (
    self._text[:column_ptr] + TextSegment(ch, self._text[column_ptr].color_pair) + self._text[column_ptr + 1 :]
)
```

### Testing
```python
def test_replace_at_end():
    line = TextLine("hello")
    line.replace_character("!", 5)
    assert str(line) == "hello!"

def test_replace_in_middle():
    line = TextLine("hello")
    line.replace_character("a", 1)
    assert str(line) == "hallo"
```

---

## Bug #3: Property Getter Has Side Effect 🔥

**File**: `textbox/input_box.py`
**Line**: 99-102
**Severity**: CRITICAL - Violates property contract

### Current Code
```python
@property
def edit_mode(self):
    self.text.edit_mode = True  # BUG: Getter modifies state!

@edit_mode.setter
def edit_mode(self, value: bool):
    self.text.edit_mode = value
```

### Problem
Property getter modifies state instead of just returning a value. Every time you read `input_box.edit_mode`, it sets edit mode to True!

This violates the fundamental principle that getters should not have side effects.

### Impact
- Reading edit_mode changes application state
- Impossible to check edit mode without changing it
- Debugging is extremely difficult
- IDE refactorings that access property can break code

### Reproduction
```python
from textbox.input_box import InputBox

box = InputBox(...)
box.edit_mode = False  # Set to False
mode = box.edit_mode   # Just reading it...
# mode is now True! (and box is in edit mode)
```

### Fix
```python
@property
def edit_mode(self):
    return self.text.edit_mode  # Just return, don't modify!

@edit_mode.setter
def edit_mode(self, value: bool):
    self.text.edit_mode = value
```

### Testing
```python
def test_edit_mode_getter_has_no_side_effects():
    box = InputBox(...)
    box.edit_mode = False
    _ = box.edit_mode  # Read it
    assert box.edit_mode == False  # Should still be False
```

---

## Bug #4: Wrong Type Assignment in erase() 🔥

**File**: `textbox/text_box.py`
**Line**: 187-189
**Severity**: CRITICAL - Type error

### Current Code
```python
def erase(self):
    self._text_list = []  # BUG: Should be TextList(), not []
    self.window.erase(verbose=self.verbose)
```

### Problem
`_text_list` should be a `TextList` instance, not a plain list. This breaks all subsequent operations that call TextList methods.

### Impact
- Type error on next operation using _text_list
- Methods like `add_text()` will fail
- Silent failure until _text_list is accessed

### Reproduction
```python
from textbox.text_box import TextBox

box = TextBox(...)
box.add_text("Hello")
box.erase()
box.add_text("World")  # CRASHES: list has no method 'add_text'
```

### Fix
```python
def erase(self):
    self._text_list = TextList()  # Create new TextList instance
    self._text_list.max_line_width = self.printable_width  # Set width
    self.window.erase(verbose=self.verbose)
```

### Testing
```python
def test_erase_maintains_type():
    box = TextBox(...)
    box.add_text("Hello")
    box.erase()
    assert isinstance(box._text_list, TextList)
    box.add_text("World")  # Should not crash
```

---

## Bug #5: Strip Result Not Assigned 🔥

**File**: `textbox/input_output_workspace.py`
**Line**: 222
**Severity**: HIGH - Data not cleaned

### Current Code
```python
def execute_command(self, text):
    logger.info(f"Command: {text}")
    text.strip()  # BUG: Result discarded!
    command = text.split(" ")[0]
```

### Problem
`str.strip()` returns a new string but the result is never assigned. The original `text` remains unchanged with leading/trailing whitespace.

### Impact
- Commands with whitespace (e.g., " quit ") don't match
- User frustration when commands don't work
- Inconsistent command parsing

### Reproduction
```python
# User types ":quit " (with trailing space)
# Command doesn't match "quit" because of space
# Nothing happens
```

### Fix
```python
def execute_command(self, text):
    logger.info(f"Command: {text}")
    text = text.strip()  # Assign the result!
    command = text.split(" ")[0]
```

### Testing
```python
def test_execute_command_strips_whitespace():
    workspace = InputOutputWorkspace(...)
    workspace.execute_command(" quit ")  # Should work
    # Verify quit was executed
```

---

## Bug #6: State Updated Before Validation 🔥

**File**: `textbox/window.py`
**Line**: 144-157
**Severity**: HIGH - State corruption

### Current Code
```python
def resize(self, box: BoundingBox, verbose=False):
    if verbose:
        logger.info("Resizing window to %s", box)
    self.dimensions = box.dimensions  # State updated
    self.position = box.position       # State updated
    try:
        self._local_window.resize(*box.dimensions)
    except curses.error:
        raise ValueError("Failed to resize window to %s", box.dimensions)

    try:
        self._local_window.mvwin(*box.position)
    except curses.error:
        raise ValueError("Failed to move window to %s", box.position)
```

### Problem
Python object state (dimensions, position) is updated BEFORE attempting curses operations. If curses operations fail, Python state is inconsistent with actual window state.

### Impact
- Window thinks it's size X but curses window is size Y
- Subsequent operations use wrong coordinates
- Drawing operations fail or draw in wrong location
- Application state becomes corrupted

### Reproduction
```python
window = Window(...)
try:
    window.resize(invalid_box)  # Curses fails
except ValueError:
    pass
# window.dimensions is wrong size now!
```

### Fix
```python
def resize(self, box: BoundingBox, verbose=False):
    if verbose:
        logger.info("Resizing window to %s", box)

    # Try curses operations FIRST
    try:
        self._local_window.resize(*box.dimensions)
        self._local_window.mvwin(*box.position)
    except curses.error as e:
        raise ValueError(f"Failed to resize/move window to {box}: {e}")

    # Only update state if successful
    self.dimensions = box.dimensions
    self.position = box.position
```

### Testing
```python
def test_resize_failure_leaves_state_unchanged():
    window = Window(...)
    original_dims = window.dimensions
    try:
        window.resize(invalid_box)
    except ValueError:
        pass
    assert window.dimensions == original_dims
```

---

## Bug #7: Assignment vs Comparison 🔥

**File**: `textbox/curses_utils.py`
**Line**: 71
**Severity**: MEDIUM - Logic error

### Current Code
```python
finally:
    if state == 1:
        if "stdscr" in locals():
            stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        state == 0  # BUG: Should be state = 0
```

### Problem
Uses comparison operator `==` instead of assignment `=`. State is never reset to 0.

### Impact
- State variable not reset (though doesn't affect functionality since function ends)
- Indicates confusion about state management
- Could cause issues if code is refactored

### Fix
```python
finally:
    if state == 1:
        if "stdscr" in locals():
            stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        state = 0  # Fix: Assignment not comparison
```

### Testing
```python
# This is more of a code quality issue
# Consider removing state variable entirely and using try-finally properly
```

---

## Bug #8: ColorCode Not Using Enum 🔥

**File**: `textbox/color_code.py`
**Line**: 1-17
**Severity**: MEDIUM - Type safety issue

### Current Code
```python
from enum import Enum  # Imported but not used!

class ColorCode:  # Should be ColorCode(Enum)
    WHITE = 0
    GREY = 1
    # ...
    OUPTUT_TEXT = 7  # TYPO: Should be OUTPUT_TEXT
    DEFAULT = None
```

### Problems
1. Imports Enum but doesn't use it
2. Not a proper enum means no type safety
3. Typo in public API: OUPTUT_TEXT
4. Mixed types (integers + None)

### Impact
- No IDE autocomplete for color codes
- No type checking of color values
- Public API has embarrassing typo
- Can't iterate over available colors

### Fix
```python
from enum import IntEnum

class ColorCode(IntEnum):
    WHITE = 0
    GREY = 1
    DARK_RED = 2
    GREEN = 3
    YELLOW = 4
    DARK_BLUE = 5
    DARK_PURPLE = 6
    OUTPUT_TEXT = 7  # Fixed typo
    LIGHT_BLUE = 7
    OFF_WHITE = 195
    LIGHT_PURPLE = 14
    # Handle DEFAULT separately or use -1

# Deprecated alias for backwards compatibility
OUPTUT_TEXT = OUTPUT_TEXT  # Warn on use
```

### Testing
```python
def test_color_code_is_enum():
    assert isinstance(ColorCode.WHITE, ColorCode)
    assert ColorCode.WHITE == 0

def test_can_iterate_colors():
    colors = list(ColorCode)
    assert len(colors) > 0
```

---

## Bug #9: Type Hint Mismatch in on_submit 🔥

**File**: `textbox/__init__.py`
**Line**: 78, 204 (input_output_workspace.py)
**Severity**: MEDIUM - Type checker will report false errors

### Current Code
```python
# __init__.py:78
def on_submit(self, func: Callable[[str], None]):  # Says str
    self._submit_callbacks.append(func)
    return func

# But actually called with:
# input_output_workspace.py:204
self._submit_callback(self.focused_box.text.copy())  # Passes Text object!
```

### Problem
Type hint says callback receives `str`, but it actually receives `Text` object. This will cause mypy/pyright to report errors on correct code.

### Impact
- Type checkers report false positives
- Users write wrong callback signatures
- Runtime errors when users expect string

### Reproduction
```python
from textbox import App

app = App()

@app.on_submit
def handle(text: str):  # User follows type hint
    # Type checker says this is correct
    print(text.upper())  # But crashes at runtime!
    # AttributeError: 'Text' object has no attribute 'upper'
```

### Fix Option 1: Change type hint to match reality
```python
def on_submit(self, func: Callable[[Text], None]):
    self._submit_callbacks.append(func)
    return func
```

### Fix Option 2: Convert to string before calling
```python
# In input_output_workspace.py:204
self._submit_callback(str(self.focused_box.text))
```

### Recommendation
Use Option 1 - users need access to Text methods like color, lines, etc.

### Testing
```python
def test_on_submit_receives_text_object():
    app = App()
    received = []

    @app.on_submit
    def handler(text: Text):
        received.append(text)

    # Simulate submit
    # Verify received[0] is Text instance
```

---

## Priority Fix Order

### Day 1 - Crashes (2-3 hours)
1. Bug #1: IndexError in next_line
2. Bug #2: Missing return in replace_character
3. Bug #3: Property getter side effect
4. Bug #4: Wrong type in erase()

### Day 2 - Data Integrity (1-2 hours)
5. Bug #5: Strip result not assigned
6. Bug #6: State updated before validation

### Day 3 - Type Safety (1-2 hours)
7. Bug #8: ColorCode enum + typo fix
8. Bug #9: Type hint mismatch
9. Bug #7: Assignment vs comparison

---

## Verification Checklist

After fixing all bugs:

- [ ] All 9 bugs have fixes committed
- [ ] Tests added for each bug (9 new tests minimum)
- [ ] All tests pass
- [ ] No regressions in existing tests
- [ ] Type checking passes (mypy)
- [ ] Manual testing of affected features
- [ ] CHANGELOG.md updated with bug fixes

---

## Preventing Future Bugs

### Immediate Actions
1. Set up CI to run tests automatically
2. Add pytest configuration
3. Enable type checking in CI
4. Add pre-commit hooks

### Long-term Actions
1. Achieve 80%+ test coverage
2. Add property-based testing for edge cases
3. Add integration tests
4. Set up mutation testing
5. Regular code reviews

---

## Estimated Fix Time

| Bug | Severity | Time to Fix | Time to Test |
|-----|----------|-------------|--------------|
| #1 | Critical | 5 min | 10 min |
| #2 | Critical | 5 min | 10 min |
| #3 | Critical | 5 min | 10 min |
| #4 | Critical | 10 min | 10 min |
| #5 | High | 2 min | 5 min |
| #6 | High | 15 min | 15 min |
| #7 | Medium | 2 min | 5 min |
| #8 | Medium | 20 min | 15 min |
| #9 | Medium | 10 min | 10 min |

**Total: ~2-3 hours** (including testing)

These bugs should be fixed before any other work is done on the project.

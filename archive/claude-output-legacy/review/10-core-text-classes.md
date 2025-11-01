# Core Text Classes Analysis

This document contains detailed analysis of the text abstraction layer: TextSegment, SegmentedTextLine, TextLine, and Text.

---

## Architecture Overview

The textbox library uses a four-layer text abstraction:

```
Text (Multi-line text with cursor)
  ↓
TextLine (Single line, no newlines)
  ↓
SegmentedTextLine (Line with multiple colored segments)
  ↓
TextSegment (String + color pair)
```

This is a **well-designed hierarchy** with clear separation of concerns.

---

## TextSegment (`text_segment.py`)

### Purpose
Atomic text unit with color information.

### Strengths
- Simple, focused class
- Immutable-style operations (returns new instances)
- Color pair tracking

### Issues Found

#### 1. No Validation in `__init__` (Line 9-14)
```python
def __init__(self, text: str = None, color_pair: int = ColorCode.DEFAULT):
    if text is None:
        self._text = ""
    else:
        self._text = text  # No validation!
    self.color_pair = color_pair
```

**Problems:**
- Doesn't validate `text` is actually a string
- Doesn't validate `color_pair` is valid
- Allows newlines (violates TextLine contract)

**Fix:**
```python
def __init__(self, text: str = None, color_pair: int = ColorCode.DEFAULT):
    if text is None:
        self._text = ""
    elif not isinstance(text, str):
        raise TypeError(f"text must be str, got {type(text)}")
    elif "\n" in text:
        raise ValueError("TextSegment cannot contain newlines")
    else:
        self._text = text

    if not isinstance(color_pair, int) and color_pair is not None:
        raise TypeError(f"color_pair must be int or None, got {type(color_pair)}")
    self.color_pair = color_pair
```

#### 2. `isalnum()` Method Incorrect (Line 19-20)
```python
def isalnum(self):
    return self._text.isalnum()
```

**Problem:** For multi-character segments, this doesn't work as expected in word navigation logic which expects character-level behavior.

**Example:**
```python
seg = TextSegment("hello world")
seg.isalnum()  # Returns False (space breaks it)
# But used in word navigation as if it's single character
```

**Fix:** Either restrict to single characters or clarify purpose:
```python
def isalnum(self):
    """Check if ALL characters are alphanumeric."""
    return len(self._text) > 0 and self._text.isalnum()
```

#### 3. Inconsistent `__add__` Behavior (Line 37-45)
```python
def __add__(self, other: Union[str, "TextSegment"]):
    if isinstance(other, str):
        return TextSegment(self._text + other, self.color_pair)
    elif isinstance(other, TextSegment):
        if self.color_pair != other.color_pair:
            raise ValueError("Cannot add TextSegments with different color pairs")
        return TextSegment(self._text + other._text, self.color_pair)
```

**Problem:**
- Adding string uses self's color (ok)
- Adding different-color TextSegment raises error (restrictive)
- Should return SegmentedTextLine for mixed colors

**Better Design:**
```python
def __add__(self, other: Union[str, "TextSegment", "SegmentedTextLine"]):
    if isinstance(other, str):
        return TextSegment(self._text + other, self.color_pair)
    elif isinstance(other, TextSegment):
        if self.color_pair == other.color_pair:
            return TextSegment(self._text + other._text, self.color_pair)
        else:
            # Return SegmentedTextLine with both segments
            return SegmentedTextLine([self, other])
    elif isinstance(other, SegmentedTextLine):
        return SegmentedTextLine([self]) + other
```

### Missing Features
- No substring/slice support
- No search functionality
- No width calculation (important for terminal display)

### Test Coverage
**Current: 0% (no test file)**

**Needed Tests:**
- Initialization validation
- String addition
- TextSegment addition (same color)
- TextSegment addition (different colors)
- isalnum behavior
- split functionality
- copy method
- Equality and hashing

---

## SegmentedTextLine (`segmented_text_line.py`)

### Purpose
Collection of TextSegments representing a single line with multiple colors.

### Strengths
- Automatic segment reduction/merging
- Slice support
- Color-aware operations

### Issues Found

#### 1. Accessing Private Members (Line 39)
```python
def reduce(self):
    for segment in self._segments:
        if segment._text == "":  # Accessing private _text
            continue
```

**Problem:** Accesses `_text` private member of TextSegment.

**Fix:**
```python
if len(segment) == 0:
    continue
```

#### 2. Performance Issue - No Lazy Evaluation (Line 35-47)
```python
def reduce(self):
    """Called after EVERY modification"""
    # O(n) operation on every change
```

**Problem:** Reduction happens eagerly after every operation. For large texts with many edits, this is wasteful.

**Suggestion:** Consider lazy evaluation or dirty flag.

#### 3. Wrong Exception Type (Line 96-97)
```python
if item.step is not None and item.step != 1:
    raise IndexError("SegmentedTextLine does not support slicing with a step")
```

**Problem:** Should be `NotImplementedError` not `IndexError`.

**Fix:**
```python
if item.step is not None and item.step != 1:
    raise NotImplementedError("SegmentedTextLine does not support slicing with a step")
```

#### 4. Complex Slicing Logic (Lines 95-147)
50+ lines of complex nested conditionals for slicing.

**Problem:** Hard to maintain, test, and debug.

**Refactor Suggestion:**
```python
def __getitem__(self, item):
    if isinstance(item, int):
        return self._getitem_single(item)
    elif isinstance(item, slice):
        return self._getitem_slice(item)
    else:
        raise TypeError(f"indices must be integers or slices, not {type(item)}")

def _getitem_single(self, index: int) -> TextSegment:
    # Handle single index
    ...

def _getitem_slice(self, s: slice) -> Union[TextSegment, "SegmentedTextLine"]:
    # Handle slice
    ...
```

### Test Coverage
**Current: ~80% (good)**

**Additional Tests Needed:**
- Edge cases with empty segments
- Negative indices
- Step slicing (should raise NotImplementedError)
- reduce() behavior validation
- Color preservation through operations

---

## TextLine (`text_line.py`)

### Purpose
Single line of text (no newlines) with cursor operations and word navigation.

### Strengths
- Clean API for line manipulation
- Word navigation support
- Cursor position calculations with wrapping
- Color tracking via SegmentedTextLine

### Issues Found

#### 1. Bug: Missing Return (Line 153-157) - See Bug #2
Already documented in critical bugs.

#### 2. Incomplete Validation in Setter (Line 116-117)
```python
if "\n" in value:
    raise ValueError("TextLine cannot contain newlines")
```

**Problem:** Only works for strings, fails for other types before conversion.

**Fix:**
```python
@text.setter
def text(self, value):
    # Convert first
    if isinstance(value, str):
        if "\n" in value:
            raise ValueError("TextLine cannot contain newlines")
        self._text = SegmentedTextLine(TextSegment(value))
    # ... handle other types ...

    # Validate after conversion
    if "\n" in str(self._text):
        raise ValueError("TextLine cannot contain newlines")
```

#### 3. Confusing Backspace Error (Line 197-198)
```python
if len(self._text) == 0:
    raise ValueError("Cannot backspace an empty line")
```

**Problem:** In Text context, backspace at line start should join with previous line. This error prevents that at TextLine level.

**Design Question:** Should TextLine know about multi-line context?

#### 4. Incorrect Return Type Hint (Line 159)
```python
def delete_to_end(self, column_ptr: int) -> str:
    # ...
    return remainder  # Actually returns SegmentedTextLine
```

**Fix:**
```python
def delete_to_end(self, column_ptr: int) -> SegmentedTextLine:
```

### Missing Features
- No regex support for word boundaries
- No Unicode-aware width calculation
- No way to get character at position with color

### Test Coverage
**Current: ~85% (good)**

**Additional Tests Needed:**
- Word navigation with punctuation
- Word navigation with Unicode
- Color preservation during edits
- Rich text operations
- Line wrapping edge cases

---

## Text (`text.py`)

### Purpose
Multi-line text with cursor, editing operations, and wrapping support.

### Strengths
- Comprehensive cursor management
- Edit mode awareness
- Word navigation across lines
- Wrapping support

### Issues Found

#### 1. Bug: IndexError in next_line (Line 191) - See Bug #1
Already documented in critical bugs.

#### 2. Typo in `__repr__` (Line 384)
```python
edit_moode={self._edit_mode}  # Should be edit_mode
```

#### 3. Property Has Side Effects (Line 179-181)
```python
@property
def current_line(self):
    if len(self._text_lines) == 0:
        return TextLine("")  # Creates temporary object
    return self._text_lines[self._line_ptr]
```

**Problem:** Returns temporary TextLine if empty. Modifications to it are lost.

**Better Design:**
```python
@property
def current_line(self):
    if len(self._text_lines) == 0:
        raise IndexError("No lines in text")
    return self._text_lines[self._line_ptr]
```

Or ensure empty text always has one empty line.

#### 4. Inconsistent Initialization (Line 23-31)
```python
def __init__(self, text: str = "", max_line_width: int = None):
    self._text_lines: List[TextLine] = []
    self._line_ptr = 0
    self._column_ptr = 0
    # ...
    self.text = text  # Moves cursor to end!
```

**Problem:** Cursor starts at (0, 0) then immediately moves to end when text is set. Inconsistent initial state.

#### 5. No Validation in goto (Line 249-251)
```python
def goto(self, position: Position):
    self._line_ptr = position.lineno  # No validation
    self._column_ptr = position.colno
```

**Fix:** See Bug #9 fix in critical bugs document.

#### 6. O(n²) cursor_position (Line 95-108)
```python
@property
def cursor_position(self) -> Position:
    # ...
    line_offset = 0
    for idx in range(self._line_ptr):  # O(n) every time
        line_offset += self._text_lines[idx].line_count(self._max_line_width)
```

**Problem:** Called frequently, iterates all previous lines.

**Fix:** Cache line offsets (see architecture improvements section).

#### 7. Incorrect Type Hint (Line 111)
```python
@property
def lines(self) -> List[TextLine]:
    if self._max_line_width is None:
        return [str(text_line) for text_line in self._text_lines]  # Returns List[str]!
```

**Fix:**
```python
@property
def lines(self) -> List[TextLine]:
    if self._max_line_width is None:
        return self._text_lines.copy()  # Return actual TextLines
    # ... rest
```

Or rename to `visual_lines` and update type hint to `Union[List[str], List[TextLine]]`.

#### 8. Complex Backspace Logic (Line 283-312)
30 lines of complex branching for backspace operation.

**Refactor Suggestion:**
```python
def backspace(self):
    """Delete the character before the cursor."""
    if self.column_ptr == 0:
        self._backspace_at_line_start()
    else:
        self._backspace_in_line()

def _backspace_at_line_start(self):
    if self._line_ptr == 0:
        return  # At start of text
    # ... rest of logic

def _backspace_in_line(self):
    self.current_line.backspace(self.column_ptr)
    self.decrement_column_ptr()
```

### Missing Features
- No undo/redo
- No search/replace
- No event system for observing changes
- No multi-cursor support
- No transaction support (atomicity)

### Test Coverage
**Current: ~75% (adequate but needs improvement)**

**Additional Tests Needed:**
- copy() method
- char_at_cursor with bounds
- goto() validation
- Color preservation
- Edge cases with max_line_width
- Word navigation across multiple lines

---

## API Design Recommendations

### 1. Consistent Naming
**Current:** Mix of properties and methods for similar operations

**Recommendation:**
```python
# Properties for reading state
current_line: TextLine
cursor_position: Position
edit_mode: bool

# Methods for actions
def move_to_start_of_line() -> None
def move_to_end_of_line() -> None
def move_to_next_word() -> None
```

### 2. Separate Logical and Visual
**Current:** `lines` property returns different types based on wrapping

**Recommendation:**
```python
@property
def logical_lines(self) -> List[TextLine]:
    """Get lines as stored (no wrapping)."""
    return self._text_lines.copy()

@property
def visual_lines(self) -> List[TextLine]:
    """Get lines as displayed (with wrapping)."""
    if self._max_line_width is None:
        return self.logical_lines
    # ... apply wrapping
```

### 3. Explicit Cursor vs Pointer
**Current:** Mix of "cursor", "pointer", "ptr" terminology

**Recommendation:** Use "cursor" consistently:
```python
self._cursor_line: int
self._cursor_column: int

@property
def cursor_position(self) -> Position:
    return Position(self._cursor_line, self._cursor_column)
```

### 4. Validation Methods
**Current:** Validation scattered through code

**Recommendation:**
```python
def _validate_line_index(self, line_idx: int) -> None:
    if line_idx < 0 or line_idx >= len(self._text_lines):
        raise IndexError(f"Line {line_idx} out of range [0, {len(self._text_lines)-1}]")

def _validate_column_index(self, col_idx: int, line_idx: int = None) -> None:
    if line_idx is None:
        line_idx = self._line_ptr
    max_col = len(self._text_lines[line_idx])
    if col_idx < 0 or col_idx > max_col:
        raise IndexError(f"Column {col_idx} out of range [0, {max_col}]")
```

---

## Performance Optimization Recommendations

### 1. Cache Line Offsets
```python
class Text:
    def __init__(self, ...):
        self._line_offset_cache: Optional[List[int]] = None

    def _invalidate_cache(self):
        self._line_offset_cache = None

    def _build_cache(self):
        if self._line_offset_cache is None:
            # Build cache
            pass
```

### 2. Lazy Reduce in SegmentedTextLine
```python
class SegmentedTextLine:
    def __init__(self, ...):
        self._needs_reduce = True

    def _ensure_reduced(self):
        if self._needs_reduce:
            self.reduce()
            self._needs_reduce = False
```

### 3. Avoid Unnecessary Copies
```python
# Current
for text_line in self._text_lines:
    sub_line = text_line.copy()  # Always copies

# Better
for text_line in self._text_lines:
    if needs_modification:
        sub_line = text_line.copy()
    else:
        sub_line = text_line
```

---

## Summary

### Strengths
- ✅ Well-designed abstraction layers
- ✅ Clear separation of concerns
- ✅ Good test coverage for most components

### Critical Issues
- ❌ 3 critical bugs in this layer
- ❌ TextSegment has 0% test coverage
- ❌ Missing validation throughout
- ❌ Performance issues (O(n²) operations)

### Priority Actions
1. Fix 3 critical bugs
2. Add TextSegment tests
3. Add validation to constructors
4. Optimize cursor_position calculation
5. Refactor complex methods (backspace, slicing)
6. Fix type hints
7. Improve error messages

### Estimated Effort
- Bug fixes: 1 day
- Tests: 2 days
- Validation: 1 day
- Optimization: 2 days
- Refactoring: 3 days

**Total: ~2 weeks** for complete overhaul of text layer

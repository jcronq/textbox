# Test Coverage Analysis

## Current Test Coverage: ~25%

### Test Files Found
1. `box_types_test.py` - 5 tests ✅
2. `text_line_test.py` - 11 tests ✅
3. `segmented_text_line_test.py` - 6 tests ✅
4. `text_test.py` - 19 tests ✅
5. `text_list_test.py` - 16 tests ✅

**Total: 57 tests covering only low-level data structures**

---

## Coverage by Module

| Module | Coverage | Test Count | Status |
|--------|----------|------------|--------|
| **box_types.py** | ~90% | 5 | ✅ Excellent |
| **text_line.py** | ~85% | 11 | ✅ Good |
| **segmented_text_line.py** | ~80% | 6 | ✅ Good |
| **text.py** | ~75% | 19 | ⚠️ Adequate |
| **text_list.py** | ~70% | 16 | ⚠️ Adequate |
| **text_segment.py** | 0% | 0 | ❌ Missing |
| **input_box.py** | 0% | 0 | ❌ Missing |
| **text_box.py** | 0% | 0 | ❌ Missing |
| **window.py** | 0% | 0 | ❌ Missing |
| **input_output_workspace.py** | 0% | 0 | ❌ Missing |
| **input_manager.py** | 0% | 0 | ❌ Missing |
| **App (__init__.py)** | 0% | 0 | ❌ Missing |
| **colored.py** | 0% | 0 | ❌ Missing |
| **curses_utils.py** | 0% | 0 | ❌ Missing |
| **signals.py** | 0% | 0 | ❌ Missing |

---

## Critical Missing Tests

### 1. App Class Tests (Priority: CRITICAL)

**File to create:** `textbox/app_test.py`

```python
import pytest
from textbox import App, Text, TextSegment, ColorCode

def test_app_initialization():
    """App should initialize with empty callbacks."""
    app = App()
    assert app._submit_callbacks == []
    assert "help" in app._user_defined_commands

def test_on_submit_decorator():
    """on_submit should register callback."""
    app = App()
    called = []

    @app.on_submit
    def handler(text: Text):
        called.append(text)

    assert handler in app._submit_callbacks

def test_command_decorator():
    """command decorator should register command."""
    app = App()

    @app.command("test", help="Test command")
    def test_cmd(cmd_str: str):
        pass

    assert "test" in app._user_defined_commands

def test_command_with_alternate_names():
    """command decorator should register alternate names."""
    app = App()

    @app.command("quit", "q", "exit", help="Quit")
    def quit_cmd(cmd_str: str):
        pass

    assert "quit" in app._user_defined_commands
    assert "q" in app._user_defined_commands
    assert "exit" in app._user_defined_commands

def test_print_requires_running_app():
    """print should fail if app not running."""
    app = App()
    with pytest.raises(RuntimeError, match="not running"):
        app.print("Hello")

def test_default_help_command():
    """App should have default help command."""
    app = App()
    assert "help" in app._user_defined_commands
    assert "help" in app._user_defined_commands_help

# Need 15+ more tests...
```

### 2. TextSegment Tests (Priority: CRITICAL)

**File to create:** `textbox/text_segment_test.py`

```python
import pytest
from textbox.text_segment import TextSegment
from textbox.color_code import ColorCode

def test_initialization_with_text():
    seg = TextSegment("hello", ColorCode.WHITE)
    assert str(seg) == "hello"
    assert seg.color_pair == ColorCode.WHITE

def test_initialization_with_none():
    seg = TextSegment(None, ColorCode.WHITE)
    assert str(seg) == ""

def test_initialization_rejects_non_string():
    with pytest.raises(TypeError):
        TextSegment(123, ColorCode.WHITE)

def test_initialization_rejects_newlines():
    with pytest.raises(ValueError):
        TextSegment("hello\nworld", ColorCode.WHITE)

def test_add_string():
    seg = TextSegment("hello", ColorCode.WHITE)
    result = seg + " world"
    assert str(result) == "hello world"
    assert result.color_pair == ColorCode.WHITE

def test_add_same_color_segment():
    seg1 = TextSegment("hello", ColorCode.WHITE)
    seg2 = TextSegment(" world", ColorCode.WHITE)
    result = seg1 + seg2
    assert str(result) == "hello world"

def test_add_different_color_raises():
    seg1 = TextSegment("hello", ColorCode.WHITE)
    seg2 = TextSegment(" world", ColorCode.BLUE)
    with pytest.raises(ValueError):
        seg1 + seg2

def test_isalnum_single_char():
    assert TextSegment("a").isalnum()
    assert not TextSegment(" ").isalnum()

def test_copy():
    seg = TextSegment("hello", ColorCode.WHITE)
    copy = seg.copy()
    assert str(copy) == str(seg)
    assert copy is not seg

def test_split():
    seg = TextSegment("hello", ColorCode.WHITE)
    parts = seg.split(2)
    assert len(parts) == 3
    # Test each part

# Need 10+ more tests...
```

### 3. InputBox Tests (Priority: HIGH)

**File to create:** `textbox/input_box_test.py`

```python
import pytest
from textbox.input_box import InputBox, InputHistory
from textbox.text import Text

def test_input_history_initialization():
    history = InputHistory(max_size=10)
    assert history._max_size == 10
    assert len(history._history) == 0

def test_input_history_append():
    history = InputHistory(max_size=3)
    history.append(Text("line1"))
    history.append(Text("line2"))
    assert len(history._history) == 2

def test_input_history_max_size():
    history = InputHistory(max_size=2)
    history.append(Text("line1"))
    history.append(Text("line2"))
    history.append(Text("line3"))
    assert len(history._history) == 2
    assert str(history._history[0]) == "line2"

def test_input_history_previous():
    history = InputHistory()
    history.append(Text("line1"))
    history.append(Text("line2"))
    prev = history.previous()
    assert str(prev) == "line2"

def test_input_history_previous_at_start():
    history = InputHistory()
    history.append(Text("line1"))
    history.previous()
    history.previous()
    prev = history.previous()
    assert str(prev) == "line1"  # Stays at start

def test_input_history_empty_previous():
    history = InputHistory()
    prev = history.previous()
    assert prev is None

# Need 20+ more tests...
```

---

## Edge Cases Not Tested

### Critical Edge Cases

1. **Unicode Handling**
   - Emoji in text
   - Multi-byte characters
   - Combining characters
   - RTL text

2. **Boundary Conditions**
   - Empty text operations
   - Single character operations
   - Maximum length strings
   - Zero-width windows

3. **Color Management**
   - Invalid color pairs
   - Color transitions
   - DEFAULT color handling
   - Mixed color operations

4. **Async Operations**
   - Multiple rapid keypresses
   - Race conditions
   - Exception handling
   - Cleanup on error

5. **State Transitions**
   - Mode changes
   - Focus changes
   - Resize during input
   - Submit while editing

---

## Test Quality Issues

### Problems Found

1. **Duplicate Test Names** in `text_test.py`
   ```python
   # Line 369
   def test_start_of_next_word():
       ...

   # Line 375 - DUPLICATE!
   def test_start_of_next_word():
       ...
   ```

2. **Duplicate Test Names** in `text_list_test.py`
   ```python
   # Line 89
   def test_getitem_negative_slice():
       ...

   # Line 97 - DUPLICATE!
   def test_getitem_negative_slice():
       ...
   ```

3. **No Test Organization**
   - All tests in flat structure
   - No test classes
   - No logical grouping

4. **Missing Docstrings**
   - Tests don't explain what they're testing
   - No context for edge cases

5. **No Parametrized Tests**
   - Many similar tests could use `@pytest.mark.parametrize`

---

## Recommended Test Structure

```
textbox/
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── unit/
│   │   ├── test_box_types.py
│   │   ├── test_text_segment.py  # NEW - CRITICAL
│   │   ├── test_segmented_text_line.py
│   │   ├── test_text_line.py
│   │   ├── test_text.py
│   │   ├── test_text_list.py
│   │   ├── test_colored.py       # NEW
│   │   ├── test_input_box.py     # NEW - CRITICAL
│   │   ├── test_text_box.py      # NEW - CRITICAL
│   │   ├── test_window.py        # NEW - CRITICAL
│   │   └── test_app.py           # NEW - CRITICAL
│   ├── integration/
│   │   ├── test_app_workflow.py  # NEW - CRITICAL
│   │   ├── test_mode_transitions.py
│   │   ├── test_input_output_workspace.py
│   │   └── test_command_execution.py
│   ├── fixtures/
│   │   ├── mock_window.py        # NEW
│   │   └── sample_text.py
│   └── performance/
│       └── test_rendering.py
```

---

## Priority Test Implementation

### Week 1: Critical Components (15-20 hours)

**Day 1-2: App & TextSegment**
- [ ] Create `test_app.py` with 20+ tests
- [ ] Create `test_text_segment.py` with 15+ tests
- [ ] Achieve 70%+ coverage for both

**Day 3-4: Input/Output**
- [ ] Create `test_input_box.py` with 25+ tests
- [ ] Create `test_text_box.py` with 20+ tests
- [ ] Test history management thoroughly

**Day 5: Window & Integration**
- [ ] Create `test_window.py` with 15+ tests
- [ ] Create first integration test
- [ ] Set up test fixtures

### Week 2: Coverage & Edge Cases (15-20 hours)

**Day 1-2: Workspace & Manager**
- [ ] Create `test_input_output_workspace.py` with 30+ tests
- [ ] Create `test_input_manager.py` with 15+ tests
- [ ] Test async behavior

**Day 3-4: Edge Cases**
- [ ] Add Unicode tests
- [ ] Add boundary condition tests
- [ ] Add error recovery tests

**Day 5: Quality**
- [ ] Fix duplicate test names
- [ ] Add test docstrings
- [ ] Refactor with parametrize
- [ ] Generate coverage report

---

## Test Configuration Needed

### pytest.ini or pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["textbox"]
python_files = ["*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=textbox",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

### Coverage Configuration

```toml
[tool.coverage.run]
source = ["textbox"]
omit = [
    "*/tests/*",
    "*_test.py",
    "*/scratch.py",
    "textbox.bck/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
precision = 2
```

---

## Success Metrics

### Target Coverage

| Component | Target | Current | Gap |
|-----------|--------|---------|-----|
| Core Text | 85% | 75% | 10% |
| UI Layer | 80% | 0% | 80% |
| App Layer | 85% | 0% | 85% |
| Utils | 70% | 0% | 70% |
| **Overall** | **80%** | **25%** | **55%** |

### Test Count Goals

- Unit tests: 200+ (current: 57)
- Integration tests: 30+ (current: 0)
- Edge case tests: 50+ (current: ~10)

**Total Goal: 280+ tests**

---

## Estimated Effort

| Task | Time | Priority |
|------|------|----------|
| Create test infrastructure | 4h | Critical |
| Add App tests | 8h | Critical |
| Add TextSegment tests | 4h | Critical |
| Add InputBox tests | 8h | High |
| Add TextBox tests | 6h | High |
| Add Window tests | 6h | High |
| Add integration tests | 12h | High |
| Add edge case tests | 8h | Medium |
| Fix test quality issues | 4h | Medium |

**Total: ~60 hours (~2 weeks)**

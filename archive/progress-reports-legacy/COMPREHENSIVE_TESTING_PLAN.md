# Comprehensive Testing Plan

## Current State

**Overall Coverage**: 53.03%
**Tests Passing**: 77/77 (100%)
**Test Files**: 10

### Coverage Breakdown by Component

| Component | Coverage | Priority | Target |
|-----------|----------|----------|--------|
| **UI Components** | | | |
| workspace.py | 14.40% | CRITICAL | 70% |
| window.py | 21.79% | HIGH | 70% |
| input_manager.py | 24.49% | HIGH | 70% |
| input_box.py | 27.86% | HIGH | 70% |
| text_box.py | 30.83% | HIGH | 70% |
| **Application** | | | |
| App (__init__.py) | 33.06% | CRITICAL | 80% |
| **Core Classes** | | | |
| text.py | 78.07% | GOOD | 85% |
| text_line.py | 88.79% | EXCELLENT | 90% |
| segmented_text_line.py | 89.02% | EXCELLENT | 90% |
| text_list.py | 90.85% | EXCELLENT | 92% |
| text_segment.py | 76.19% | GOOD | 85% |
| **Utilities** | | | |
| box_types.py | 94.59% | EXCELLENT | 95% |
| curses_utils.py | 90.74% | EXCELLENT | 92% |
| color_code.py | 100.00% | PERFECT | 100% |
| signals.py | 100.00% | PERFECT | 100% |
| colors.py | 0.00% | LOW | 90% |
| key_state_machine.py | 0.00% | LOW | 80% |

**Target Overall Coverage**: 70%+

---

## Testing Strategy

### Phase 1: App Integration Tests (CRITICAL)
**Current**: 33% | **Target**: 80% | **Priority**: HIGHEST

#### Missing Coverage in App
- Lines 31-36: `start()` method
- Lines 39-44: `astart()` method
- Lines 47-61: `run()` method and workspace setup
- Lines 68-72: `_command_callback()` method
- Lines 79-99: `print()` method with different input types
- Lines 102-109: `command()` decorator
- Lines 112-114: `_default_help()` method
- Line 117: `stop()` method

#### Tests to Write

1. **test_app_lifecycle.py** - App startup and shutdown
   ```python
   test_app_instantiation()
   test_app_start_creates_workspace()
   test_app_stop_raises_window_quit()
   test_app_multiple_instantiation()
   ```

2. **test_app_commands.py** - Command system
   ```python
   test_command_decorator_registration()
   test_command_with_multiple_aliases()
   test_command_execution()
   test_command_with_help()
   test_default_help_command()
   test_unknown_command()
   test_command_callback_invocation()
   ```

3. **test_app_print.py** - Print method variations
   ```python
   test_print_string()
   test_print_text_object()
   test_print_segmented_text_list()
   test_print_text_line_list()
   test_print_with_newline()
   test_print_without_newline()
   test_print_before_workspace_created()  # error case
   ```

4. **test_app_callbacks.py** - Callback system
   ```python
   test_on_submit_callback()
   test_multiple_submit_callbacks()
   test_submit_callback_receives_text()
   test_command_callback()
   ```

---

### Phase 2: Workspace Tests (CRITICAL)
**Current**: 14% | **Target**: 70% | **Priority**: HIGHEST

#### Missing Coverage in Workspace
- Lines 34-61: Initialization and box setup
- Lines 100-107: `resize()` method
- Lines 110-128: Mode switching methods
- Lines 131-197: Input handling and key processing
- Lines 200-275: Mode-specific handlers
- Lines 278-375: Command entry and execution

#### Tests to Write

1. **test_workspace_init.py** - Initialization
   ```python
   test_workspace_creation()
   test_workspace_boxes_created()
   test_workspace_initial_mode()
   test_workspace_callbacks()
   ```

2. **test_workspace_modes.py** - Mode switching
   ```python
   test_enter_insert_mode()
   test_enter_replace_mode()
   test_enter_command_mode()
   test_enter_read_only_mode()
   test_mode_transitions()
   ```

3. **test_workspace_input.py** - Input handling
   ```python
   test_handle_keypress_insert_mode()
   test_handle_keypress_command_mode()
   test_handle_keypress_read_only_mode()
   test_special_keys()
   test_navigation_keys()
   ```

4. **test_workspace_commands.py** - Command execution
   ```python
   test_command_entry()
   test_command_execution()
   test_command_with_args()
   test_invalid_command()
   ```

5. **test_workspace_resize.py** - Window resizing
   ```python
   test_resize_updates_boxes()
   test_resize_preserves_content()
   test_resize_redraws()
   ```

---

### Phase 3: UI Component Tests (HIGH)
**Current**: 21-31% | **Target**: 70% | **Priority**: HIGH

#### 3a. Window Tests (window.py)
```python
test_window_initialization()
test_window_properties()
test_window_create_subwindow()
test_window_refresh()
test_window_erase()
test_window_addch()
test_window_addstr()
test_window_cursor_position()
test_window_bounding_box()
```

#### 3b. TextBox Tests (text_box.py)
```python
test_textbox_initialization()
test_textbox_add_str()
test_textbox_add_text()
test_textbox_add_segmented_line()
test_textbox_end_current_text()
test_textbox_resize()
test_textbox_refresh()
test_textbox_scrolling()
test_textbox_line_wrapping()
```

#### 3c. InputBox Tests (input_box.py)
```python
test_inputbox_initialization()
test_inputbox_set_text()
test_inputbox_resize()
test_inputbox_edit_mode()
test_inputbox_cursor_display()
test_inputbox_refresh()
test_inputbox_text_property()
```

#### 3d. InputManager Tests (input_manager.py)
```python
test_input_manager_creation()
test_input_manager_async_context()
test_input_manager_input_loop()
test_input_manager_stop()
test_input_manager_keypress_callback()
```

---

### Phase 4: Helper Utility Tests (MEDIUM)
**Current**: 0% | **Target**: 90% | **Priority**: MEDIUM

#### 4a. Colors Helper Tests (colors.py)
```python
test_dark_blue()
test_light_blue()
test_dark_purple()
test_light_purple()
test_color_returns_text_segment()
test_color_with_correct_color_code()
test_color_type_validation()
```

#### 4b. KeyStateMachine Tests (key_state_machine.py)
```python
test_state_machine_init()
test_state_machine_repr()
test_state_machine_state_tracking()
```

---

### Phase 5: Enhanced Core Tests (OPTIONAL)
**Current**: 76-91% | **Target**: 85-92% | **Priority**: LOW

Minor coverage improvements for already well-tested components:
- Add edge cases for text.py
- Add corner cases for text_segment.py
- Increase text_list.py to 92%

---

## Implementation Plan

### Week 1: Critical Components
**Days 1-2**: App Integration Tests
- Write test_app_lifecycle.py
- Write test_app_commands.py
- Write test_app_print.py
- Write test_app_callbacks.py
- **Goal**: App coverage 33% → 80%

**Days 3-5**: Workspace Tests
- Write test_workspace_init.py
- Write test_workspace_modes.py
- Write test_workspace_input.py
- Write test_workspace_commands.py
- Write test_workspace_resize.py
- **Goal**: Workspace coverage 14% → 70%

### Week 2: UI Components
**Days 1-2**: Window and Manager Tests
- Write test_window.py (comprehensive)
- Write test_input_manager.py
- **Goal**: window.py 22% → 70%, input_manager.py 24% → 70%

**Days 3-4**: Box Components
- Write test_textbox.py (enhanced)
- Write test_inputbox.py (enhanced)
- **Goal**: text_box.py 31% → 70%, input_box.py 28% → 70%

**Day 5**: Helper Utilities
- Write test_colors.py
- Write test_key_state_machine.py
- **Goal**: colors.py 0% → 90%, key_state_machine.py 0% → 80%

### Validation
- Run full test suite
- Generate coverage report
- Verify 70%+ overall coverage
- Document any remaining gaps

---

## Testing Approach

### Mocking Strategy

For UI tests that interact with curses:
```python
from unittest.mock import Mock, MagicMock, patch

@patch('textbox.utils.curses_utils.curses')
def test_window_operation(mock_curses):
    mock_stdscr = MagicMock()
    mock_curses.initscr.return_value = mock_stdscr
    # Test code
```

### Async Testing

For async components:
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_operation():
    # Async test code
    await some_async_function()
```

### Integration Testing

For end-to-end workflows:
```python
def test_full_workflow():
    app = App()

    @app.on_submit
    def handler(text):
        # Callback logic
        pass

    @app.command('test')
    def test_cmd(cmd):
        # Command logic
        pass

    # Verify registrations
    assert 'test' in app._user_defined_commands
```

---

## Success Criteria

✅ **Coverage**: 70%+ overall (currently 53%)
✅ **All Tests Pass**: 100% pass rate maintained
✅ **Critical Components**: 70%+ each (App, workspace, UI)
✅ **Documentation**: All new tests documented
✅ **Performance**: Test suite runs in < 2 seconds
✅ **Maintainability**: Clear, readable test code

---

## Test Organization

```
tests/
├── unit/                    # Unit tests (current tests)
│   ├── core/
│   │   ├── text_test.py
│   │   ├── text_line_test.py
│   │   └── ...
│   └── utils/
│       ├── box_types_test.py
│       └── ...
├── integration/            # New integration tests
│   ├── test_app_lifecycle.py
│   ├── test_app_commands.py
│   ├── test_app_print.py
│   └── test_app_callbacks.py
├── ui/                     # New UI component tests
│   ├── test_workspace.py
│   ├── test_window.py
│   ├── test_textbox.py
│   ├── test_inputbox.py
│   └── test_input_manager.py
└── helpers/                # New helper tests
    ├── test_colors.py
    └── test_key_state_machine.py
```

---

**Created**: 2025-10-31
**Target Completion**: 2 weeks
**Priority**: HIGH - Foundation for production readiness

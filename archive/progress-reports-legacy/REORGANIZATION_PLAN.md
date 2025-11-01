# Code Reorganization Plan - Stage 2.5

## Current Problems

1. **Dead/Scratch Code**: Files that serve no purpose
   - `hotkeys.py` - Empty file (1 line)
   - `scratch.py` - Test/scratch file (49 lines)
   - `colored_string.py` - Unused ColoredString class (5 lines)
   - `colored.py` - Redundant helper functions (26 lines)

2. **Flat Structure**: All 19 files in one directory
   - No logical grouping
   - Hard to understand relationships
   - Difficult to navigate

3. **Inconsistent Naming**:
   - `text_list.py` vs `text_line.py` - unclear distinction
   - `input_output_workspace.py` - overly long name

4. **Missing Organization**: No clear separation between:
   - Core data structures
   - UI components
   - Utilities
   - Public API

## Proposed Structure

```
textbox/
├── __init__.py              # Public API (App, main exports)
│
├── core/                    # Core text data structures
│   ├── __init__.py
│   ├── text.py             # Text class (397 lines)
│   ├── text_line.py        # TextLine class (237 lines)
│   ├── text_segment.py     # TextSegment class (51 lines)
│   ├── segmented_text_line.py  # SegmentedTextLine (147 lines)
│   └── text_list.py        # TextList class (161 lines)
│
├── ui/                      # UI components
│   ├── __init__.py
│   ├── window.py           # Window wrapper (182 lines)
│   ├── text_box.py         # TextBox component (287 lines)
│   ├── input_box.py        # InputBox component (198 lines)
│   ├── workspace.py        # Rename from input_output_workspace.py (375 lines)
│   └── input_manager.py    # AsyncInputManager (53 lines)
│
├── utils/                   # Utilities and helpers
│   ├── __init__.py
│   ├── box_types.py        # Position, BoundingBox, etc (136 lines)
│   ├── color_code.py       # ColorCode enum (23 lines)
│   ├── curses_utils.py     # Curses helpers (73 lines)
│   ├── signals.py          # WindowQuit, DelayedRedraw (6 lines)
│   └── key_state_machine.py  # Key state tracking (19 lines)
│
└── examples/                # Keep as is
    ├── main.py
    ├── llm_interface.py
    └── print_colors.py
```

## Files to Remove

### 1. `hotkeys.py` - REMOVE
- Empty file with 0 content
- No imports anywhere

### 2. `scratch.py` - REMOVE
- Test/scratch code
- Not used in production
- Should be in examples/ if needed

### 3. `colored_string.py` - REMOVE
- Unused ColoredString class
- No imports found in codebase
- Replaced by TextSegment

### 4. `colored.py` - EVALUATE
- Helper functions for creating colored TextSegments
- Could be useful for public API
- **Decision**: Keep but move to utils/ as `colors.py`

## Import Changes Required

After reorganization, imports will change from:
```python
from textbox.text import Text
from textbox.input_box import InputBox
```

To:
```python
from textbox.core.text import Text
from textbox.ui.input_box import InputBox
```

**However**, the public API in `textbox/__init__.py` will re-export everything:
```python
# textbox/__init__.py
from textbox.core.text import Text, TextLine, TextSegment
from textbox.ui.workspace import InputOutputWorkspace
from textbox.utils.color_code import ColorCode
# ... etc

__all__ = ['App', 'Text', 'TextLine', 'TextSegment', 'ColorCode', ...]
```

This means **users** can still do:
```python
from textbox import App, Text, ColorCode  # Public API unchanged
```

But **internal code** uses full paths:
```python
from textbox.core.text import Text  # Internal imports
```

## Migration Strategy

### Phase 1: Remove Dead Code
1. Delete `hotkeys.py`
2. Delete `scratch.py`
3. Delete `colored_string.py`
4. Run tests to confirm nothing breaks

### Phase 2: Create Subpackages
1. Create `textbox/core/__init__.py`
2. Create `textbox/ui/__init__.py`
3. Create `textbox/utils/__init__.py`

### Phase 3: Move Files (in dependency order)
1. **First**: Move leaf dependencies (no internal imports)
   - `text_segment.py` → `core/`
   - `color_code.py` → `utils/`
   - `signals.py` → `utils/`
   - `box_types.py` → `utils/`

2. **Second**: Move mid-level classes
   - `segmented_text_line.py` → `core/`
   - `text_line.py` → `core/`
   - `curses_utils.py` → `utils/`
   - `key_state_machine.py` → `utils/`

3. **Third**: Move high-level classes
   - `text_list.py` → `core/`
   - `text.py` → `core/`
   - `window.py` → `ui/`
   - `input_manager.py` → `ui/`

4. **Fourth**: Move UI components
   - `text_box.py` → `ui/`
   - `input_box.py` → `ui/`
   - `input_output_workspace.py` → `ui/workspace.py` (rename)

5. **Fifth**: Move utilities
   - `colored.py` → `utils/colors.py` (rename)

### Phase 4: Update Imports
For each moved file:
1. Update its internal imports to use new paths
2. Update `textbox/__init__.py` to import from new locations
3. Update test files in `tests/`
4. Update example files in `examples/`

### Phase 5: Verify
1. Run all tests: `python3 -m unittest discover tests "*_test.py"`
2. Run all examples to ensure they work
3. Verify public API unchanged: `python3 -c "from textbox import App, Text, ColorCode"`

## Benefits

1. **Clarity**: Immediately clear what each subpackage does
2. **Maintainability**: Related code grouped together
3. **Scalability**: Easy to add new components in right place
4. **Documentation**: Structure self-documents the architecture
5. **Navigation**: Easier to find what you're looking for
6. **Testing**: Can test subpackages independently

## Risks

1. **Import breakage**: Must update all imports carefully
2. **Test failures**: Tests may need import updates
3. **Example breakage**: Examples must be updated
4. **Circular imports**: Must watch for circular dependencies

## Testing Strategy

After each phase:
1. Run full test suite
2. Test one example file
3. Verify public API still works

If any phase fails:
1. Roll back that phase
2. Investigate issue
3. Fix and retry

## Timeline

- Phase 1 (Remove dead code): 15 minutes
- Phase 2 (Create subpackages): 5 minutes
- Phase 3 (Move files): 1 hour (careful, methodical)
- Phase 4 (Update imports): 1.5 hours (most time-consuming)
- Phase 5 (Verify): 30 minutes
- **Total**: ~3 hours

## Alternative: Keep Flat Structure

If this seems too risky, we could instead:
1. Just remove dead code (Phase 1 only)
2. Keep flat structure
3. Focus on type hints and bug fixes

**Recommendation**: Proceed with full reorganization. The codebase is small enough (2545 lines) that this is manageable, and it will pay dividends for future maintenance.

# Textbox Development Roadmap

**Last Updated**: 2025-10-31
**Current Version**: 0.1.0
**Next Version**: 0.2.0 (after Phase 1-3)

---

## Vision

**Build the best vim-like text editor library for Python terminal applications.**

**Core Principles**:
- Vim completeness and accuracy
- Robust and reliable
- Extensible and documented
- Clean, maintainable code

---

## Completed Work ✅

### Stage 1: Foundation (Oct 2025)
- ✅ Removed unnecessary dependencies (uvloop, termcolor)
- ✅ Fixed 9 critical bugs with test coverage
- ✅ Reorganized into professional package structure
- ✅ Added 200+ type hints to all APIs
- ✅ Achieved 82.38% test coverage (329 tests)
- ✅ Cross-platform compatibility

**Result**: Production-ready foundation

---

## Current Priorities 🔥

### Phase 1: Code Quality & Robustness
**Status**: Not started
**Timeline**: 2-3 days
**Version**: Will be included in 0.2.0

#### Input Validation
- [ ] Add validation to `Text.goto()` with helpful errors
- [ ] Add validation to `Window.resize()`
- [ ] Add validation to `TextBox.add_text()`
- [ ] Add validation to all cursor operations
- [ ] Write tests for validation

#### Error Handling
- [ ] Strategic error logging in Window operations
- [ ] Context-aware error messages
- [ ] Log mode transitions and errors
- [ ] Debug logging for complex operations

#### Resource Management
- [ ] Implement Window.cleanup()
- [ ] Add Text.set_max_lines() for memory limits
- [ ] Proper resource cleanup on exit
- [ ] Test for memory leaks

**Outcome**: 10x better debugging, prevents crashes

---

### Phase 2: Vim Feature Completeness
**Status**: Not started
**Timeline**: 3-4 days
**Version**: 0.2.0 release blocker

#### 2.1 Visual Mode (CRITICAL)
- [ ] Add VISUAL and VISUAL_LINE to INPUT_MODE enum
- [ ] Implement visual selection tracking
- [ ] Add visual mode entry/exit methods
- [ ] Implement `v` keybinding (enter visual)
- [ ] Implement `V` keybinding (enter visual line)
- [ ] Implement `y` (yank selection)
- [ ] Implement `d` (delete selection)
- [ ] Implement `c` (change selection)
- [ ] Visual selection highlighting
- [ ] Write comprehensive tests

**Outcome**: Users can select and manipulate text visually

#### 2.2 Register System (HIGH PRIORITY)
- [ ] Create RegisterManager class
- [ ] Implement yank to register
- [ ] Implement put from register
- [ ] Default register (") support
- [ ] Named registers (a-z) support
- [ ] Implement `p` keybinding (paste after)
- [ ] Implement `P` keybinding (paste before)
- [ ] Implement `"<char>y` (yank to named)
- [ ] Implement `"<char>p` (put from named)
- [ ] Write register tests

**Outcome**: Complete copy/paste workflow

#### 2.3 Essential Vim Commands
- [ ] `dd` - Delete line
- [ ] `D` - Delete to end of line
- [ ] `x` - Delete character under cursor
- [ ] `X` - Delete character before cursor
- [ ] `cc` - Change line
- [ ] `C` - Change to end of line
- [ ] `cw` - Change word
- [ ] `o` - Open line below
- [ ] `O` - Open line above
- [ ] `J` - Join lines
- [ ] Write vim command tests

**Outcome**: Vim users feel at home

---

### Phase 3: Advanced Features
**Status**: Not started
**Timeline**: 4-5 days
**Version**: 0.2.0 or 0.3.0

#### 3.1 Undo/Redo System (CRITICAL)
- [ ] Create Command abstract base class
- [ ] Create CommandHistory manager
- [ ] Implement InsertTextCommand
- [ ] Implement DeleteTextCommand
- [ ] Implement ReplaceTextCommand
- [ ] Implement DeleteLineCommand
- [ ] Implement PasteCommand
- [ ] Integrate with Text operations
- [ ] Implement `u` keybinding (undo)
- [ ] Implement `Ctrl-r` keybinding (redo)
- [ ] Write undo/redo tests
- [ ] Test undo limits (1000 operations)

**Outcome**: Professional undo/redo capability

#### 3.2 Event System
- [ ] Create Event base class
- [ ] Create EventBus
- [ ] Define TextChangedEvent
- [ ] Define ModeChangedEvent
- [ ] Define CommandExecutedEvent
- [ ] Integrate events into Text operations
- [ ] Integrate events into mode changes
- [ ] Document event system usage
- [ ] Write event system tests

**Outcome**: Extensible architecture for plugins

---

## Future Phases (Backlog) 📋

### Phase 4: Documentation & DX
**Priority**: Medium
**Timeline**: 2-3 days

- [ ] Enhanced README with examples
- [ ] Complete API docstrings
- [ ] Usage guide (vim modes, commands)
- [ ] Architecture documentation
- [ ] Debug mode implementation
- [ ] Debug overlay display

### Phase 5: Testing Enhancements
**Priority**: Medium
**Timeline**: 2 days

- [ ] Integration tests for workflows
- [ ] Edge case testing (unicode, long lines)
- [ ] Property-based tests
- [ ] Vim compatibility tests

### Phase 6: Performance & Polish
**Priority**: Low-Medium
**Timeline**: 1-2 days

- [ ] Cache cursor position calculation
- [ ] Lazy line wrapping
- [ ] Reduce unnecessary copies
- [ ] Add py.typed marker
- [ ] Performance benchmarks

---

## Advanced Features (Future Consideration)

These are deferred until core features are complete:

### Search & Replace
- `/` - Search forward
- `?` - Search backward
- `n`/`N` - Next/previous match
- `:s/pattern/replacement/` - Substitute

### Advanced Vim Features
- Macros (recording with `q`)
- Marks (`` ` `` and `'`)
- Text objects (`ciw`, `ca(`, etc.)
- Counts (e.g., `3dd`, `5j`)

### Syntax Highlighting
- Implement as plugin using event system
- Language-specific highlighters
- Theme support

### Multi-Buffer Support
- Multiple text buffers
- Buffer switching (`:bnext`, `:bprev`)
- Split windows

**Note**: These are intentionally deferred. Focus is on getting core vim features solid first.

---

## Version Planning

### v0.2.0 - "Vim Complete" (Target: Dec 2025)
**Focus**: Visual mode, registers, undo/redo

**Must Have**:
- ✅ Input validation and error handling
- ✅ Visual mode (character and line)
- ✅ Register system (copy/paste)
- ✅ Undo/redo system
- ✅ Essential vim commands (dd, o, J, etc.)

**Should Have**:
- ✅ Event system
- ✅ Documentation improvements

**Nice to Have**:
- Integration tests
- Debug mode
- Performance optimizations

### v0.3.0 - "Power User" (Target: Q1 2026)
**Focus**: Advanced vim features

- Search and replace
- Macros
- Marks
- Text objects
- Counts

### v1.0.0 - "Production Excellence" (Target: Q2 2026)
**Focus**: Polish and stability

- 90%+ test coverage
- Comprehensive documentation
- Performance optimized
- Proven stability
- Community adoption

---

## Success Metrics

### v0.2.0 Targets
- **Test Coverage**: >80% (maintain current level)
- **Tests**: 450+ tests (from 329)
- **Vim Commands**: 20+ implemented
- **Type Hints**: 100% public API
- **Documentation**: All public methods documented

### User Experience Goals
- **"Feels like vim"** - Users immediately comfortable
- **"Doesn't crash"** - Robust error handling
- **"Easy to debug"** - Clear error messages
- **"Extensible"** - Event system enables plugins

### Technical Goals
- **Zero critical bugs**
- **<50ms render time** for 1000 lines
- **<1GB memory** for large texts
- **Cross-platform** (Mac, Linux, Windows)

---

## Contributing

### Current Focus
We're currently working on **Phase 1 (Code Quality)** and **Phase 2 (Vim Features)**.

The best ways to contribute:
1. **Test vim compatibility** - Try vim commands, report what's missing
2. **Write integration tests** - Real-world editing workflows
3. **Documentation** - Examples, tutorials, guides
4. **Bug reports** - Especially vim behavior differences

### Not Accepting (Yet)
- CI/CD setup (low priority)
- Major architectural changes (foundation is solid)
- Framework replacements (staying with curses)
- Features outside vim scope (staying focused)

---

## Design Decisions

### What We're Optimizing For
1. **Vim accuracy** - Match vim behavior closely
2. **Simplicity** - Clean, understandable code
3. **Extensibility** - Via event system and clear APIs
4. **Performance** - Fast enough for comfortable editing

### What We're NOT Optimizing For
- Being a general-purpose TUI framework
- Supporting every terminal feature
- Maximum theoretical performance
- Feature parity with Neovim

### Technology Choices
- **Curses**: Direct terminal control, proven technology
- **Asyncio**: Modern Python async patterns
- **Type hints**: Better DX and error catching
- **No fancy frameworks**: Keep it simple and focused

---

## Questions?

- **Full improvement plan**: See `docs/IMPROVEMENT_PLAN.md`
- **Executive summary**: See `docs/IMPROVEMENT_SUMMARY.md`
- **Progress reports**: See `docs/progress-reports/`
- **Original review**: See `claude-output/review/`

---

**Last Updated**: 2025-10-31
**Maintainer**: Jason Cronquist
**Status**: Active development - Phase 1 starting soon

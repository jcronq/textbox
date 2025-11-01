# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-11-01

### Added

#### Vim Features
- Complete vim modal editing system with 7 modes (COMMAND, INSERT, REPLACE, VISUAL, VISUAL LINE, COMMAND ENTRY, SEARCH ENTRY)
- Visual mode for character-wise and line-wise selection
- Register system with named (`"a-z`), unnamed (`"`), and numbered (`"0-9`) registers
- Full undo/redo system using Command pattern with 1000-operation history
- Search functionality with forward (`/`) and backward (`?`) search
- Search navigation with `n` (next) and `N` (previous)
- 40+ vim keybindings including:
  - Motion: `h j k l w b $ 0`
  - Edit: `i I a A o O R`
  - Delete: `x dd D`
  - Change: `cc C`
  - Yank/Paste: `yy p P`
  - Visual: `v V`
  - Other: `J u Ctrl-r : / ?`

#### Event System
- Pub/sub event system with `EventBus` class
- `TextChangedEvent` published on insert, delete, and replace operations
- `ModeChangedEvent` published on all mode transitions
- `CommandExecutedEvent` published when commands execute
- Event propagation through component hierarchy (Workspace → TextBox → TextList → Text)
- Support for multiple subscribers per event type
- Graceful error handling (exceptions in handlers don't stop other handlers)

#### Debug Mode
- `DebugOverlay` class for displaying real-time internal state
- `DebugStats` for tracking metrics (keypress count, mode changes, etc.)
- Enhanced logging with `setup_debug_logging()` function
- `PerformanceTimer` for measuring operation durations
- Structured event logging with `log_event()`
- Helper utilities: `format_bytes()`, `get_text_stats()`
- Opt-in debug mode: `App(debug=True)`

#### Documentation
- Complete vim mode reference guide (`docs/vim-mode.md`, ~450 lines)
- Event system guide with examples (`docs/event-system.md`, ~450 lines)
- Updated README with feature highlights and quick start
- Reorganized docs with clear navigation structure
- All new features documented with working code examples

#### Testing
- 227 new tests added (329 → 556 tests)
- Integration tests for complete workflows (visual + yank + paste + undo)
- Edge case tests (empty text, unicode, rapid operations)
- Event system test suite (13 unit tests + 9 integration tests)
- Mode transition workflow tests
- 100% pass rate maintained

#### Type Safety
- Added `py.typed` marker for PEP 561 compliance
- External projects now get type checking support
- Complete type hints throughout codebase

### Changed

- Upgraded project status to production-ready
- Improved error messages with helpful context
- Enhanced resource cleanup for long-running applications
- Better memory management with optional max line limits
- Command pattern for all text operations (makes everything undoable)
- Updated README with modern presentation and badges

### Fixed

- Memory leaks in long-running applications
- Cursor positioning edge cases in visual mode
- Event propagation through all Text objects
- Search wrapping at document boundaries
- Backward search overlap detection
- Register operations with proper state capture

### Performance

- Efficient undo/redo with O(1) undo and redo operations
- Event system with minimal overhead (publish is O(n) in subscribers)
- Lazy text object creation in TextList

## [0.1.0] - 2025-10-01

### Added

- Initial release
- Basic terminal UI with curses
- Async/await support with asyncio
- Colored text support with ColorCode enum
- Command system with decorator-based registration
- Input/output workspace with split-screen interface
- Text abstraction layers (TextSegment → TextLine → Text → TextList)
- Basic vim-like navigation (hjkl, arrow keys)
- Submit callbacks with `@app.on_submit`
- Custom commands with `@app.command()`
- 329 comprehensive tests
- 82.38% test coverage

### Project Setup

- Professional package structure (core/ui/utils)
- Type hints for all public APIs
- pytest test suite with coverage
- Black code formatting (119 char line length)
- pyproject.toml configuration
- Minimal dependencies (only PyYAML)

[Unreleased]: https://github.com/jasoncronquist/textbox/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/jasoncronquist/textbox/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/jasoncronquist/textbox/releases/tag/v0.1.0

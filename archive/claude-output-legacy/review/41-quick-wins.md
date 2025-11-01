# Quick Wins - Immediate Improvements

These improvements can be completed in **less than 1 day** and provide immediate value.

---

## Hour 1: Fix Critical Bugs (2-3 hours)

### Bug Fixes (90 minutes)

See [01-critical-bugs.md](01-critical-bugs.md) for detailed fixes.

**Checklist:**
- [ ] Fix `text.py:191` - IndexError in next_line (5 min)
- [ ] Fix `text_line.py:153` - Missing return statement (5 min)
- [ ] Fix `input_box.py:100` - Property getter side effect (5 min)
- [ ] Fix `text_box.py:188` - Wrong type assignment (10 min)
- [ ] Fix `input_output_workspace.py:222` - Strip not assigned (2 min)
- [ ] Fix `window.py:144-157` - Validate before state update (15 min)
- [ ] Fix `curses_utils.py:71` - Assignment vs comparison (2 min)
- [ ] Fix `color_code.py` - Make proper Enum + fix typo (20 min)
- [ ] Fix `__init__.py:78` - Type hint mismatch (10 min)

**Commands:**
```bash
# Test each fix
python -m pytest textbox/text_test.py::test_next_line -v
python -m pytest textbox/text_line_test.py -v
# ... etc
```

---

## Hour 2: Basic Infrastructure (1 hour)

### Create pytest.ini (5 minutes)

Create `pytest.ini` at project root:
```ini
[pytest]
testpaths = textbox
python_files = *_test.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

**Or add to `pyproject.toml`:**
```toml
[tool.pytest.ini_options]
testpaths = ["textbox"]
python_files = ["*_test.py"]
addopts = ["-v", "--tb=short"]
```

### Enhance README.md (30 minutes)

Replace current README with:
```markdown
# textbox

A Python library for building terminal user interfaces with vim-like keybindings and rich text formatting.

## Features

- 🎨 Rich text formatting with color support
- ⌨️ Vim-like keybindings (INSERT, COMMAND, REPLACE modes)
- ⚡ Async input handling with uvloop
- 🪟 Resizable terminal windows
- 🎯 Decorator-based command system

## Installation

```bash
pip install textbox
```

## Quick Start

```python
from textbox import App

app = App()

@app.on_submit
def handle_input(text):
    app.print(f"You said: {text}")

@app.command("quit", "q", help="Exit application")
def quit_cmd(cmd):
    app.stop()

app.start()
```

## Examples

See `examples/` directory:
- `llm_interface.py` - Chat interface with commands
- `print_colors.py` - Color demonstration
- `main.py` - Basic setup

## Development

```bash
# Install with dev dependencies
pip install -e .

# Run tests
python -m pytest

# Format code
black --line-length 119 textbox/
```

## Requirements

- Python 3.9+
- termcolor
- pyyaml
- uvloop (Linux/macOS only)

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please open an issue first to discuss changes.
```

### Update .gitignore (10 minutes)

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Project specific
log.txt
textbox.log
scratch.py
*.bck

# OS
.DS_Store
Thumbs.db
```

### Create CHANGELOG.md (15 minutes)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- IndexError in `text.py` next_line property
- Logic error in `text_line.py` replace_character method
- Property getter side effect in `input_box.py`
- Type error in `text_box.py` erase method
- Strip result not assigned in `input_output_workspace.py`
- State corruption in `window.py` resize method
- Assignment vs comparison in `curses_utils.py`
- ColorCode not using Enum, fixed OUPTUT_TEXT typo
- Type hint mismatch in App.on_submit

### Added
- pytest configuration
- Enhanced README
- CHANGELOG.md
- Improved .gitignore

## [0.1.0] - 2024-04-04

### Added
- Initial release
- Vim-like terminal interface
- Rich text formatting with colors
- Async input handling
- Command system with decorators
- Text abstraction layers

[Unreleased]: https://github.com/jcronq/textbox/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jcronq/textbox/releases/tag/v0.1.0
```

---

## Hour 3: Remove Dead Code (30 minutes)

### Clean Up Repository

```bash
# Remove backup directory
git rm -r textbox.bck/

# Remove scratch files
git rm textbox/scratch.py

# Remove old pytest cache
rm -rf .pytest_cache/

# Remove log files from git
git rm --cached log.txt textbox.log

# Commit cleanup
git commit -m "Clean up dead code and ignored files"
```

### Update .gitignore
Already covered above - add `*.log`, `scratch.py`, etc.

---

## Hour 4: Basic GitHub Actions (1 hour)

### Create Basic CI Workflow (45 minutes)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12', '3.13']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest

    - name: Run tests
      run: pytest -v
```

### Push and Verify (15 minutes)

```bash
git add .github/workflows/ci.yml
git commit -m "Add basic CI workflow"
git push

# Check Actions tab on GitHub to verify it runs
```

---

## Hour 5: pyproject.toml Enhancements (1 hour)

### Expand Current Configuration

Current `pyproject.toml` only has:
```toml
[tool.black]
line-length=119
```

Replace with comprehensive version:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "textbox"
version = "0.1.0"
description = "Terminal UI library with vim-like keybindings and rich text"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [{name = "Jason Cronquist"}]
keywords = ["terminal", "curses", "tui", "vim", "cli"]

dependencies = [
    "termcolor>=2.0.0",
    "pyyaml>=6.0",
    "uvloop>=0.17.0; platform_system != 'Windows'",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
]

[project.urls]
Homepage = "https://github.com/jcronq/textbox"
Repository = "https://github.com/jcronq/textbox"
Issues = "https://github.com/jcronq/textbox/issues"

[tool.setuptools]
packages = ["textbox"]

[tool.black]
line-length = 119
target-version = ['py39']

[tool.pytest.ini_options]
testpaths = ["textbox"]
python_files = ["*_test.py"]
addopts = ["-v", "--tb=short"]
```

---

## Total Time Breakdown

| Task | Time | Immediate Value |
|------|------|-----------------|
| Fix 9 critical bugs | 90 min | Prevents crashes/corruption |
| Create pytest config | 5 min | Enables proper testing |
| Enhance README | 30 min | Makes project usable |
| Update .gitignore | 10 min | Cleaner repository |
| Create CHANGELOG | 15 min | Track changes properly |
| Remove dead code | 30 min | Cleaner codebase |
| Setup GitHub Actions | 45 min | Automated testing |
| Enhance pyproject.toml | 60 min | Modern packaging |

**Total: ~5 hours**

---

## Immediate Impact

### After These Quick Wins:

✅ **No more critical bugs** - Library won't crash or corrupt data
✅ **Professional appearance** - Good README, proper packaging
✅ **Automated testing** - CI runs on every push
✅ **Cleaner repository** - No dead code or clutter
✅ **Better documentation** - CHANGELOG tracks changes
✅ **Proper configuration** - Modern pyproject.toml

### What You Still Need:

⚠️ More comprehensive tests
⚠️ Type checking setup
⚠️ Code coverage tracking
⚠️ Linting automation
⚠️ Complete documentation

But with these quick wins, you have a **solid foundation** to build on.

---

## Recommended Order

### Morning (3 hours)
1. Fix all critical bugs
2. Create pytest configuration
3. Enhance README.md
4. Update .gitignore
5. Create CHANGELOG.md

**Commit:** "Fix critical bugs and improve documentation"

### Afternoon (2 hours)
1. Remove dead code
2. Setup GitHub Actions
3. Enhance pyproject.toml

**Commit:** "Add CI and modernize packaging"

### Evening
Celebrate! 🎉

Your project now:
- ✅ Has no critical bugs
- ✅ Looks professional
- ✅ Has automated testing
- ✅ Uses modern Python packaging

---

## Verification Checklist

After completing quick wins:

- [ ] All 9 critical bugs fixed
- [ ] All existing tests pass
- [ ] README is comprehensive
- [ ] .gitignore covers all generated files
- [ ] CHANGELOG.md exists and is updated
- [ ] Dead code removed from repository
- [ ] GitHub Actions workflow exists
- [ ] CI runs successfully on push
- [ ] pyproject.toml has full metadata
- [ ] Can install with `pip install -e .`
- [ ] Can run tests with `pytest`

---

## Next Steps After Quick Wins

See [40-implementation-roadmap.md](40-implementation-roadmap.md) for the complete improvement plan.

**Immediate priorities after quick wins:**
1. Add comprehensive test coverage
2. Set up type checking with mypy
3. Add code coverage tracking
4. Set up pre-commit hooks
5. Write API documentation

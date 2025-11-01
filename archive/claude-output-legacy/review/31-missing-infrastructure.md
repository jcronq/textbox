# Missing Infrastructure

This document catalogs all missing development infrastructure, tooling, and automation.

---

## CI/CD Pipeline ❌ CRITICAL

### Current State
**No CI/CD exists whatsoever**

- No GitHub Actions workflows
- No automated testing
- No automated linting
- No automated type checking
- No coverage reporting
- No automated releases

### Impact
- Changes merged without validation
- Bugs reach main branch
- No quality gates
- Manual testing burden
- No deployment automation

### Required Files

#### `.github/workflows/ci.yml`
```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12', '3.13']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]

    - name: Lint with ruff
      run: ruff check textbox/

    - name: Format check
      run: black --check --line-length 119 textbox/

    - name: Type check
      run: mypy textbox/

    - name: Test
      run: pytest --cov=textbox --cov-report=xml --cov-report=term

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      if: matrix.python-version == '3.11' && matrix.os == 'ubuntu-latest'
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

#### `.github/workflows/publish.yml`
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Check package
      run: twine check dist/*

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

#### `.github/workflows/security.yml`
```yaml
name: Security Scan

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install safety bandit

    - name: Run safety check
      run: safety check --json

    - name: Run bandit
      run: bandit -r textbox/ -f json
```

---

## Testing Configuration ❌ CRITICAL

### Current State
- Tests exist but no pytest configuration
- No coverage tracking
- No test discovery rules
- No test markers

### Required: pytest Configuration

Add to `pyproject.toml`:
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
    "--cov-fail-under=60",  # Start at 60%, increase to 80%
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "asyncio: marks tests as async",
]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["textbox"]
omit = [
    "*/tests/*",
    "*_test.py",
    "*/scratch.py",
    "textbox.bck/*",
]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
precision = 2
show_missing = true
```

---

## Code Quality Tools ❌ HIGH PRIORITY

### Current State
- No linting configuration
- No formatter configuration (only basic Black in pyproject.toml)
- No type checking
- Inconsistent code style

### Required: Ruff Configuration

Add to `pyproject.toml`:
```toml
[tool.ruff]
line-length = 119
target-version = "py39"

select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "N",   # pep8-naming
    "YTT", # flake8-2020
    "S",   # flake8-bandit
    "A",   # flake8-builtins
    "COM", # flake8-commas
    "T10", # flake8-debugger
    "ISC", # flake8-implicit-str-concat
    "ICN", # flake8-import-conventions
    "PIE", # flake8-pie
    "Q",   # flake8-quotes
    "RSE", # flake8-raise
    "RET", # flake8-return
    "SIM", # flake8-simplify
    "PTH", # flake8-use-pathlib
]

ignore = [
    "E501",  # line too long (handled by black)
    "S101",  # assert used (ok in tests)
    "COM812", # trailing comma (conflicts with formatter)
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # Unused imports ok in __init__
"*_test.py" = ["S101"]    # asserts ok in tests

[tool.ruff.isort]
known-first-party = ["textbox"]
```

### Required: MyPy Configuration

Add to `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true
disallow_untyped_defs = false  # Enable gradually
check_untyped_defs = true
no_implicit_optional = true
strict_equality = true
warn_unreachable = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "termcolor.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "yaml.*"
ignore_missing_imports = true
```

---

## Pre-commit Hooks ❌ HIGH PRIORITY

### Current State
No pre-commit hooks configured

### Required: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: check-toml
      - id: debug-statements
      - id: mixed-line-ending

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        args: [--line-length=119]
        language_version: python3.11

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies:
          - types-termcolor
          - types-PyYAML
        args: [--ignore-missing-imports]
```

**Setup:**
```bash
pip install pre-commit
pre-commit install
```

---

## Tox Configuration ❌ MEDIUM PRIORITY

### Current State
No multi-version testing

### Required: `tox.ini`

```ini
[tox]
envlist = py39,py310,py311,py312,py313,lint,type,coverage
isolated_build = True
skip_missing_interpreters = True

[testenv]
deps =
    pytest>=7.4.0
    pytest-cov>=4.1.0
    pytest-asyncio>=0.21.0
commands =
    pytest {posargs}

[testenv:lint]
deps =
    ruff>=0.1.0
    black>=23.0.0
commands =
    ruff check textbox/
    black --check --line-length 119 textbox/
skip_install = True

[testenv:type]
deps =
    mypy>=1.5.0
    types-termcolor
    types-PyYAML
commands =
    mypy textbox/

[testenv:coverage]
deps =
    pytest>=7.4.0
    pytest-cov>=4.1.0
commands =
    pytest --cov=textbox --cov-report=html --cov-report=term --cov-fail-under=80

[testenv:format]
deps = black>=23.0.0
commands = black --line-length 119 textbox/
skip_install = True

[testenv:docs]
deps =
    sphinx>=7.0.0
    sphinx-rtd-theme>=1.3.0
commands =
    sphinx-build -W -b html docs/source docs/build/html
```

---

## Dependency Management ❌ MEDIUM PRIORITY

### Current State
- Basic requirements.txt
- No version locking
- No security scanning

### Required: Dependabot Configuration

Create `.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "jcronq"
    labels:
      - "dependencies"
    commit-message:
      prefix: "deps"
```

### Required: requirements-dev.txt

```txt
# Development dependencies
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
pytest-mock>=3.11.0

# Code quality
black>=23.0.0
ruff>=0.1.0
mypy>=1.5.0
pre-commit>=3.5.0

# Type stubs
types-termcolor>=1.1.0
types-PyYAML>=6.0.0

# Docs
sphinx>=7.0.0
sphinx-rtd-theme>=1.3.0

# Tools
tox>=4.11.0
build>=1.0.0
twine>=4.0.0
```

---

## Package Configuration ❌ CRITICAL

### Current State
- Using old setup.py
- No PEP 621 compliance
- Incomplete metadata

### Required: Complete pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "textbox"
version = "0.1.0"
description = "Terminal UI library with vim-like keybindings and rich text"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Jason Cronquist", email = "jcronq@users.noreply.github.com"}
]
keywords = ["terminal", "curses", "tui", "vim", "cli"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Libraries",
    "Topic :: Terminals",
]

dependencies = [
    "termcolor>=2.0.0",
    "pyyaml>=6.0",
    "uvloop>=0.17.0; platform_system != 'Windows'",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "types-termcolor",
    "types-PyYAML",
]

[project.urls]
Homepage = "https://github.com/jcronq/textbox"
Repository = "https://github.com/jcronq/textbox"
Issues = "https://github.com/jcronq/textbox/issues"
Changelog = "https://github.com/jcronq/textbox/blob/main/CHANGELOG.md"

[tool.setuptools]
packages = ["textbox"]

[tool.setuptools.package-data]
textbox = ["py.typed"]
```

### Required: MANIFEST.in

```
include README.md
include LICENSE
include CHANGELOG.md
include requirements.txt
include version.txt
recursive-include textbox *.py py.typed
recursive-exclude * __pycache__
recursive-exclude * *.pyc
```

### Required: textbox/py.typed

Create empty file to mark package as typed (PEP 561).

---

## Documentation Generation ❌ LOW PRIORITY

### Current State
No documentation generation setup

### Required: Sphinx Configuration

Create `docs/source/conf.py`:
```python
project = 'textbox'
copyright = '2024, Jason Cronquist'
author = 'Jason Cronquist'
version = '0.1.0'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_member_order = 'bsource'
autodoc_typehints = 'description'
```

---

## Issue Templates ❌ LOW PRIORITY

### Required: Bug Report Template

Create `.github/ISSUE_TEMPLATE/bug_report.md`:
```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. ...
2. ...

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
 - OS: [e.g. macOS 14.0]
 - Python version: [e.g. 3.11]
 - Textbox version: [e.g. 0.1.0]

**Additional context**
Any other information.
```

### Required: Feature Request Template

Create `.github/ISSUE_TEMPLATE/feature_request.md`:
```markdown
---
name: Feature request
about: Suggest an idea
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem?**
Description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Alternative solutions.

**Additional context**
Any other information.
```

---

## Priority Implementation Order

### Week 1: Critical Infrastructure (20 hours)
1. ✅ Create complete pyproject.toml
2. ✅ Set up pytest configuration
3. ✅ Create GitHub Actions CI workflow
4. ✅ Add basic pre-commit hooks
5. ✅ Set up coverage tracking

### Week 2: Quality Tools (15 hours)
1. ✅ Configure ruff and black
2. ✅ Set up mypy
3. ✅ Create tox configuration
4. ✅ Add security scanning
5. ✅ Set up Dependabot

### Week 3: Publishing (10 hours)
1. ✅ Create publish workflow
2. ✅ Set up PyPI test publishing
3. ✅ Create issue templates
4. ✅ Add pull request template
5. ✅ Document release process

### Week 4: Documentation (Optional, 15 hours)
1. ✅ Set up Sphinx
2. ✅ Generate API docs
3. ✅ Host docs on Read the Docs
4. ✅ Add badges to README

---

## Estimated Total Effort

| Category | Time | Priority |
|----------|------|----------|
| CI/CD Setup | 8h | Critical |
| Testing Config | 4h | Critical |
| Package Config | 4h | Critical |
| Pre-commit Hooks | 2h | High |
| Code Quality Tools | 4h | High |
| Tox Setup | 2h | Medium |
| Dependabot | 1h | Medium |
| Issue Templates | 1h | Low |
| Sphinx Docs | 8h | Low |

**Total: 34 hours (~1 week)**

Most critical items (CI/CD, testing, packaging) can be done in **1-2 days**.

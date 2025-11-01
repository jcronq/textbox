# Textbox Deployment Plan

Comprehensive plan for CI/CD, GitHub Pages documentation, PyPI publishing, and production release.

**Status**: Ready for implementation
**Target**: v0.2.0 release
**Updated**: 2025-11-01

---

## Table of Contents

- [Overview](#overview)
- [Phase 1: GitHub Actions CI/CD](#phase-1-github-actions-cicd)
- [Phase 2: GitHub Pages Documentation](#phase-2-github-pages-documentation)
- [Phase 3: PyPI Publishing](#phase-3-pypi-publishing)
- [Phase 4: Release Process](#phase-4-release-process)
- [Phase 5: Monitoring & Badges](#phase-5-monitoring--badges)
- [Implementation Checklist](#implementation-checklist)
- [Post-Deployment](#post-deployment)

---

## Overview

### Current State
- ✅ 556 tests passing (100% pass rate)
- ✅ 82.38% code coverage
- ✅ Complete documentation (vim, events, API)
- ✅ Production-ready v0.2.0 codebase
- ✅ Type hints with py.typed marker
- ❌ No CI/CD pipeline
- ❌ No automated testing
- ❌ Not published to PyPI
- ❌ No GitHub Pages docs

### Goals
1. **Automated Testing**: CI runs on every push/PR
2. **Documentation Site**: GitHub Pages for docs
3. **PyPI Publishing**: Automated releases
4. **Quality Gates**: Enforce coverage and tests
5. **Release Automation**: One-command releases

---

## Phase 1: GitHub Actions CI/CD

### 1.1 Main CI Pipeline

**File**: `.github/workflows/ci.yml`

**Triggers**:
- Every push to `main` and `develop` branches
- All pull requests
- Manual workflow dispatch

**Jobs**:

#### Job 1: Test Matrix
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    python-version: ['3.10', '3.11', '3.12']
```

**Steps**:
1. Checkout code
2. Setup Python (matrix version)
3. Install dependencies (`pip install -e ".[dev]"`)
4. Run linting (`black --check`, `flake8`)
5. Run tests (`pytest tests/ -v --cov=textbox`)
6. Upload coverage to Codecov
7. Check coverage threshold (>80%)

#### Job 2: Type Checking
```yaml
- name: Type check with mypy
  run: mypy textbox/ --strict
```

#### Job 3: Documentation Build Test
```yaml
- name: Build documentation
  run: |
    pip install mkdocs mkdocs-material
    mkdocs build --strict
```

**Estimated Time**: ~5 minutes per matrix job

### 1.2 PR Quality Checks

**File**: `.github/workflows/pr-checks.yml`

**Triggers**: Pull requests only

**Checks**:
1. No merge conflicts
2. Tests pass
3. Coverage doesn't decrease
4. No failing linter
5. Documentation builds successfully
6. All todos in code have GitHub issues

### 1.3 Dependency Security Scanning

**File**: `.github/workflows/security.yml`

**Triggers**:
- Weekly schedule
- Pull requests touching requirements

**Steps**:
1. Run `pip-audit` for vulnerability scanning
2. Run `safety check` for known security issues
3. Check for outdated dependencies with `pip list --outdated`

---

## Phase 2: GitHub Pages Documentation

### 2.1 Documentation Structure

Use **MkDocs** with **Material theme** for beautiful, searchable docs.

**Structure**:
```
docs/
├── index.md                    # Landing page (from README)
├── getting-started.md          # Already exists
├── quick-start.md              # Already exists
├── vim-mode.md                 # Already exists ✅
├── event-system.md             # Already exists ✅
├── api/
│   ├── index.md               # API overview
│   ├── app.md                 # App class reference
│   ├── text.md                # Text classes
│   ├── events.md              # Event system API
│   └── debug.md               # Debug utilities
├── guides/
│   ├── text-handling.md       # Already exists
│   ├── color-support.md       # Already exists
│   ├── advanced-topics.md     # Already exists
│   └── examples.md            # Already exists
└── development/
    ├── contributing.md         # From CONTRIBUTING.md
    ├── architecture.md         # Already exists
    └── testing.md              # New: testing guide
```

### 2.2 MkDocs Configuration

**File**: `mkdocs.yml`

```yaml
site_name: Textbox
site_description: A powerful, vim-inspired terminal UI library for Python
site_author: Jason Cronquist
site_url: https://jasoncronquist.github.io/textbox/

repo_name: jasoncronquist/textbox
repo_url: https://github.com/jasoncronquist/textbox

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - admonition
  - pymdownx.details
  - pymdownx.tabbed:
      alternate_style: true
  - attr_list
  - md_in_html

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started.md
    - Quick Start: quick-start.md
  - Core Features:
    - Vim Mode: vim-mode.md
    - Event System: event-system.md
    - Text Handling: guides/text-handling.md
    - Color Support: guides/color-support.md
  - API Reference:
    - Overview: api/index.md
    - App Class: api/app.md
    - Text Classes: api/text.md
    - Events: api/events.md
    - Debug Utilities: api/debug.md
  - Guides:
    - Examples: guides/examples.md
    - Advanced Topics: guides/advanced-topics.md
  - Development:
    - Contributing: development/contributing.md
    - Architecture: development/architecture.md
    - Testing: development/testing.md

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [textbox]
          options:
            show_source: true
            show_root_heading: true
            heading_level: 2
```

### 2.3 GitHub Pages Deployment

**File**: `.github/workflows/docs.yml`

```yaml
name: Deploy Documentation

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install mkdocs mkdocs-material mkdocstrings[python]

      - name: Build documentation
        run: mkdocs build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

**GitHub Settings**:
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages` / `root`

**URL**: `https://jasoncronquist.github.io/textbox/`

---

## Phase 3: PyPI Publishing

### 3.1 Package Preparation

**Update** `pyproject.toml`:

```toml
[project]
name = "textbox"
version = "0.2.0"  # Update for release
description = "A powerful, vim-inspired terminal UI library for Python"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

[project.urls]
Homepage = "https://github.com/jasoncronquist/textbox"
Documentation = "https://jasoncronquist.github.io/textbox/"
Repository = "https://github.com/jasoncronquist/textbox"
Issues = "https://github.com/jasoncronquist/textbox/issues"
Changelog = "https://github.com/jasoncronquist/textbox/blob/main/CHANGELOG.md"
```

**Create** `MANIFEST.in`:
```
include README.md
include LICENSE
include CHANGELOG.md
recursive-include textbox *.py py.typed
recursive-include docs *.md
recursive-include examples *.py
exclude tests/*
```

### 3.2 Build Configuration

**Add to** `pyproject.toml`:
```toml
[tool.setuptools]
packages = ["textbox"]

[tool.setuptools.package-data]
textbox = ["py.typed"]

[tool.setuptools.packages.find]
where = ["."]
include = ["textbox*"]
exclude = ["tests*", "docs*"]
```

### 3.3 Automated PyPI Publishing

**File**: `.github/workflows/publish.yml`

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install build tools
        run: |
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

**Setup**:
1. Create PyPI account
2. Generate API token on PyPI
3. Add token to GitHub Secrets as `PYPI_API_TOKEN`

### 3.4 Test PyPI (Optional)

**File**: `.github/workflows/test-publish.yml`

Test publishing to TestPyPI on version tags.

---

## Phase 4: Release Process

### 4.1 Version Management

**Create** `textbox/version.py`:
```python
"""Version information for textbox."""

__version__ = "0.2.0"
__version_info__ = (0, 2, 0)
```

**Update** `textbox/__init__.py`:
```python
from .version import __version__

__all__ = [..., "__version__"]
```

### 4.2 Changelog Management

**Create** `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-11-01

### Added
- Complete vim modal editing (7 modes, 40+ keybindings)
- Visual mode (character and line selection)
- Register system (named, unnamed, numbered)
- Undo/redo with Command pattern (1000-operation history)
- Search functionality (forward/backward with n/N navigation)
- Event system (TextChangedEvent, ModeChangedEvent, CommandExecutedEvent)
- Debug mode with DebugOverlay and enhanced logging
- Complete documentation (vim-mode.md, event-system.md)
- 556 comprehensive tests (82.38% coverage)
- Type hints throughout with py.typed marker

### Changed
- Upgraded to production-ready status
- Improved error messages and validation
- Enhanced resource cleanup

### Fixed
- Memory management in long-running applications
- Cursor positioning edge cases
- Event propagation through component hierarchy

## [0.1.0] - 2025-10-01

### Added
- Initial release
- Basic terminal UI with curses
- Async/await support
- Colored text support
- Command system
- Input/output workspace

[Unreleased]: https://github.com/jasoncronquist/textbox/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/jasoncronquist/textbox/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/jasoncronquist/textbox/releases/tag/v0.1.0
```

### 4.3 Release Script

**Create** `scripts/release.sh`:

```bash
#!/bin/bash
# Release automation script

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/release.sh <version>"
    echo "Example: ./scripts/release.sh 0.2.0"
    exit 1
fi

echo "🚀 Releasing version $VERSION"

# 1. Update version in files
echo "📝 Updating version files..."
sed -i.bak "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
sed -i.bak "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" textbox/version.py

# 2. Run tests
echo "🧪 Running tests..."
pytest tests/ -v

# 3. Build documentation
echo "📚 Building documentation..."
mkdocs build

# 4. Create git tag
echo "🏷️  Creating git tag..."
git add .
git commit -m "chore: release v$VERSION"
git tag -a "v$VERSION" -m "Release v$VERSION"

# 5. Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main
git push origin "v$VERSION"

echo "✅ Release v$VERSION complete!"
echo "👉 Create GitHub release at: https://github.com/jasoncronquist/textbox/releases/new?tag=v$VERSION"
```

### 4.4 Release Checklist

**File**: `.github/RELEASE_CHECKLIST.md`

```markdown
# Release Checklist

Before creating a release:

- [ ] All tests passing locally (`pytest tests/`)
- [ ] Coverage above 80% (`pytest --cov=textbox`)
- [ ] Documentation builds without errors (`mkdocs build`)
- [ ] CHANGELOG.md updated with release notes
- [ ] Version bumped in `pyproject.toml` and `textbox/version.py`
- [ ] README.md updated if needed
- [ ] Examples still work (`python examples/main.py`)

Creating the release:

1. Run `./scripts/release.sh <version>`
2. Verify CI passes on GitHub Actions
3. Create GitHub Release with tag
4. Monitor PyPI publishing workflow
5. Verify package installs: `pip install textbox==<version>`
6. Check documentation site updated

Post-release:

- [ ] Announcement on relevant platforms
- [ ] Update project roadmap
- [ ] Close milestone on GitHub
- [ ] Update development version to next version
```

---

## Phase 5: Monitoring & Badges

### 5.1 Status Badges

**Add to** `README.md`:

```markdown
[![CI](https://github.com/jasoncronquist/textbox/workflows/CI/badge.svg)](https://github.com/jasoncronquist/textbox/actions)
[![Coverage](https://codecov.io/gh/jasoncronquist/textbox/branch/main/graph/badge.svg)](https://codecov.io/gh/jasoncronquist/textbox)
[![PyPI version](https://badge.fury.io/py/textbox.svg)](https://badge.fury.io/py/textbox)
[![Python versions](https://img.shields.io/pypi/pyversions/textbox.svg)](https://pypi.org/project/textbox/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://jasoncronquist.github.io/textbox/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

### 5.2 Codecov Integration

**File**: `.codecov.yml`

```yaml
coverage:
  status:
    project:
      default:
        target: 80%
        threshold: 1%
    patch:
      default:
        target: 80%

comment:
  layout: "reach,diff,flags,tree"
  behavior: default
  require_changes: false
```

**Setup**:
1. Sign up at codecov.io with GitHub
2. Add repository
3. Token is automatic for public repos

### 5.3 Dependabot

**File**: `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Implementation Checklist

### Prerequisites
- [ ] GitHub repository created
- [ ] PyPI account created
- [ ] PyPI API token generated
- [ ] Codecov account setup

### Phase 1: CI/CD (Priority: HIGH)
- [ ] Create `.github/workflows/ci.yml`
- [ ] Create `.github/workflows/pr-checks.yml`
- [ ] Create `.github/workflows/security.yml`
- [ ] Add PYPI_API_TOKEN to GitHub Secrets
- [ ] Test CI pipeline with a PR

### Phase 2: Documentation (Priority: HIGH)
- [ ] Install MkDocs: `pip install mkdocs mkdocs-material`
- [ ] Create `mkdocs.yml`
- [ ] Reorganize docs/ for MkDocs structure
- [ ] Create API reference pages
- [ ] Test local build: `mkdocs serve`
- [ ] Create `.github/workflows/docs.yml`
- [ ] Enable GitHub Pages in repo settings
- [ ] Verify docs site live

### Phase 3: PyPI (Priority: HIGH)
- [ ] Update `pyproject.toml` URLs
- [ ] Create `MANIFEST.in`
- [ ] Create `textbox/version.py`
- [ ] Test local build: `python -m build`
- [ ] Test package install: `pip install dist/*.whl`
- [ ] Create `.github/workflows/publish.yml`
- [ ] (Optional) Test with TestPyPI first

### Phase 4: Release Process (Priority: MEDIUM)
- [ ] Create `CHANGELOG.md`
- [ ] Create `scripts/release.sh`
- [ ] Make script executable: `chmod +x scripts/release.sh`
- [ ] Create `.github/RELEASE_CHECKLIST.md`
- [ ] Test release script on a branch

### Phase 5: Monitoring (Priority: LOW)
- [ ] Add badges to README.md
- [ ] Create `.codecov.yml`
- [ ] Setup Codecov integration
- [ ] Create `.github/dependabot.yml`
- [ ] Enable Dependabot

---

## Post-Deployment

### Verification Steps

After deployment, verify:

1. **CI/CD Pipeline**
   - Push a commit, verify CI runs
   - Create a PR, verify checks pass
   - Merge PR, verify main branch CI runs

2. **Documentation**
   - Visit GitHub Pages URL
   - Verify all pages load
   - Test search functionality
   - Check responsive design

3. **PyPI Package**
   - `pip install textbox` works
   - `import textbox` works
   - Type checking works in user projects
   - Version is correct: `textbox.__version__`

4. **Release Process**
   - Create a test release (v0.2.0-rc1)
   - Verify PyPI publishing
   - Verify changelog updated
   - Verify badges work

### Monitoring

Set up monitoring for:
- **CI failures**: GitHub Actions notifications
- **Security issues**: Dependabot alerts
- **Coverage drops**: Codecov notifications
- **PyPI downloads**: pypistats.org

---

## Estimated Timeline

| Phase | Time | Complexity |
|-------|------|------------|
| Phase 1: CI/CD | 2-4 hours | Medium |
| Phase 2: GitHub Pages | 3-5 hours | Medium |
| Phase 3: PyPI | 2-3 hours | Low-Medium |
| Phase 4: Release Process | 1-2 hours | Low |
| Phase 5: Monitoring | 1 hour | Low |
| **Total** | **9-15 hours** | **Medium** |

---

## Success Metrics

After implementation:
- ✅ CI runs on every commit (<5 min)
- ✅ 100% test pass rate maintained
- ✅ Coverage above 80%
- ✅ Documentation site live and searchable
- ✅ PyPI package installable
- ✅ Releases automated (one command)
- ✅ Security scans weekly
- ✅ Dependencies stay updated

---

## Resources

### Documentation
- [GitHub Actions](https://docs.github.com/en/actions)
- [MkDocs](https://www.mkdocs.org/)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- [PyPI Publishing](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Codecov](https://docs.codecov.com/docs)

### Tools
- `pytest` - Testing framework
- `pytest-cov` - Coverage plugin
- `black` - Code formatter
- `mkdocs` - Documentation generator
- `twine` - PyPI publishing tool
- `build` - Package builder

---

## Notes

- **No breaking changes**: All CI/CD is additive
- **Gradual rollout**: Can implement phases incrementally
- **Rollback plan**: All automation can be disabled via GitHub UI
- **Security**: Use GitHub Secrets for all tokens
- **Cost**: Everything is free for public repos

---

**Ready for Implementation**: This plan is production-ready. Start with Phase 1 (CI/CD) for immediate value.

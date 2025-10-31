# Contributing to Textbox

Thank you for your interest in contributing to Textbox! This guide will help you get started.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

---

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Git
- A Unix-like terminal (Linux, macOS, or WSL on Windows)
- Basic understanding of Python and terminal applications

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/textbox.git
cd textbox
```

3. Add the upstream repository:

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/textbox.git
```

---

## Development Setup

### Create Virtual Environment

Following the project's standard, use `uv` for virtual environment management:

```bash
# Create virtual environment
uv venv

# Activate it
source venv/bin/activate  # On Unix/macOS
# or
venv\Scripts\activate  # On Windows
```

### Install Dependencies

```bash
# Install in development mode
uv pip install -e .

# Install development dependencies (if any)
uv pip install pytest pytest-asyncio
```

### Verify Installation

```bash
# Run an example to verify setup
python examples/main.py
```

---

## Code Style

### General Guidelines

1. **Follow PEP 8**: Python's style guide
2. **Use type hints**: For function parameters and return values
3. **Write docstrings**: For all public classes and methods
4. **Keep it simple**: Prefer clarity over cleverness

### Type Hints

```python
from typing import List, Optional

def process_text(text: str, max_length: Optional[int] = None) -> List[str]:
    """
    Process text into lines.
    
    Args:
        text: The text to process
        max_length: Maximum line length (optional)
    
    Returns:
        List of processed lines
    """
    pass
```

### Docstring Format

Use Google-style docstrings:

```python
class TextBox:
    """Display text in a terminal box.
    
    The TextBox class manages the display of text content
    with support for colors, wrapping, and scrolling.
    
    Attributes:
        window: The curses window to render to
        text_buffer: Buffer of text to display
    """
    
    def add_text(self, text: str) -> None:
        """Add text to the display buffer.
        
        Args:
            text: The text to add
            
        Raises:
            ValueError: If text is empty
        """
        pass
```

### Code Organization

- Keep files focused and single-purpose
- Group related functionality together
- Avoid circular dependencies
- Use clear, descriptive names

---

## Testing

### Test-Driven Development (TDD)

This project follows TDD practices:

1. **Write a test** for the new functionality
2. **Run the test** and verify it fails
3. **Write the code** to make the test pass
4. **Run the test** again to verify it passes
5. **Refactor** if needed while keeping tests green

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest textbox/text_test.py

# Run with coverage
pytest --cov=textbox

# Run tests in verbose mode
pytest -v
```

### Writing Tests

```python
import pytest
from textbox import Text

class TestText:
    """Tests for the Text class"""
    
    def test_create_empty_text(self):
        """Test creating empty text"""
        text = Text()
        assert len(text) == 0
        assert str(text) == ""
    
    def test_insert_text(self):
        """Test inserting text"""
        text = Text()
        text.edit_mode = True
        text.insert("Hello")
        
        assert str(text) == "Hello"
        assert len(text) == 5
    
    def test_insert_without_edit_mode_raises_error(self):
        """Test that insert fails without edit mode"""
        text = Text()
        
        with pytest.raises(RuntimeError):
            text.insert("Hello")
```

### Test Coverage

- Aim for high test coverage (>80%)
- Test edge cases and error conditions
- Test both success and failure paths
- Use fixtures for common setup

---

## Submitting Changes

### Before Submitting

1. **Ensure all tests pass**:
```bash
pytest
```

2. **Check code style**:
```bash
# If using flake8
flake8 textbox

# If using pylint
pylint textbox
```

3. **Update documentation** if needed

4. **Write a clear commit message**:
```bash
git commit -m "Add support for custom color schemes

- Implement ColorScheme class
- Add tests for color customization
- Update documentation with examples
"
```

### Pull Request Process

1. **Update your fork**:
```bash
git fetch upstream
git rebase upstream/main
```

2. **Push your changes**:
```bash
git push origin feature-branch-name
```

3. **Create a Pull Request** on GitHub

4. **Fill out the PR template** with:
   - Description of changes
   - Motivation for the change
   - Any related issues
   - Testing done

5. **Respond to feedback** and make requested changes

### Commit Message Guidelines

Good commit messages:
```
Add cursor position tracking to Text class

- Implement cursor_position property
- Add tests for cursor movement
- Update documentation

Fixes #123
```

Bad commit messages:
```
Fixed stuff
Updated code
WIP
```

---

## Reporting Bugs

### Before Reporting

1. **Check existing issues** to avoid duplicates
2. **Test with the latest version**
3. **Create a minimal reproduction** case

### Bug Report Template

```markdown
**Description**
A clear description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Create app with '...'
2. Call method '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS 12.0]
- Python version: [e.g., 3.9.7]
- Textbox version: [e.g., 0.1.0]
- Terminal: [e.g., iTerm2]

**Code Sample**
```python
import textbox

app = textbox.App()
# ... minimal code to reproduce
```

**Error Output**
```
Full traceback or error message
```
```

---

## Feature Requests

### Proposing Features

1. **Check if already requested** in issues
2. **Describe the use case** clearly
3. **Provide examples** of how it would work
4. **Consider alternatives** and trade-offs

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature.

**Use Case**
Why this feature is needed and who would use it.

**Proposed API**
```python
# Example of how the feature would be used
app.new_feature(parameter="value")
```

**Alternatives Considered**
Other ways this could be implemented or achieved.

**Additional Context**
Any other information or screenshots.
```

---

## Development Workflow

### Typical Workflow

1. **Pick an issue** to work on (or create one)
2. **Create a branch**:
```bash
git checkout -b feature/my-feature
```

3. **Write tests first** (TDD):
```bash
# Create test file
touch textbox/my_feature_test.py

# Write failing tests
# Run: pytest textbox/my_feature_test.py
```

4. **Implement the feature**:
```bash
# Create implementation file
touch textbox/my_feature.py

# Implement until tests pass
```

5. **Refactor** if needed while keeping tests green

6. **Update documentation**

7. **Commit and push**:
```bash
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

8. **Create Pull Request**

---

## Code Review

### What We Look For

- **Correctness**: Does it work as intended?
- **Tests**: Are there tests? Do they pass?
- **Code quality**: Is it readable and maintainable?
- **Documentation**: Are changes documented?
- **No regressions**: Does it break existing functionality?

### Responding to Feedback

- Be open to suggestions
- Ask questions if unclear
- Make requested changes
- Update the PR when ready

---

## Documentation

### Updating Docs

When adding features:

1. **Update relevant documentation** in `docs/`
2. **Add code examples** to show usage
3. **Update API reference** if adding public APIs
4. **Add to CHANGELOG** (if exists)

### Documentation Style

- Use clear, simple language
- Provide code examples
- Include both basic and advanced usage
- Link to related documentation

---

## Community Guidelines

### Be Respectful

- Use welcoming language
- Be respectful of different viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the project

### Get Help

- Ask questions in issues or discussions
- Be specific about what you're trying to do
- Provide context and examples
- Be patient with responses

---

## Additional Resources

- [Architecture Documentation](docs/architecture.md) - Understanding the internals
- [API Reference](docs/api-reference.md) - Complete API documentation
- [Examples](examples/) - Working example code
- [Tests](textbox/*_test.py) - Example test patterns

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

## Thank You!

Thank you for contributing to Textbox! Your efforts help make this project better for everyone.

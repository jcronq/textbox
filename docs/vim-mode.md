# Vim Mode Reference

Textbox features a complete vim-like modal editing system. This guide covers all available modes, keybindings, and vim features.

## Table of Contents

- [Overview](#overview)
- [Input Modes](#input-modes)
- [Command Mode Keybindings](#command-mode-keybindings)
- [Visual Mode](#visual-mode)
- [Register System](#register-system)
- [Undo/Redo](#undoredo)
- [Search](#search)
- [Tips and Tricks](#tips-and-tricks)

---

## Overview

Textbox implements vim-style modal editing with multiple input modes and vim keybindings. This provides a powerful, keyboard-driven interface for text manipulation.

### Why Vim Mode?

- **Efficient text editing** - Navigate and edit without reaching for the mouse
- **Familiar keybindings** - Works like vim, so existing vim users feel at home
- **Powerful operations** - Visual selection, registers, undo/redo, and search
- **Command mode** - Execute custom commands with `:` prefix

---

## Input Modes

Textbox supports 7 different input modes:

### COMMAND Mode (default)

Navigate and manipulate text using vim keybindings. The cursor is visible and you can move around but not type text directly.

**Enter Command Mode:**
- Press `ESC` from any other mode

**Indicators:**
- Status line shows `-- COMMAND --`

### INSERT Mode

Type text normally. Characters are inserted at the cursor position.

**Enter Insert Mode:**
- `i` - Insert at cursor
- `I` - Insert at beginning of line
- `a` - Insert after cursor (append)
- `A` - Insert at end of line
- `o` - Open new line below and enter insert mode
- `O` - Open new line above and enter insert mode
- `c` commands - Change operations (see below)

**Exit Insert Mode:**
- Press `ESC` to return to COMMAND mode

**Indicators:**
- Status line shows `-- INSERT --`

### REPLACE Mode

Similar to INSERT mode, but characters replace existing text instead of inserting.

**Enter Replace Mode:**
- `R` in COMMAND mode

**Exit Replace Mode:**
- Press `ESC` to return to COMMAND mode

**Indicators:**
- Status line shows `-- REPLACE --`

### VISUAL Mode

Select text character-by-character for copy, delete, or change operations.

**Enter Visual Mode:**
- `v` in COMMAND mode

**Operations in Visual Mode:**
- Move cursor with `h`, `j`, `k`, `l`, `w`, `b`, `$`, `0` to extend selection
- `y` - Yank (copy) selection to register
- `d` - Delete selection
- `c` - Change selection (delete and enter INSERT mode)
- `ESC` - Exit visual mode

**Indicators:**
- Status line shows `-- VISUAL --`

### VISUAL LINE Mode

Select entire lines for operations.

**Enter Visual Line Mode:**
- `V` in COMMAND mode

**Operations:**
- Same as VISUAL mode, but operates on entire lines
- Move with `j`/`k` to extend selection line-by-line

**Indicators:**
- Status line shows `-- VISUAL LINE --`

### COMMAND ENTRY Mode

Execute vim-style commands starting with `:`.

**Enter Command Entry Mode:**
- `:` in COMMAND mode

**Usage:**
- Type command name and arguments
- Press `Enter` to execute
- Press `ESC` to cancel

**Built-in Commands:**
- `:help` - Show available commands
- `:q` or `:quit` - Exit application
- Custom commands defined with `@app.command()`

### SEARCH ENTRY Mode

Enter search patterns for finding text.

**Enter Search Entry Mode:**
- `/` for forward search
- `?` for backward search

**Usage:**
- Type search pattern
- Press `Enter` to find first match
- Use `n` and `N` to navigate results

---

## Command Mode Keybindings

### Motion Commands

| Key | Action | Description |
|-----|--------|-------------|
| `h` | Move left | Move cursor one character left |
| `j` | Move down | Move cursor down one line |
| `k` | Move up | Move cursor up one line |
| `l` | Move right | Move cursor one character right |
| `w` | Word forward | Move to start of next word |
| `b` | Word backward | Move to start of previous word |
| `0` | Start of line | Move to beginning of line |
| `$` | End of line | Move to end of line |

### Editing Commands

| Key | Action | Description |
|-----|--------|-------------|
| `i` | Insert | Enter INSERT mode at cursor |
| `I` | Insert at start | Enter INSERT mode at line start |
| `a` | Append | Enter INSERT mode after cursor |
| `A` | Append at end | Enter INSERT mode at line end |
| `o` | Open below | Insert new line below and enter INSERT mode |
| `O` | Open above | Insert new line above and enter INSERT mode |
| `R` | Replace mode | Enter REPLACE mode |

### Deletion Commands

| Key | Action | Description |
|-----|--------|-------------|
| `x` | Delete char | Delete character under cursor |
| `dd` | Delete line | Delete entire current line |
| `D` | Delete to end | Delete from cursor to end of line |

### Change Commands

Change commands delete text and enter INSERT mode.

| Key | Action | Description |
|-----|--------|-------------|
| `cc` | Change line | Delete line and enter INSERT mode |
| `C` | Change to end | Delete to end of line and enter INSERT mode |

### Yank (Copy) Commands

| Key | Action | Description |
|-----|--------|-------------|
| `yy` | Yank line | Copy current line to register |

### Paste Commands

| Key | Action | Description |
|-----|--------|-------------|
| `p` | Paste after | Paste register content after cursor |
| `P` | Paste before | Paste register content before cursor |

### Other Commands

| Key | Action | Description |
|-----|--------|-------------|
| `J` | Join lines | Join current line with next line |
| `u` | Undo | Undo last change |
| `Ctrl-r` | Redo | Redo undone change |
| `:` | Command entry | Enter COMMAND ENTRY mode |
| `/` | Search forward | Search for pattern forward |
| `?` | Search backward | Search for pattern backward |
| `n` | Next match | Jump to next search result |
| `N` | Previous match | Jump to previous search result |
| `v` | Visual mode | Enter VISUAL mode |
| `V` | Visual line | Enter VISUAL LINE mode |
| `Tab` | Cycle focus | Switch between input and output boxes |

---

## Visual Mode

Visual mode allows you to select text for operations.

### Character-wise Selection (VISUAL)

```
1. Press `v` in COMMAND mode
2. Move cursor with h/j/k/l/w/b/$0 to extend selection
3. Perform operation:
   - `y` - Yank (copy) selection
   - `d` - Delete selection
   - `c` - Change selection (delete and enter INSERT mode)
4. Press ESC to exit visual mode
```

**Example:**
```
hello world
^---- cursor here

1. Press 'v' (enter visual mode)
2. Press 'l' 5 times (select "hello")
3. Press 'y' (yank selection)
4. Move to end of line with '$'
5. Press 'p' (paste after cursor)

Result: hello world hello
```

### Line-wise Selection (VISUAL LINE)

```
1. Press `V` in COMMAND mode
2. Move cursor up/down with j/k to select lines
3. Perform operation (y/d/c)
4. Press ESC to exit
```

**Example:**
```
line 1
line 2
line 3

1. Press 'V' on line 2 (select entire line 2)
2. Press 'j' (extend to include line 3)
3. Press 'd' (delete lines 2 and 3)
4. Press 'u' (undo to restore)
```

### Visual Mode Operations

- **Yank (`y`)**: Copies selected text to the unnamed register
- **Delete (`d`)**: Deletes selected text (also copies to register)
- **Change (`c`)**: Deletes selected text and enters INSERT mode

All visual operations support undo/redo with `u` and `Ctrl-r`.

---

## Register System

Registers are vim-style clipboards for storing yanked or deleted text.

### Register Types

1. **Unnamed Register (`"`)**: Default register for yank/delete operations
2. **Named Registers (`a-z`)**: 26 registers you can explicitly use
3. **Numbered Registers (`0-9`)**: Automatic deletion history
   - `"0` - Last yank
   - `"1-9` - Delete history (most recent to oldest)

### Using Registers

#### Yank to Register

```
"<register>yy    - Yank line to named register

Examples:
"ayy    - Yank line to register 'a'
"byy    - Yank line to register 'b'
yy      - Yank line to unnamed register
```

#### Paste from Register

```
"<register>p    - Paste from named register

Examples:
"ap     - Paste from register 'a'
"bp     - Paste from register 'b'
p       - Paste from unnamed register
```

#### Delete to Register

```
"<register>dd   - Delete line to named register

Examples:
"add    - Delete line to register 'a'
dd      - Delete line to unnamed register (also stores in "1)
```

### Register Workflow Example

```python
# Copy from one place, paste in multiple places
1. Position cursor on line to copy
2. "ayy (yank to register 'a')
3. Move to first paste location
4. "ap (paste from register 'a')
5. Move to second paste location
6. "ap (paste from register 'a' again)

# Access delete history
1. dd (delete line - goes to "1)
2. dd (delete another line - previous deletion goes to "2)
3. dd (delete another line - previous deletions shift)
4. "1p (paste first deleted line)
5. "2p (paste second deleted line)
```

---

## Undo/Redo

Textbox implements a complete undo/redo system using the Command pattern.

### Undo

Press `u` in COMMAND mode to undo the last change.

**Undoable Operations:**
- Text insertion
- Text deletion (backspace, x, dd, D)
- Character replacement (R mode)
- Line operations (o, O, J)
- Change operations (cc, C)
- Visual mode operations (delete, change)
- Paste operations (p, P)

### Redo

Press `Ctrl-r` in COMMAND mode to redo an undone change.

### Undo/Redo Limits

- History stores up to **1000 operations**
- New edits clear the redo stack
- Undo/redo works across all operation types

### Example

```
1. Type "hello" in INSERT mode
2. Press ESC
3. Press 'u' - undoes "hello" insertion
4. Press Ctrl-r - redoes "hello" insertion
5. Press 'dd' - deletes line
6. Press 'u' - undoes deletion
7. Press 'u' - undoes "hello" insertion again
```

---

## Search

Search for patterns in your text with `/` and `?`.

### Forward Search

```
1. Press '/' in COMMAND mode
2. Type search pattern
3. Press Enter

Cursor moves to first match after current position.
```

### Backward Search

```
1. Press '?' in COMMAND mode
2. Type search pattern
3. Press Enter

Cursor moves to first match before current position.
```

### Navigate Results

- `n` - Jump to next match (in search direction)
- `N` - Jump to previous match (opposite direction)

### Search Wrapping

Searches automatically wrap:
- Forward search wraps to beginning when reaching end
- Backward search wraps to end when reaching beginning

### Search Pattern Tracking

The last search pattern is remembered, so you can use `n` and `N` without searching again.

### Example

```
Text:
hello world
foo bar
hello again

1. Press '/' (forward search)
2. Type "hello"
3. Press Enter - cursor moves to "hello" on line 1
4. Press 'n' - cursor moves to "hello" on line 3
5. Press 'N' - cursor moves back to "hello" on line 1

Or:

1. Position cursor at end (line 3)
2. Press '?' (backward search)
3. Type "hello"
4. Press Enter - cursor moves to "hello" on line 3
5. Press 'N' - cursor moves to "hello" on line 1 (reverse direction)
```

---

## Tips and Tricks

### Efficient Editing

1. **Stay in COMMAND mode** - Only enter INSERT mode when typing new text
2. **Use visual mode** - Select then operate, rather than counting characters
3. **Leverage registers** - Store frequently used snippets in named registers
4. **Master motions** - `w`, `b`, `$`, `0` are faster than arrow keys

### Common Workflows

#### Copy and Paste Within Document

```
1. 'yy' to yank line
2. Move to destination
3. 'p' to paste
```

#### Copy Multiple Different Snippets

```
1. "ayy (yank to register a)
2. Move to next snippet
3. "byy (yank to register b)
4. Paste from either register with "ap or "bp
```

#### Delete and Restore

```
1. 'dd' to delete (goes to "1)
2. Do other operations
3. "1p to restore deleted line
```

#### Visual Block Operations

```
1. 'V' to enter visual line mode
2. 'jjj' to select 4 lines
3. 'd' to delete all at once
4. 'u' to undo if needed
```

### Keyboard Shortcuts

Most efficient for frequent operations:

- `A` - Jump to end of line and start typing
- `I` - Jump to start of line and start typing
- `o` - Create new line below and start typing
- `cc` - Replace entire line
- `C` - Replace from cursor to end of line

### Debugging Tips

Use `:help` to see available commands in your application.

Check the status line to confirm which mode you're in.

If stuck in a mode, `ESC` always returns to COMMAND mode.

---

## Differences from Standard Vim

Textbox aims for vim compatibility but has some differences:

### Not Implemented

- Text objects (`ciw`, `di"`, `va(`, etc.)
- Counts (`3dd`, `5j`, etc.)
- Marks (`` `a ``, `'a`)
- Macros (`q`, `@`)
- Multi-line regex patterns
- Ex commands beyond `:` prefix

### Behavior Differences

- Single-line focus (works on one text input at a time)
- Search doesn't highlight all matches
- Register operations work on full lines or visual selections only

### Extensions

- **Tab** key cycles focus between input and output boxes
- **Event system** allows reactive features (see event system docs)
- **Async support** for background operations

---

## Learning Path

### Beginner (Day 1)

Master these basics:
- `i` to enter INSERT mode, `ESC` to exit
- `h j k l` for movement
- `u` for undo
- `:quit` to exit

### Intermediate (Week 1)

Add these to your workflow:
- `w b $ 0` for faster movement
- `dd` to delete lines
- `o O` to insert new lines
- `yy p` for copy-paste
- Visual mode with `v`

### Advanced (Month 1)

Master these powerful features:
- Named registers (`"a`, `"b`)
- Visual line mode (`V`)
- Search (`/`, `?`, `n`, `N`)
- Change operations (`cc`, `C`)
- Register history (`"1`, `"2`)

---

## Next Steps

- See [Event System](event-system.md) for reactive programming with vim operations
- Check [API Reference](api-reference.md) for programmatic access to vim features
- Read [Advanced Topics](advanced-topics.md) for custom keybindings
- View [Examples](examples.md) for complete applications using vim mode

Enjoy the power of vim in your terminal applications!

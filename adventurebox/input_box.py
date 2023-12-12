import curses
from enum import Enum

from adventurebox.window import Window
from adventurebox.box_types import BoundingBox
from adventurebox.signals import WindowQuit
from adventurebox.box_types import Coordinate

import logging

logger = logging.getLogger()


class InputHistory:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.history = []
        self.history_ptr = 0
        self.short_term_memory = None

    def has_short_term_memory(self):
        return self.short_term_memory is not None

    def pop_short_term_memory(self):
        tmp = self.short_term_memory
        self.short_term_memory = None
        return tmp

    def set_short_term_memory(self, text: str):
        self.short_term_memory = text

    def at_present(self):
        return self.history_ptr == len(self.history)

    def has_history(self):
        return len(self.history) > 0 and self.history_ptr > 0

    def append(self, text: str):
        self.history.append(text)
        if len(self.history) > self.max_size:
            self.history = self.history[-self.max_size :]
        self.history_ptr = len(self.history)

    def previous(self):
        if self.history_ptr > 0:
            self.history_ptr -= 1
            return self.history[self.history_ptr]
        else:
            return self.history[0]

    def next(self):
        if self.history_ptr < len(self.history) - 1:
            self.history_ptr += 1
            return self.history[self.history_ptr]
        elif self.history_ptr == len(self.history) - 1:
            self.history_ptr += 1
            return self.pop_short_term_memory()
        else:
            return None

    def __getitem__(self, item):
        return self.history[item]

    def __len__(self):
        return len(self.history)


class INPUT_MODE(Enum):
    INSERT = 0
    REPLACE = 1
    COMMAND = 2
    COMMAND_ENTRY = 2


class InputBox:
    focus: "InputBox" = None

    def __init__(self, parent_window: Window, box: BoundingBox):
        self.input_mode = INPUT_MODE.INSERT
        self.text_ptr = 0
        self.text = ""
        self.tmp_text = ""
        self.tmp_history_ptr = -1
        self._history = InputHistory()
        self.history = []
        self._history_ptr = -1
        self.parent_window = parent_window
        self.window = parent_window.create_newwindow(box)
        self.on_submit = lambda x: None

    def focus(self):
        self.window.move(Coordinate(self.text_ptr, 0))
        self.window.refresh()

    def refresh(self):
        self.window.refresh()

    def set_text(self, text: str):
        self.text = text
        self.window.clear()
        self.window.addstr(self.text, Coordinate(0, 0))
        self.text_ptr = len(self.text)
        self.window.refresh()

    def history_scroll_up(self):
        if not self._history.has_history():
            logger.info("Key: Up (No History)")
            return
        elif self._history.at_present():
            logger.info("Key: Up (History) - First Press")
            self._history.set_short_term_memory(self.text)
        else:
            logger.info("Key: Up (History) - Press")
        self.set_text(self._history.previous())

    def history_scroll_down(self):
        if self._history.at_present():
            logger.info("Key: Down (History) - No further history")
            return
        else:
            logger.info("Key: Down (History) - Press")
            self.set_text(self._history.next())

    def append_history(self):
        self._history.append(self.text)

    def cursor_down(self):
        pass

    def cursor_up(self):
        pass

    def cursor_left(self):
        new_coord = self.window.cursor_coord - Coordinate(1, 0)
        if new_coord.x >= 0:
            self.text_ptr -= 1
            self.window.move(new_coord)
            self.window.refresh()

    def cursor_right(self):
        new_coord = self.window.cursor_coord + Coordinate(1, 0)
        if new_coord.x <= len(self.text):
            self.text_ptr += 1
            self.window.move(new_coord)
            self.window.refresh()

    def clear_text(self):
        self.text = ""
        self.text_ptr = 0
        self.window.clear()
        self.window.addch(" ", Coordinate(0, 0))
        self.window.move(Coordinate(0, 0))
        self.window.refresh()

    def handle_backspace(self):
        if self.text_ptr == 0:
            return
        self.text = self.text[: self.text_ptr - 1] + self.text[self.text_ptr :]
        self.text_ptr -= 1
        self.window.addstr(self.text, Coordinate(0, 0))
        self.window.addch(" ", Coordinate(len(self.text), 0))
        self.window.move(Coordinate(self.text_ptr, 0))
        self.window.refresh()

    def insert_character_at_cursor(self, ch: str):
        if self.text_ptr == len(self.text):
            self.text += ch
        else:
            self.text = self.text[: self.text_ptr] + ch + self.text[self.text_ptr :]
        self.text_ptr += 1
        self.window.addch(ch, Coordinate(self.text_ptr - 1, 0))
        self.window.addstr(self.text[self.text_ptr :], self.window.cursor_coord)
        self.window.move(Coordinate(self.text_ptr, 0))
        self.window.refresh()

    def replace_character_at_cursor(self, ch: str):
        self.text = self.text[: self.text_ptr] + ch + self.text[self.text_ptr + 1 :]
        self.text_ptr += 1
        self.window.addch(ch, self.window.cursor_coord)
        self.window.refresh()

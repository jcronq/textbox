import curses
from enum import Enum

from adventurebox.window import Window
from adventurebox.box_types import BoundingBox
from adventurebox.signals import WindowQuit
from adventurebox.box_types import Coordinate
from adventurebox.text_box import TextBox

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


class InputBox(TextBox):
    def __init__(
        self,
        parent_window: Window,
        box: BoundingBox,
        color_pair: int = 0,
        top_to_bottom: bool = True,
        draw_box: bool = False,
    ):
        super().__init__(parent_window, box, color_pair, top_to_bottom, draw_box)
        self._history = InputHistory()

    def set_text(self, text: str):
        self.text = text
        self.redraw()

    @property
    def text(self):
        return self.lines[0]

    @text.setter
    def text(self, value):
        self.lines[0] = value

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
        self.column_ptr += self.printable_width
        self.window.move(self.cursor_coord)
        self.window.refresh()

    def cursor_up(self):
        self.column_ptr -= self.printable_width
        self.window.move(self.cursor_coord)
        self.window.refresh()

    def cursor_left(self):
        self.column_ptr -= 1
        logger.info("Cursor Left: %s, %s", self.column_ptr, self.cursor_coord)
        self.window.move(self.cursor_coord)
        logger.info("Cursor moved")
        self.window.refresh()

    def cursor_right(self):
        # new_coord = self.window.cursor_coord + Coordinate(1, 0)
        logger.info("Cursor Right: %s, %s", self.column_ptr, len(self.text))
        self.column_ptr += 1
        logger.info("Cursor Right: %s, %s", self.column_ptr, self.cursor_coord)
        self.window.move(self.cursor_coord)
        logger.info("Cursor moved")
        self.window.refresh()

    def handle_backspace(self):
        if self.column_ptr == 0:
            return
        self.text = self.text[: self.column_ptr - 1] + self.text[self.column_ptr :]
        self.column_ptr -= 1
        self.redraw(with_cursor=True)

    def insert_character_at_cursor(self, ch: str):
        self.text = self.text[: self.column_ptr] + ch + self.text[self.column_ptr :]
        self.column_ptr += 1
        self.redraw(with_cursor=True)

    def replace_character_at_cursor(self, ch: str):
        self.text = self.text[: self.column_ptr] + ch + self.text[self.column_ptr + 1 :]
        self.column_ptr += 1
        self.redraw(with_cursor=True)

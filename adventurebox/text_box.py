from typing import List, Union
import curses

from adventurebox.window import Window
from adventurebox.box_types import BoundingBox, Position
from adventurebox.text import Text
from adventurebox.text_list import TextList

import logging

logger = logging.getLogger()


class TextBox:
    def __init__(
        self,
        name: str,
        parent_window: Window,
        box: BoundingBox,
        color_pair: int = 0,
        top_to_bottom: bool = True,
        has_box: bool = False,
    ):
        self.name = name
        self._has_box = has_box
        self.top_to_bottom = top_to_bottom

        self.parent_window = parent_window
        self.window = parent_window.create_new_window(box)

        self.color_pair = color_pair

        self._text_list: TextList = TextList()
        self._text_ptr = 0
        self._first_lineno_in_window = 0
        self._box_visible = False
        self._text_list.max_line_width = self.printable_width
        self.verbose = False

    def resize(self, box: BoundingBox):
        self.window.resize(box, self.verbose)

    @property
    def attributes(self):
        return [curses.color_pair(self.color_pair)]

    @property
    def box_visible(self):
        return self._box_visible

    @box_visible.setter
    def box_visible(self, value: bool):
        self._box_visible = value
        if value:
            self.window.add_box(verbose=self.verbose)
            self.refresh()

    @property
    def column_ptr(self):
        return self._text_list.current_text.column_ptr

    @property
    def current_line(self):
        return self._text_list.current_text.current_line

    @property
    def height(self):
        return self.window.height

    @property
    def width(self):
        return self.window.width

    @property
    def printable_width(self):
        if self._has_box:
            # -1 for left side of box. -1 for right side of box. -1 for cursor buffer.
            return self.width - 3
        return self.width

    @property
    def printable_height(self):
        if self._has_box:
            return self.height - 2
        return self.height

    @property
    def first_printable_lineno(self):
        if self._has_box:
            return 1
        return 0

    @property
    def last_printable_lineno(self):
        if self._has_box:
            return self.printable_height
        return self.height

    @property
    def first_printable_column(self):
        if self._has_box:
            return 1
        return 0

    @property
    def last_printable_column(self):
        if self._has_box:
            return self.first_printable_column + self.printable_width
        return self.width

    @property
    def first_viewable_lineno(self):
        return self._first_lineno_in_window

    @property
    def last_viewable_lineno(self):
        return self._first_lineno_in_window + self.printable_height

    @property
    def cursor_position(self) -> Position:
        position = self._text_list.current_text.cursor_position

        if self._has_box:
            position += Position(1, 1)
        position -= Position(self._first_lineno_in_window, 0)

        return position

    def adjust_screen_position(self):
        position = self._text_list.current_text.cursor_position
        if self.verbose:
            logger.info("Current position: %s", position)
        if self._has_box:
            position += Position(1, 1)
        position -= Position(self._first_lineno_in_window, 0)
        if position.lineno > self.last_printable_lineno:
            self.scroll_down(position.lineno - self.last_printable_lineno)
            position = Position(self.last_printable_lineno, position.colno)
        elif position.lineno < self.first_printable_lineno:
            if self.verbose:
                logger.info(
                    "position %s is above first printable line %s", position.lineno, self.first_printable_lineno
                )
            self.scroll_up(self.first_printable_lineno - position.lineno)
            position = Position(self.first_printable_lineno, position.colno)
            if self.verbose:
                logger.info("New position in window: %s", position)

    def scroll_down(self, n_lines):
        self._first_lineno_in_window += n_lines
        if self.verbose:
            logger.info("New first line in window: %s", self._first_lineno_in_window)
        self.redraw()

    def scroll_up(self, n_lines):
        self._first_lineno_in_window -= n_lines
        if self.verbose:
            logger.info("New first line in window: %s", self._first_lineno_in_window)
        self.redraw()

    def erase(self):
        self._text_list = []
        self._text_ptr = 0
        self.window.erase(verbose=self.verbose)

    def refresh(self):
        self.window.refresh(verbose=self.verbose)

    def update_cursor(self):
        self.window.move_cursor(self.cursor_position, verbose=self.verbose)
        self.window.refresh(verbose=self.verbose)

    def redraw(self, with_cursor: bool = False):
        self.window.erase(verbose=self.verbose)
        self.adjust_screen_position()
        if self._box_visible:
            logger.debug("Drawing box")
            self.window.add_box(verbose=self.verbose)
        logger.debug("cleared")
        self.draw_texts()
        if with_cursor:
            self.window.move_cursor(self.cursor_position, verbose=self.verbose)
            logger.debug("Cursor moved to %s", self.cursor_position)
        logger.debug("Texts added")
        self.refresh()
        logger.debug("refreshed")

    def hline(self, position: Position):
        self.window.hline(position, verbose=self.verbose)

    def print_text(self, text: str):
        self.add_text(text)
        self.redraw()

    def add_text(self, text: Text):
        text.max_line_width = self.printable_width
        self._text_list.add_text(text)
        self.redraw()

    def add_str(self, text: str):
        self._text_list[self._text_ptr].insert(text)

    def add_char(self, text: str):
        self._text_list[self._text_ptr].insert(text)

    def draw_texts(self):
        if self._text_list.line_count == 0:
            return

        visible_lines = self._text_list[self.first_viewable_lineno : self.last_viewable_lineno]
        logger.debug("visible_lines: %s", visible_lines)
        if not self.top_to_bottom:
            logger.debug("reversed printable set")
            visible_lines.reverse()

        for idx, line in enumerate(visible_lines):
            columnno = self.first_printable_column
            local_lineno = idx + self.first_printable_lineno
            if not self.top_to_bottom:
                local_lineno = self.printable_height - local_lineno + 1

            position = Position(local_lineno, columnno)
            logger.debug(
                "%s - draw line %s %s: %s/%s (%s%s) at Coord(%s): %s/%s char w/ box=%s",
                self.name,
                idx,
                "top to bottom" if self.top_to_bottom else "bottom to top",
                local_lineno,
                self.printable_height,
                line[:5],
                "..." if len(line) > 5 else "",
                position,
                len(line),
                self.printable_width,
                self._has_box,
            )
            self.window.addstr(str(line), position, attributes=self.attributes, verbose=self.verbose)

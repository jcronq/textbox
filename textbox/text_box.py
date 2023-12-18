from typing import List, Union
import curses

from textbox.window import Window
from textbox.box_types import BoundingBox, Position
from textbox.text import Text
from textbox.text_list import TextList

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
        self._first_lineno_in_window = 0
        self._box_visible = False
        self._text_list.max_line_width = self.printable_width
        self.verbose = False

    def resize(self, box: BoundingBox):
        total_line_count = self._text_list.line_count
        if self.last_viewable_lineno <= total_line_count:
            value = self.last_viewable_lineno
        else:
            value = total_line_count
        self.window.resize(box, self.verbose)
        self._text_list.max_line_width = self.printable_width
        self.last_viewable_lineno = value

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
        return self.width - 1

    @property
    def printable_height(self):
        if self._has_box:
            return self.height - 2
        return self.height - 1

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
        return self.width - 1

    @property
    def first_viewable_lineno(self):
        return self._first_lineno_in_window

    @property
    def last_viewable_lineno(self):
        return self._first_lineno_in_window + self.printable_height

    @last_viewable_lineno.setter
    def last_viewable_lineno(self, value: int):
        if not isinstance(value, int):
            raise TypeError("last_viewable_lineno must be an integer")
        self._first_lineno_in_window = max(value - self.printable_height, 0)

    @property
    def box_offset(self):
        if self._has_box:
            return Position(1, 1)
        return Position(0, 0)

    @property
    def cursor_position(self) -> Position:
        position = self._text_list.cursor_position

        position += self.box_offset
        position -= Position(self._first_lineno_in_window, 0)

        if self.verbose:
            logger.info(
                "Current position: %s, first_line: %s, box_offset %s",
                position,
                self._first_lineno_in_window,
                self.box_offset,
            )
            logger.debug("TextList: %s", self._text_list)

        return position

    def adjust_screen_position(self):
        position = self._text_list.cursor_position
        position = position + self.box_offset - Position(self._first_lineno_in_window, 0)
        if self.verbose:
            logger.info(
                "Cursor Position in Window: %s, Limits[%s, %s]",
                position,
                self.last_printable_lineno,
                self.first_printable_lineno,
            )
        if position.lineno > self.last_printable_lineno:
            self.scroll_down(position.lineno - self.last_printable_lineno)
            position = Position(self.last_printable_lineno, position.colno)
        elif position.lineno < self.first_printable_lineno:
            self.scroll_up(self.first_printable_lineno - position.lineno)
            position = Position(self.first_printable_lineno, position.colno)

    def scroll_down(self, n_lines):
        self._first_lineno_in_window += n_lines
        if self.verbose:
            logger.info("Scroll down: %s, first_line @ %s", n_lines, self._first_lineno_in_window)
        self.redraw()

    def scroll_up(self, n_lines):
        self._first_lineno_in_window -= n_lines
        if self.verbose:
            logger.info("Scroll up: %s, first_line @ %s", n_lines, self._first_lineno_in_window)
        if self._first_lineno_in_window < 0:
            raise ValueError("Cannot scroll up past first line")
        self.redraw()

    def erase(self):
        self._text_list = []
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
        self._text_list.insert(text)
        self.redraw()

    def end_current_text(self):
        self._text_list.increment_text_ptr()

    def add_char(self, text: str):
        self._text_list.current_text.edit_mode = True
        self._text_list.current_text.insert(text)
        self._text_list.current_text.edit_mode = False

    def draw_texts(self):
        if self._text_list.line_count == 0:
            return

        if self.verbose:
            logger.info("Drawing texts on lines: %s - %s", self.first_viewable_lineno, self.last_viewable_lineno)
        visible_lines = self._text_list[self.first_viewable_lineno : self.last_viewable_lineno]
        logger.debug("visible_lines: %s", visible_lines)
        if not self.top_to_bottom:
            logger.debug("reversed printable set")
            visible_lines.reverse()

        for idx, line in enumerate(visible_lines):
            columnno = self.first_printable_column
            local_lineno = idx + self.first_printable_lineno
            if not self.top_to_bottom:
                local_lineno = self.printable_height - local_lineno + (1 if self._has_box else 0)

            position = Position(local_lineno, columnno)
            logger.info(
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
            # self.window.addstr(str(line), position, attributes=self.attributes, verbose=self.verbose)
            offset = 0
            for idx, text_segment in enumerate(line):
                attributes = [curses.color_pair(text_segment.color_pair)]
                position = Position(local_lineno, columnno + offset)
                self.window.addstr(str(text_segment), position, attributes=attributes, verbose=self.verbose)
                offset += len(text_segment)

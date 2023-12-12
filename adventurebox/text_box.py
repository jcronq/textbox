import curses
from adventurebox.window import Window
from adventurebox.box_types import BoundingBox, Coordinate

import logging

logger = logging.getLogger()


class TextBox:
    def __init__(self, parent_window: Window, box: BoundingBox, color_pair: int = 0):
        self.lines = []
        self.col_output_ptr = 0
        self.line_output_ptr = 0
        self.parent_window = parent_window
        self.window = parent_window.create_newwindow(box)
        self.attributes = [curses.color_pair(color_pair)]

    @property
    def height(self):
        return self.window.height

    @property
    def width(self):
        return self.window.width

    def refresh(self):
        self.window.refresh()

    def hline(self, coordinate: Coordinate):
        self.window.hline(coordinate)

    def add_line(self, text_line):
        self.lines.append(text_line)
        for idx, line in enumerate(self.lines[-(self.height - 1) :][::-1]):
            self.window.addstr(
                line + " " * (self.width - len(line)), Coordinate(1, idx + 1), attributes=self.attributes
            )
        self.window.refresh()

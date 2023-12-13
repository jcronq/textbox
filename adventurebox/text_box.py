import curses
from adventurebox.window import Window
from adventurebox.box_types import BoundingBox, Coordinate

import logging

logger = logging.getLogger()


class TextBox:
    def __init__(
        self,
        parent_window: Window,
        box: BoundingBox,
        color_pair: int = 0,
        top_to_bottom: bool = True,
        draw_box: bool = False,
    ):
        self.lines = [""]
        self._column_ptr = 0
        self._line_ptr = 0
        self.parent_window = parent_window
        self.window = parent_window.create_newwindow(box)
        self.attributes = [curses.color_pair(color_pair)]
        self.top_to_bottom = top_to_bottom
        self.draw_box = draw_box
        if self.draw_box:
            self.window.box()
            self.refresh()

    @property
    def column_ptr(self):
        return self._column_ptr

    @column_ptr.setter
    def column_ptr(self, value):
        logger.info("Setting column_ptr to %s, %s, %s", value, self.line_ptr, len(self.lines))
        if value < 0:
            if self.line_ptr == 0:
                self._column_ptr = 0
            else:
                self.line_ptr -= 1
                self._column_ptr = len(self.lines[self.line_ptr])
        elif value > len(self.lines[self.line_ptr]):
            if self.line_ptr == len(self.lines) - 1:
                self._column_ptr = len(self.lines[self.line_ptr])
            else:
                self.line_ptr += 1
                self._column_ptr = 0
        else:
            self._column_ptr = value

    @property
    def line_ptr(self):
        return self._line_ptr

    @line_ptr.setter
    def line_ptr(self, value):
        if value < 0:
            self._line_ptr = 0
        elif value > len(self.lines):
            self._line_ptr = len(self.lines)
        else:
            self._line_ptr = value

    @property
    def top_line(self):
        return self.window.height - 1

    @property
    def height(self):
        return self.window.height

    @property
    def width(self):
        return self.window.width

    @property
    def printable_width(self):
        if self.draw_box:
            return self.width - 2
        return self.width

    @property
    def printable_height(self):
        if self.draw_box:
            return self.height - 2
        return self.height

    @property
    def cursor_coord(self) -> Coordinate:
        if self.top_to_bottom:
            x = self.column_ptr % self.printable_width
            apparent_line_number = self.column_ptr // self.printable_width
            y = self.top_line - apparent_line_number
        else:
            raise NotImplementedError("Bottom to top not implemented")
        if self.draw_box:
            logger.info("Moving + 1")
            return Coordinate(x + 1, y + 1)
        else:
            logger.info("Moving")
            return Coordinate(x, y)

    def clear(self):
        self.lines = [""]
        self.column_ptr = 0
        self.line_ptr = 0
        self.window.clear()

    def refresh(self):
        self.window.refresh()

    def redraw(self, with_cursor: bool = False):
        logger.info("Redrawing %s", self.lines[0])
        self.window.clear()
        if self.draw_box:
            self.window.box()
        logger.info("cleared")
        self.update()
        logger.info("updated")
        if with_cursor:
            self.window.move(self.cursor_coord)
        self.refresh()
        logger.info("refreshed")

    def hline(self, coordinate: Coordinate):
        self.window.hline(coordinate)

    def print_str(self, text: str, end_line: bool = False):
        self.add_str(text, end_line=end_line)
        self.redraw()

    def print_line(self, text: str):
        self.add_line(text)
        self.redraw()

    def add_line(self, text: str):
        self.add_str(text, end_line=True)

    def add_str(self, text, end_line: bool = False):
        if self.line_ptr < 0 or self.line_ptr >= len(self.lines):
            raise ValueError(
                f"The line_output_ptr is out of bounds: Line: {self.line_ptr}, NumLines: {len(self.lines)}"
            )
        if self.column_ptr < 0 or self.column_ptr > len(self.lines[self.line_ptr]) + 1:
            raise ValueError(
                f"The column_ptr is out of bounds: Line: {self.line_ptr}, Col: {self.column_ptr}, Text: {self.lines[self.line_ptr]}"
            )
        if self.column_ptr == len(self.lines[self.line_ptr]) + 1:
            self.lines[self.line_ptr] += text
            self.column_ptr += len(text)
        else:
            self.lines[self.line_ptr] = (
                self.lines[self.line_ptr][: self.column_ptr] + text + self.lines[self.line_ptr][self.column_ptr :]
            )
            self.column_ptr += len(text)
        if end_line:
            self._line_ptr += 1
            self._column_ptr = 0
            if self.line_ptr == len(self.lines):
                self.lines.append("")
            else:
                self.lines.insert(self.line_ptr, "")

    def update(self):
        if len(self.lines) == 0:
            return

        focused_line = self.line_ptr
        # If the curosor is at the start of an empty line, move cursor back one.
        if self.column_ptr == 0 and self.lines[self.line_ptr] == "" and self.line_ptr == len(self.lines) - 1:
            focused_line = self.line_ptr - 1

        printable_lines = []
        start_line = focused_line
        end_line = max(
            (start_line - self.height) - 1, -1
        )  # the number of lines taht will fill the height, or -1 if there are fewer lines than the height
        for idx in range(start_line, end_line, -1):
            if len(printable_lines) >= self.height:
                break
            line = self.lines[idx]
            total_lines_used = len(line) // (self.printable_width)
            if total_lines_used == 0:
                printable_lines.append(line)
            else:
                for split_idx in range(total_lines_used, -1, -1):
                    if len(printable_lines) >= self.height:
                        break
                    printable_lines.append(
                        line[split_idx * self.printable_width : (split_idx + 1) * self.printable_width]
                    )

        step_direction = -1 if self.top_to_bottom else 1
        for idx, line in enumerate(printable_lines[::step_direction]):
            # line += " " * (self.printable_width - len(line))
            if idx >= self.printable_height:
                break
            x_offset = 1 if self.draw_box else 0
            if self.top_to_bottom:
                y_offset = self.top_line - idx
            else:
                y_offset = idx
            y_offset += 1 if self.draw_box else 0
            coord = Coordinate(x_offset, y_offset)
            logger.info("Line: %s, %s, %s, %s", idx, coord, line, self.draw_box)
            self.window.addstr(line, coord, attributes=self.attributes)

import curses
from adventurebox.window import Window
from adventurebox.box_types import BoundingBox, Coordinate

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
        self.lines = [""]
        self._column_ptr = 0
        self._line_ptr = 0
        self._view_line = 0
        self.parent_window = parent_window
        self.window = parent_window.create_newwindow(box)
        self.color_pair = color_pair
        self.top_to_bottom = top_to_bottom
        self.has_box = has_box
        self._box_visible = False

    @property
    def attributes(self):
        return [curses.color_pair(self.color_pair)]

    @property
    def box_visible(self):
        return self._box_visible

    @box_visible.setter
    def box_visible(self, value: bool):
        self._box_visible = value
        self.window.box()
        self.refresh()

    @property
    def column_ptr(self):
        return self._column_ptr

    @column_ptr.setter
    def column_ptr(self, value):
        if value < 0:
            if self.line_ptr <= 0:
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

        # Position the view if the cursor is out of view
        # if self.top_to_bottom:
        # apparent_number =
        if self.apparent_line_number > (self.printable_height):
            logger.info("View violation: %s > %s", self.apparent_line_number, self.printable_height)
            self._view_line += self.apparent_line_number - (self.printable_height)
            logger.info("Moved view (add): %s", self._view_line)
        elif self.apparent_line_number < 0:
            logger.info("View violation: %s < 0", self.apparent_line_number)
            self._view_line += self.apparent_line_number
            logger.info("Moved view (sub): %s", self._view_line)
        logger.info("column_ptr set to %s, Coordinate(%s)", value, self.cursor_coord)

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
        if self.has_box:
            return self.height - 1
        return self.height

    @property
    def bottom_line(self):
        if self.has_box:
            return 1
        return 0

    @property
    def height(self):
        return self.window.height

    @property
    def width(self):
        return self.window.width

    @property
    def printable_width(self):
        if self.has_box:
            return self.width - 2
        return self.width

    @property
    def printable_height(self):
        if self.has_box:
            return self.height - 2
        return self.height

    @property
    def apparent_line_number(self):
        apparent_ptr = 0
        if self.lines[self.line_ptr] == "" and self.line_ptr == len(self.lines) - 1:
            lines = self.lines[:-1]
        else:
            logger.info("line_ptr: %s, len(lines): %s", self.line_ptr, len(self.lines))
        lines = self.lines[: self.line_ptr + 1]

        for text_line in lines:
            apparent_ptr += (len(text_line) // self.printable_width) + 1
        return apparent_ptr - self._view_line

    @property
    def top_viewable_line(self):
        return self._view_line

    @property
    def bottom_viewable_line(self):
        return self._view_line + self.printable_height

    @property
    def cursor_coord(self) -> Coordinate:
        x = self.column_ptr % self.printable_width + 1 if self.has_box else 0
        if self.top_to_bottom:
            logger.debug(
                "name: %s, top_line: %s, apparent_line: %s", self.name, self.top_line, self.apparent_line_number
            )
            y = self.top_line - self.apparent_line_number
        else:
            y = self.bottom_line + self.apparent_line_number
        return Coordinate(x, y)

    def clear(self):
        self.lines = [""]
        self.column_ptr = 0
        self.line_ptr = 0
        self.window.clear()

    def synchronize_cursor(self):
        self.window.move(self.cursor_coord)
        self.window.refresh()

    def refresh(self):
        self.window.refresh()

    def redraw(self, with_cursor: bool = False):
        logger.info("Redrawing %s%s", self.lines[0][:5], "..." if len(self.lines[0]) > 5 else "")
        self.window.clear()
        if self._box_visible:
            self.window.box()
        logger.info("cleared")
        self.update()
        logger.info("updated")
        if with_cursor:
            self.window.move(self.cursor_coord)
            logger.info("Cursor moved to %s", self.cursor_coord)
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

        lines = self.lines
        if len(lines[-1]) == 0:
            lines = lines[:-1]
        printable_lines = []
        for idx, line in enumerate(lines):
            sub_line_count = len(line) // self.printable_width
            for split_idx in range(sub_line_count + 1):
                printable_lines.append(line[split_idx * self.printable_width : (split_idx + 1) * self.printable_width])

        visible_lines = printable_lines[self.top_viewable_line : self.bottom_viewable_line]
        logger.info(
            "Viewable Bounds: %s - %s : cursor on apparent line %s",
            self.top_viewable_line,
            self.bottom_viewable_line,
            self.apparent_line_number,
        )
        logger.info("self.lines: %s", self.lines)
        logger.info("lines: %s", lines)
        logger.info("printable_lines: %s", printable_lines)
        logger.info("visible_lines: %s", visible_lines)
        if not self.top_to_bottom:
            logger.info("reversed printable set")
            visible_lines.reverse()
        for idx, line in enumerate(visible_lines):
            x_offset = 1 if self.has_box else 0
            box_offset = 1 if self.has_box else 0
            line_num = idx
            if self.top_to_bottom:
                line_num = self.printable_height - (idx + 1)
            y_offset = line_num + box_offset
            coord = Coordinate(x_offset, y_offset)
            logger.info(
                "draw line %ss: %s/%s (%s%s) at Coord(%s): %s/%s char w/ box=%s",
                idx,
                y_offset,
                self.printable_height,
                line[:5],
                "..." if len(line) > 5 else "",
                coord,
                len(line),
                self.printable_width,
                self.has_box,
            )
            self.window.addstr(line, coord, attributes=self.attributes)

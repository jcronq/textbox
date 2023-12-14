from typing import Optional, Tuple
from collections import namedtuple

import curses
from curses import window

from adventurebox.box_types import Coordinate, BoundingBox, Dimensions

import logging

logger = logging.getLogger()


class Window:
    def __init__(
        self,
        local_window: window,
        coordinate: Optional[Coordinate] = None,
        dimensions: Optional[Dimensions] = None,
        parent_window: Optional["Window"] = None,
    ):
        if parent_window is None and (coordinate is not None or dimensions is not None):
            raise ValueError("Cannot specify coordinate or dimensions without a parent window")
        self.__children = []
        self.coordinate = coordinate if coordinate is not None else Coordinate(0, 0)
        self.dimensions = dimensions if dimensions is not None else Dimensions(curses.COLS, curses.LINES)
        self._local_window = local_window
        self.__parent = parent_window

        # Validate bounding box of the window
        if self.__parent is not None:
            if not (
                self.__parent.contains_coordinate_locally(self.coordinate)
                and self.__parent.contains_coordinate_locally(self.coordinate + self.dimensions)
            ):
                raise ValueError(
                    f"Window {self.bounding_box} is not contained within parent window {self.__parent.bounding_box}"
                )

    @property
    def width(self):
        return self.dimensions.width

    @property
    def height(self):
        return self.dimensions.height

    @property
    def x(self):
        return self.coordinate.x

    @property
    def y(self):
        return self.coordinate.y

    @property
    def bounding_box(self):
        return BoundingBox(self.x, self.y, self.width, self.height)

    @property
    def main_window(self):
        if self.__parent is None:
            return self
        return self.__parent.main_window

    @property
    def cursor_coord(self) -> Coordinate:
        curses_coord = self._local_window.getyx()
        return self._translate_curses_coord_to_local_coordinate(curses_coord)

    def _translate_local_coordinate_to_local_curses_coord(self, coord: Coordinate) -> (int, int):
        return self.height - (coord.y + 1), coord.x

    def _translate_curses_coord_to_local_coordinate(self, coord: Tuple[int, int]) -> Coordinate:
        return Coordinate(coord[1], self.height - coord[0])

    def validate_contains_bounding_box(self, box: BoundingBox):
        if not (self.contains_coordinate_locally(box.bottom_left) and self.contains_coordinate_locally(box.top_right)):
            raise ValueError(f"Window {self.bounding_box} does not contain bounding box {box}")

    def validate_contains_coordinate(self, coord: Coordinate):
        if not self.contains_coordinate_locally(coord):
            raise ValueError(f"Window {self.bounding_box} does not contain coordinate {coord}")

    def contains_coordinate_globally(self, coord):
        return self.main_window.contains_coordinate_locally(coord)

    def contains_coordinate_locally(self, coord: Coordinate):
        return 0 <= coord.y <= self.dimensions.height and 0 <= coord.x <= self.dimensions.width

    def create_newwindow(self, box: BoundingBox, validate_input=True) -> "Window":
        if validate_input:
            self.main_window.validate_contains_bounding_box(box)
        logger.info("Creating new window: %s", box)
        logger.info("top_left: %s", box.top_left)
        y, x = self.main_window._translate_local_coordinate_to_local_curses_coord(box.top_left)
        logger.info(f"({box.height}, {box.width}, {y}, {x})")
        subwin = curses.newwin(box.height, box.width, y, x)
        new_window = Window(subwin, box.coordinate, box.dimensions, parent_window=self)
        self.__children.append(new_window)
        return new_window

    def refresh(self):
        self._local_window.refresh()

    def refresh_all(self):
        self._local_window.refresh()
        for subwin in self.__children:
            subwin.refresh()

    def clear(self):
        logger.info("Cleared window")
        self._local_window.erase()

    def alert(self, msg):
        self.addstr(msg, Coordinate(0, 0))
        self.refresh()

    def addch(self, ch: str, coord: Coordinate = None, attributes: list = None):
        if type(ch) is not str:
            raise ValueError(f"ch must be a string, not {type(ch)}")
        if len(ch) != 1:
            raise ValueError(f"ch must be a single character, not {len(ch)}")
        if attributes is None:
            attributes = []
        if coord is not None:
            self.validate_contains_coordinate(coord)
            curses_coord = self._translate_local_coordinate_to_local_curses_coord(coord)
            try:
                self._local_window.addch(*curses_coord, ch, *attributes)
            except curses.error:
                pass

        else:
            self._local_window.addch(str(ch))

    def addstr(self, text: str, coord: Coordinate = None, attributes: list = None):
        if attributes is None:
            attributes = []
        if coord is not None:
            self.validate_contains_coordinate(coord)
            curses_coord = self._translate_local_coordinate_to_local_curses_coord(coord)
            logger.info(f"Adding string at Coord({coord}); curses{curses_coord}")
            try:
                self._local_window.addstr(*curses_coord, text, *attributes)
            except curses.error:
                pass
        else:
            self._local_window.addstr(text, *attributes)

    def getkey(self) -> str:
        return self._local_window.getkey()

    def getch(self) -> str:
        return self._local_window.getch()

    def getstr(self, coord: Coordinate, n: int) -> str:
        return self._local_window.getstr(*self._translate_local_coordinate_to_local_curses_coord(coord), n)

    def move(self, coord: Coordinate):
        curses_coord = self._translate_local_coordinate_to_local_curses_coord(coord)
        logger.info(f"Window: Moving to Coord({coord}) Curses{curses_coord} within {self.dimensions}")
        self._local_window.move(*curses_coord)

    def resize(self, box: BoundingBox):
        logger.info("Resizing window to %s, %s, %s", box, box.coordinate, box.dimensions)
        self.dimensions = box.dimensions
        self.coordinate = box.coordinate
        try:
            self._local_window.resize(box.height, box.width)
            self.dimensions = box.dimensions
        except curses.error:
            logger.error("Failed to resize window to %s", box.dimensions)
        curses_coord = self.main_window._translate_local_coordinate_to_local_curses_coord(box.top_left)
        try:
            self._local_window.mvwin(*curses_coord)
            self.coordinate = box.coordinate
        except curses.error:
            logger.error("Failed to move window to coord(%s), curses(%s)", box.coordinate, curses_coord)

    # def resize(self, box: BoundingBox):
    #     y, x = self.main_window._translate_local_coordinate_to_local_curses_coord(box.top_left)
    #     del self._local_window
    #     new_win = self.main_window.create_newwindow(box, False)
    #     self._local_window = new_win._local_window
    #     self.coordinate = new_win.coordinate
    #     self.dimensions = new_win.dimensions
    #     logger.info("New Window: %s", self)
    #     # self.indow = curses.newwin(box.height, box.width, y, x)

    def hline(self, coord: Coordinate, ch: str = None, length: int = None):
        if length is None:
            length = self.width
        if ch is None:
            ch = curses.ACS_HLINE
        self._local_window.hline(*self._translate_local_coordinate_to_local_curses_coord(coord), ch, length)

    def box(self):
        self._local_window.box()

    def __del__(self):
        for subwin in self.__children:
            del subwin

    def __repr__(self):
        return f"Window(x={self.x}, y={self.y}, width={self.width}, height={self.height})"

    def __str__(self):
        return self.__repr__()

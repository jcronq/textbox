from typing import Optional, Union
from collections import namedtuple

import curses
from curses import window

from adventurebox.box_types import Position, BoundingBox, Dimensions

import logging

logger = logging.getLogger()


class Window:
    def __init__(
        self,
        local_window: window,
        position: Optional[Position] = None,
        dimensions: Optional[Dimensions] = None,
        parent_window: Optional["Window"] = None,
    ):
        if parent_window is None and (position is not None or dimensions is not None):
            raise ValueError("Cannot specify position or dimensions without a parent window")
        self.__children = []
        self.position = position if position is not None else Position(0, 0)
        self.dimensions = dimensions if dimensions is not None else Dimensions(height=curses.LINES, width=curses.COLS)
        self._local_window = local_window
        self.__parent = parent_window

        # Validate bounding box of the window
        if self.__parent is not None:
            if not (self.bounding_box in self.__parent):
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
    def start_lineno(self):
        return self.position.lineno

    @property
    def start_colno(self):
        return self.position.colno

    @property
    def bounding_box(self):
        return BoundingBox(self.start_lineno, self.start_colno, self.height, self.width)

    @property
    def local_box(self):
        return BoundingBox(0, 0, self.height, self.width)

    @property
    def main_window(self):
        if self.__parent is None:
            return self
        return self.__parent.main_window

    @property
    def cursor_position(self) -> Position:
        return Position(*self._local_window.getyx())

    def create_new_window(self, box: BoundingBox, validate_input=True, verbose=False) -> "Window":
        if validate_input and not box in self:
            raise ValueError(f"New window {box} is not contained within {self.bounding_box}")

        if verbose:
            logger.info("Creating new window: %s", box)
        subwin = curses.newwin(*box.dimensions, *box.position)
        new_window = Window(subwin, box.position, box.dimensions, parent_window=self)
        self.__children.append(new_window)
        return new_window

    def refresh(self, verbose=False):
        self._local_window.refresh()

    def refresh_all(self, verbose=False):
        self._local_window.refresh()
        for subwin in self.__children:
            subwin.refresh()

    def erase(self, verbose=False):
        if verbose:
            logger.info("Erased window")
        self._local_window.erase()

    def addch(self, ch: str, position: Position = None, attributes: list = None, verbose=False):
        if type(ch) is not str:
            raise ValueError(f"ch must be a string, not {type(ch)}")
        if len(ch) != 1:
            raise ValueError(f"ch must be a single character, not {len(ch)}")
        if attributes is None:
            attributes = []
        if position is not None:
            if not position in self.local_box:
                raise ValueError(f"Position {position} is not contained within {self.bounding_box}")
            try:
                self._local_window.addch(*position, ch, *attributes)
            except curses.error:
                pass

        else:
            self._local_window.addch(str(ch))

    def addstr(self, text: str, position: Position = None, attributes: list = None, verbose=False):
        if attributes is None:
            attributes = []
        if position is None:
            if verbose:
                logger.info(f"Adding string at cursor_position")
            position = self.cursor_position
        str_box = BoundingBox(position.lineno, position.colno, height=1, width=len(text))
        if str_box not in self.local_box:
            raise ValueError(f"String '{text}':{str_box} @ {position} will not fit within {self.bounding_box}")
        if verbose:
            logger.info(f"Adding string at {position}")
        try:
            self._local_window.addstr(*position, text, *attributes)
        except curses.error:
            pass

    def getkey(self, verbose=False) -> str:
        return self._local_window.getkey()

    def getch(self, verbose=False) -> str:
        return self._local_window.getch()

    def move_cursor(self, position: Position, verbose=False):
        if not position in self.local_box:
            raise ValueError(f"Cursor Position {position} is not contained within {self.bounding_box}")

        if verbose:
            logger.info(f"Window: Moving cursor to {position}")
        self._local_window.move(*position)

    def resize(self, box: BoundingBox, verbose=False):
        if verbose:
            logger.info("Resizing window to %s", box)
        self.dimensions = box.dimensions
        self.position = box.position
        try:
            self._local_window.resize(*box.dimensions)
        except curses.error:
            raise ValueError("Failed to resize window to %s", box.dimensions)

        try:
            self._local_window.mvwin(*box.position)
        except curses.error:
            raise ValueError("Failed to move window to %s", box.position)

    def add_box(self, verbose=False):
        self._local_window.box()

    def __del__(self):
        for subwin in self.__children:
            del subwin

    def __repr__(self):
        return f"Window(x={self.start_lineno}, y={self.start_colno}, height={self.height}, width={self.width})"

    def __str__(self):
        return self.__repr__()

    def __contains__(self, other: Union[Position, BoundingBox, "Window"]):
        if isinstance(other, Position) or isinstance(other, BoundingBox):
            return other in self.bounding_box

        elif isinstance(other, Window):
            return other.bounding_box in self.bounding_box

        else:
            raise ValueError(f"Invalid type {type(other)}. Expected Position, BoundingBox, or Window.")

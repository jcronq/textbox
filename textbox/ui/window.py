from typing import Optional, Union
from collections import namedtuple

import curses
from curses import window

from textbox.utils.box_types import Position, BoundingBox, Dimensions

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
    def width(self) -> int:
        return self.dimensions.width

    @property
    def height(self) -> int:
        return self.dimensions.height

    @property
    def start_lineno(self) -> int:
        return self.position.lineno

    @property
    def start_colno(self) -> int:
        return self.position.colno

    @property
    def bounding_box(self) -> BoundingBox:
        return BoundingBox(self.start_lineno, self.start_colno, self.height, self.width)

    @property
    def local_box(self) -> BoundingBox:
        return BoundingBox(0, 0, self.height, self.width)

    @property
    def main_window(self) -> curses.window:
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

    def refresh(self, verbose=False) -> None:
        self._local_window.refresh()

    def refresh_all(self, verbose=False) -> None:
        self._local_window.refresh()
        for subwin in self.__children:
            subwin.refresh()

    def erase(self, verbose=False) -> None:
        if verbose:
            logger.info("Erased window")
        self._local_window.erase()

    def addch(self, ch: str, position: Position = None, attributes: list = None, verbose=False) -> None:
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
            except curses.error as e:
                # Log with context but don't raise - drawing at edge is expected
                logger.debug(
                    f"Failed to draw '{ch}' at ({position.lineno}, {position.colno}): {e}. "
                    f"Window size: {self.height}x{self.width}"
                )

        else:
            self._local_window.addch(str(ch))

    def addstr(self, text: str, position: Position = None, attributes: list = None, verbose=False) -> None:
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
        except curses.error as e:
            # Log with context but don't raise - drawing at edge is expected
            logger.debug(
                f"Failed to draw '{text}' at ({position.lineno}, {position.colno}): {e}. "
                f"Window size: {self.height}x{self.width}"
            )

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

    def resize(self, box: BoundingBox, verbose=False) -> None:
        """Resize window to new bounding box with validation.

        Args:
            box: New bounding box for the window
            verbose: Enable verbose logging

        Raises:
            ValueError: If dimensions are invalid or resize fails
        """
        # Validate dimensions before attempting resize
        if box.height <= 0 or box.width <= 0:
            raise ValueError(
                f"Window dimensions must be positive. "
                f"Got height={box.height}, width={box.width}. "
                f"Current size: {self.height}x{self.width}"
            )

        if box.height < 0:
            raise ValueError(
                f"Window height cannot be negative (got {box.height}). "
                f"Current height: {self.height}"
            )

        if box.width < 0:
            raise ValueError(
                f"Window width cannot be negative (got {box.width}). "
                f"Current width: {self.width}"
            )

        if verbose:
            logger.info("Resizing window from %dx%d to %s", self.height, self.width, box)

        try:
            self._local_window.resize(*box.dimensions)
        except curses.error as e:
            raise ValueError(
                f"Failed to resize window to {box.dimensions}: {e}"
            )

        try:
            self._local_window.mvwin(*box.position)
        except curses.error as e:
            raise ValueError(
                f"Failed to move window to {box.position}: {e}"
            )

        # Only update state after curses operations succeed
        self.dimensions = box.dimensions
        self.position = box.position

    def add_box(self, verbose=False):
        self._local_window.box()

    def cleanup(self) -> None:
        """Clean up window resources.

        Clears the window and releases references. Safe to call multiple times.
        Handles curses errors gracefully.
        """
        if self._local_window is None:
            return  # Already cleaned up

        try:
            self._local_window.clear()
        except (curses.error, AttributeError):
            # Window may already be destroyed or invalid
            pass

        # Note: We don't set _local_window to None to maintain compatibility
        # with property accessors that may still query dimensions

    def __del__(self):
        """Cleanup when object is garbage collected."""
        self.cleanup()
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

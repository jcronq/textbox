from curses import wrapper, window
import curses
import time


class Window:
    def __init__(self, stdscr: window, height: int = None, width: int = None):
        self.stdscr = stdscr
        if height is not None:
            self.height = height
        else:
            self.height = curses.LINES
        if width is not None:
            self.width = width
        else:
            self.width = curses.COLS
        self._subwindows = []

    def validate_coordinate(self, y: int, x: int):
        if y < 0 or x < 0:
            raise ValueError(f"y and x must be positive integers. Got y={y} and x={x}")
        if y >= self.height or x >= self.width:
            raise ValueError(f"y and x must be less than the height and width of the window. Got y={y} and x={x}")

    def subwin(self, height: int, width: int, y: int, x: int) -> window:
        self.validate_coordinate(y, x)
        subwin = self.stdscr.subwin(height, width, y, x)
        self._subwindows.append(subwin)
        return subwin

    def refresh(self):
        self.stdscr.refresh()
        for subwin in self._subwindows:
            subwin.refresh()

    def clear(self):
        self.stdscr.clear()
        for subwin in self._subwindows:
            subwin.clear()

    def addstr(self, y: int, x: int, text: str):
        self.validate_coordinate(y, x)
        self.stdscr.addstr(y, x, text)

    def getkey(self) -> str:
        return self.stdscr.getkey()

    def getch(self) -> str:
        return self.stdscr.getch()

    def getstr(self, y: int, x: int, n: int) -> str:
        return self.stdscr.getstr(y, x, n)

    def move(self, y: int, x: int):
        self.stdscr.move(y, x)

    def resize(self, height: int, width: int):
        self.addstr(0, 0, "Resizing...")
        self.stdscr.resize(height, width)

    def __del__(self):
        for subwin in self._subwindows:
            del subwin


class TextBox(Window):
    def __init__(self, stdscr: window, height: int, width: int):
        super().__init__(stdscr=stdscr, height=height, width=width)
        self.lines = []

    @property
    def cur_line(self):
        return len(self.lines) - 1

    def print(self, *args, end="\n", **kwargs):
        line = "".join([str(arg) for arg in args]) + end
        self.lines.append(line)
        self.addstr(self.cur_line, 0, line)
        self.refresh()


def main(stdscr: window):
    next_ch = 0
    box = TextBox(stdscr, curses.LINES, curses.COLS)
    box.print("Hel\nlo")
    while next_ch != "q":
        next_ch = box.getkey()
        box.print(f"{box.cur_line, next_ch}")


wrapper(main)

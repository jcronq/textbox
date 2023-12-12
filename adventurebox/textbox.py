from curses import window
from adventurebox.window import Window


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

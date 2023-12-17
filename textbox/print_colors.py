import time
import asyncio
import functools
import curses

import uvloop
import logging

from textbox.input_manager import AsyncInputManager
from textbox.window import Window
from textbox.input_box import InputBox
from textbox.box_types import BoundingBox, Coordinate
from textbox.signals import WindowQuit
from textbox.input_output_workspace import InputOutputWorkspace
from textbox.curses_utils import curses_wrapper

logger = logging.getLogger()
logger.addHandler(logging.FileHandler("log.txt"))
logger.setLevel(logging.INFO)


async def amain(window: Window):
    async with AsyncInputManager(window) as input_manager:
        try:
            for i in range(0, 255):
                window._local_window.addstr(str(i), curses.color_pair(i))
                window._local_window.addstr(" ", curses.color_pair(i))
        except Exception as e:
            logger.exception(e)
            input_manager.stop()
            raise e


@curses_wrapper
def main(stdscr: curses.window):
    window = Window(stdscr)
    asyncio.run(amain(window))


if __name__ == "__main__":
    uvloop.install()
    main()

import time
import asyncio
import functools
import curses

import uvloop
import logging

from adventurebox.input_manager import AsyncInputManager
from adventurebox.window import Window
from adventurebox.input_box import InputBox
from adventurebox.box_types import BoundingBox, Coordinate
from adventurebox.signals import WindowQuit
from adventurebox.adventure_input import VimLikeInputBox
from adventurebox.curses_utils import curses_wrapper

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

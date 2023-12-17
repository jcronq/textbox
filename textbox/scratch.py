import time
import asyncio
import functools
import curses

import uvloop
import logging

from textbox.input_manager import AsyncInputManager
from textbox.window import Window
from textbox.input_box import InputBox
from textbox.text_box import TextBox
from textbox.box_types import BoundingBox, Coordinate
from textbox.signals import WindowQuit
from textbox.adventure_input import VimLikeInputBox
from textbox.curses_utils import curses_wrapper
from textbox.color_code import ColorCode

logger = logging.getLogger()
logger.addHandler(logging.FileHandler("log.txt"))
logger.setLevel(logging.INFO)


async def amain(window: Window):
    async with AsyncInputManager(window) as input_manager:
        try:
            text_box = TextBox(
                window, BoundingBox(0, 0, window.width, window.height), ColorCode.WHITE  # , top_to_bottom=False
            )
            await asyncio.sleep(0.05)
            # text_box.add_str("H" * (81), end_line=True)
            # text_box.add_str("E" * int(window.width * 2))
            text_box.add_str("L", end_line=True)
            # text_box.add_str("H", end_line=True)
            # text_box.add_str("K", end_line=True)
            # text_box.add_str("H" * (window.width + 1), end_line=True)
            text_box.redraw()
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

import asyncio
import curses

from .window import Window
from .signals import WindowQuit, DelayedRedraw
import logging

logger = logging.getLogger()


class AsyncInputManager:
    def __init__(self, window: Window):
        self.window = window
        self.on_keypress = lambda x: None
        self.redraw = lambda: None
        self.running = False

    async def __aenter__(self, *args, **kwargs):
        self.window._local_window.nodelay(True)
        self.running = True
        self.input_future = asyncio.create_task(self.__async_input_loop())
        self.redraw_soon = False
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.debug("InputManager: Pending Exit")
        await self.input_future
        self.window._local_window.nodelay(False)
        logger.debug("InputManager: Complete")

    async def __async_input_loop(self):
        sleep_time = 0.015
        while self.running:
            try:
                key = self.window.getch()
                if self.redraw_soon:
                    self.redraw()
                    self.redraw_soon = False
                if key == curses.ERR:
                    await asyncio.sleep(sleep_time)
                else:
                    try:
                        await self.on_keypress(key)
                    except WindowQuit:
                        self.stop()
                    except DelayedRedraw:
                        self.redraw_soon = True

            except curses.error:
                await asyncio.sleep(sleep_time)

    def stop(self):
        self.running = False

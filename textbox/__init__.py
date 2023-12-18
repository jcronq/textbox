import asyncio
import curses
from typing import Callable, Union, List

import uvloop

from .signals import WindowQuit
from .window import Window
from .curses_utils import curses_wrapper
from .input_manager import AsyncInputManager
from .input_output_workspace import InputOutputWorkspace
from .input_box import InputBox
from .text_box import TextBox
from .text import Text
from .text_segment import TextSegment
from .text_line import TextLine
from .segmented_text_line import SegmentedTextLine
from .color_code import ColorCode

import logging

logger = logging.getLogger()


class App:
    def __init__(self):
        self._submit_callbacks = []
        self._user_defined_commands = {}
        self.workspace: InputOutputWorkspace = None

    def start(self):
        uvloop.install()

        @curses_wrapper
        def main(stdscr: curses.window):
            window = Window(stdscr)
            asyncio.run(self.run(window))

        main()

    async def run(self, window: Window):
        async with AsyncInputManager(window) as input_manager:
            try:
                await asyncio.sleep(0.05)
                self.workspace = InputOutputWorkspace(window, input_manager)
                self.workspace.set_submit_callback(self._submit_callback)
                self.workspace.set_command_callback(self._command_callback)
                self.workspace.enter_insert_mode()
                window.refresh()
                self.workspace.focused_box.refresh()

            except Exception as e:
                logger.exception(e)
                input_manager.stop()
                raise e
        self.workspace = None

    def _submit_callback(self, text: str):
        for func in self._submit_callbacks:
            func(text)

    def _command_callback(self, command: str):
        if command in self._user_defined_commands:
            self._user_defined_commands[command](command)
        else:
            self.print(f"Unknown command: {command}")

    def on_submit(self, func: Callable[[str], None]):
        self._submit_callbacks.append(func)
        return func

    def print(self, text: Union[str, Text, List[SegmentedTextLine]], end="\n"):
        if self.workspace.output_bounding_box is None:
            raise ValueError("The application is not running.")
        if isinstance(text, str):
            self.workspace.output_box.add_str(text)
        elif isinstance(text, Text):
            self.workspace.output_box.add_text(text)
        elif isinstance(text, SegmentedTextLine):
            raise NotImplementedError("SegmentedTextLine is not implemented yet.")
            # self.workspace.output_box.add_segmented_text_line(text)
        elif isinstance(text, list):
            if all([isinstance(line, SegmentedTextLine) for line in text]):
                for line in text:
                    self.workspace.output_box.add_segmented_text_line(line)
            else:
                raise ValueError("List must contain only SegmentedTextLines")
        else:
            raise ValueError(f"Cannot print {type(text)}")

        if end == "\n":
            self.workspace.output_box.end_current_text()

    def command(self, name: str):
        def decorator(func):
            self._user_defined_commands[name] = func
            return func

        return decorator

    def stop(self):
        raise WindowQuit()


__all__ = ["App", "Text", "InputBox", "TextBox", "TextSegment", "TextLine", "ColorCode"]

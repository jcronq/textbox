import asyncio
import curses
from typing import Callable, Union, List, Optional

from .utils.signals import WindowQuit
from .ui.window import Window
from .utils.curses_utils import curses_wrapper
from .ui.input_manager import AsyncInputManager
from .ui.workspace import InputOutputWorkspace
from .ui.input_box import InputBox
from .ui.text_box import TextBox
from .core.text import Text
from .core.text_segment import TextSegment
from .core.text_line import TextLine
from .core.segmented_text_line import SegmentedTextLine
from .utils.color_code import ColorCode
from .utils.debug import DebugOverlay, setup_debug_logging

import logging

logger = logging.getLogger()


class App:
    def __init__(self, debug: bool = False) -> None:
        """Initialize the App.

        Args:
            debug: Enable debug mode with overlay and enhanced logging
        """
        self._submit_callbacks = []
        self._user_defined_commands = {"help": self._default_help}
        self._user_defined_commands_help = {"help": "Print this help message."}
        self.workspace: InputOutputWorkspace = None
        self.debug = debug
        self.debug_overlay: Optional[DebugOverlay] = None
        self.debug_logger: Optional[logging.Logger] = None

        if debug:
            self._setup_debug_mode()

    def start(self) -> None:
        @curses_wrapper
        def main(stdscr: curses.window):
            window = Window(stdscr)
            asyncio.run(self.run(window))

        main()

    async def astart(self) -> None:
        @curses_wrapper
        async def main(stdscr: curses.window):
            window = Window(stdscr)
            await self.run(window)

        await main()

    async def run(self, window: Window) -> None:
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

    def _submit_callback(self, text: Text) -> None:
        for func in self._submit_callbacks:
            func(text)

    def _command_callback(self, command_str: str) -> None:
        command = command_str.split(" ")[0]
        if command in self._user_defined_commands:
            self._user_defined_commands[command](command_str)
        else:
            self.print(f"Unknown command: {command}")

    def on_submit(self, func: Callable[[Text], None]) -> Callable[[Text], None]:
        self._submit_callbacks.append(func)
        return func

    def print(self, text: Union[str, Text, List[SegmentedTextLine]], end="\n"):
        if self.workspace.output_bounding_box is None:
            raise ValueError("The application is not running.")
        if isinstance(text, str):
            self.workspace.output_box.add_str(text)
        elif isinstance(text, Text):
            self.workspace.output_box.add_text(text)
        elif isinstance(text, list):
            if all([isinstance(line, SegmentedTextLine) for line in text]):
                for line in text:
                    self.workspace.output_box.add_segmented_text_line(line)
            elif all((isinstance(line, SegmentedTextLine) for line in text)):
                self.workspace.output_box.add_text(Text([TextLine(line) for line in text]))
            elif all((isinstance(line, TextLine) for line in text)):
                self.workspace.output_box.add_text(Text(text))
            else:
                raise ValueError("List must contain only SegmentedTextLines")
        else:
            raise ValueError(f"Cannot print {type(text)}")

        if end == "\n":
            self.workspace.output_box.end_current_text()

    def command(self, name: str, *alt_names, help: str = None) -> Callable:
        def decorator(func):
            self._user_defined_commands[name] = func
            for alt_name in alt_names:
                self._user_defined_commands[alt_name] = func
            self._user_defined_commands_help[name] = help
            return func

        return decorator

    def _default_help(self, command_str: str) -> None:
        self.print("Commands:")
        for command, help in self._user_defined_commands_help.items():
            self.print(f"  {command}: {help}")

    def stop(self) -> None:
        raise WindowQuit()

    def _setup_debug_mode(self) -> None:
        """Setup debug mode with overlay and enhanced logging."""
        self.debug_overlay = DebugOverlay(enabled=True)
        self.debug_logger = setup_debug_logging()
        self.debug_logger.info("Debug mode enabled")


__all__ = ["App", "Text", "InputBox", "TextBox", "TextSegment", "TextLine", "ColorCode"]

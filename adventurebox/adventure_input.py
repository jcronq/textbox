import curses
from enum import Enum


from adventurebox.window import Window
from adventurebox.input_manager import AsyncInputManager
from adventurebox.input_box import InputBox
from adventurebox.box_types import BoundingBox
from adventurebox.signals import WindowQuit
from adventurebox.box_types import Coordinate

import logging

logger = logging.getLogger()


class INPUT_MODE(Enum):
    INSERT = 0
    REPLACE = 1
    COMMAND = 2
    COMMAND_ENTRY = 3


class VimLikeInputBox:
    def __init__(self, main_window: Window, input_manager: AsyncInputManager):
        self.text_box = InputBox(main_window, BoundingBox(0, 1, main_window.width, 3))
        self.command_box = InputBox(main_window, BoundingBox(0, 0, main_window.width, 1))

        self.focused_box: InputBox = self.text_box
        self.input_mode = INPUT_MODE.COMMAND

    def enter_replace_mode(self):
        self.input_mode = INPUT_MODE.REPLACE
        self.focused_box = self.text_box
        self.command_box.set_text("-- REPLACE --")
        logger.info("Input Mode: REPLACE")
        self.focused_box.refresh()

    def enter_insert_mode(self):
        self.input_mode = INPUT_MODE.INSERT
        self.focused_box = self.text_box
        self.command_box.set_text("-- INSERT --")
        logger.info("Input Mode: INSERT")
        self.focused_box.refresh()

    def enter_command_mode(self):
        self.input_mode = INPUT_MODE.COMMAND
        self.command_box.set_text("")
        self.focused_box = self.text_box
        logger.info("Input Mode: COMMAND")
        self.focused_box.refresh()

    def enter_command_entry_mode(self):
        self.input_mode = INPUT_MODE.COMMAND_ENTRY
        self.focused_box = self.command_box
        self.command_box.set_text(":")
        logger.info("Input Mode: COMMAND_ENTRY")
        self.focused_box.refresh()

    def handle_keypress(self, key: int):
        if self.input_mode == INPUT_MODE.COMMAND:
            self.command_handler(key)
        elif self.input_mode == INPUT_MODE.INSERT:
            self.text_handler(key)
        elif self.input_mode == INPUT_MODE.REPLACE:
            self.text_handler(key)
        elif self.input_mode == INPUT_MODE.COMMAND_ENTRY:
            self.command_entry_handler(key)

    def _handle_history_scroll_up(self):
        if not self._history.has_history():
            logger.info("Key: Up (No History)")
            return
        elif self._history.at_present():
            logger.info("Key: Up (History) - First Press")
            self._history.set_short_term_memory(self.text)
        else:
            logger.info("Key: Up (History) - Press")
        self._set_text(self._history.previous())

    def _handle_history_scroll_down(self):
        if self._history.at_present():
            logger.info("Key: Down (History) - No further history")
            return
        else:
            logger.info("Key: Down (History) - Press")
            self._set_text(self._history.next())

    def submit(self):
        if len(self.focused_box.text) > 0:
            self.focused_box.append_history()
        self.on_submit(self.focused_box.text)
        self.focused_box.clear_text()

    def execute_command(self, text):
        match text:
            case "q":
                raise WindowQuit()
            case _:
                pass

    def text_handler(self, key: int):
        logger.debug("text_handler.key_pressed: %s", chr(key))
        if key == curses.KEY_UP:
            logger.info("Key: Up")
            self.focused_box.cursor_up()

        elif key == curses.KEY_DOWN:
            logger.info("Key: Down")
            self.focused_box.cursor_down()

        elif key == curses.KEY_LEFT:
            logger.info("Key: Left")
            self.focused_box.cursor_left()

        elif key == curses.KEY_RIGHT:
            logger.info("Key: Right")
            self.focused_box.cursor_right()

        elif key == 27:
            logger.info("Key: Escape")
            self.enter_command_mode()

        elif key == ord("\n") or key == ord("\r"):
            logger.info("Key: Enter")
            self.submit()

        elif key == curses.KEY_BACKSPACE or key == 127:  # 127 is the delete key.  Macs use delete instead of backspace.
            self.focused_box.handle_backspace()

        else:
            logger.info("key: %s", chr(key))
            if self.input_mode == INPUT_MODE.REPLACE:
                self.focused_box.replace_character_at_cursor(chr(key))
            else:
                self.focused_box.insert_character_at_cursor(chr(key))

    def command_handler(self, key: int):
        logger.debug("command_handler.key_pressed: %s", chr(key))
        if key == curses.KEY_UP:
            logger.info("Command: Up")
            self.focused_box.history_scroll_up()

        elif key == curses.KEY_DOWN:
            logger.info("Key: Down")
            self.focused_box.history_scroll_down()

        elif key == ord("j"):
            self.focused_box.cursor_down()

        elif key == ord("k"):
            self.focused_box.cursor_up()

        elif key == ord("h"):
            logger.info("Command: h")
            self.focused_box.cursor_left()

        elif key == ord("l"):
            logger.info("Command: l")
            self.focused_box.cursor_right()

        elif key == ord("i"):
            logger.info("Command: i")
            self.enter_insert_mode()
            logger.info("Input Mode: %s", self.input_mode)

        elif key == ord("R"):
            logger.info("Command: R")
            self.enter_replace_mode()
            logger.info("Input Mode: %s", self.input_mode)

        elif key == ord("x"):
            logger.info("Command: x")
            self.focused_box.handle_backspace()

        elif key == ord(":"):
            logger.info("Command: :")
            self.enter_command_entry_mode()

        elif key in [27]:
            logger.info("Command: Escape")

    def command_entry_handler(self, key: int):
        logger.debug("command_entry_handler.key_pressed: %s", chr(key))
        if key == curses.KEY_UP:
            logger.info("Command: Up")
            self.focused_box.history_scroll_up()

        elif key == curses.KEY_DOWN:
            logger.info("Key: Down")
            self.focused_box.history_scroll_down()

        elif key in [27]:
            logger.info("Command: Escape")
            self.enter_command_mode()

        elif key in [ord("\n"), ord("\r")]:
            logger.info("Command: Enter")
            if len(self.command_box.text) > 0:
                self.command_box.append_history()
            self.execute_command(self.command_box.text[1:])
            self.enter_command_mode()

        else:
            self.text_handler(key)

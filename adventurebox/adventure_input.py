import curses
from enum import Enum


from adventurebox.window import Window
from adventurebox.input_manager import AsyncInputManager
from adventurebox.input_box import InputBox
from adventurebox.text_box import TextBox
from adventurebox.box_types import BoundingBox, Coordinate
from adventurebox.signals import WindowQuit
from adventurebox.color_code import ColorCode

import logging

logger = logging.getLogger()


class INPUT_MODE(Enum):
    INSERT = 0
    REPLACE = 1
    COMMAND = 2
    COMMAND_ENTRY = 3


class VimLikeInputBox:
    def __init__(self, main_window: Window, input_manager: AsyncInputManager):
        self.command_box = InputBox(
            "command_box",
            main_window,
            BoundingBox(0, 0, main_window.width, 1),
            ColorCode.GREY,
            top_to_bottom=True,
        )
        self.user_box = InputBox(
            "user_box",
            main_window,
            BoundingBox(0, 1, main_window.width, 4),
            ColorCode.WHITE,
            top_to_bottom=True,
            has_box=True,
        )
        self.output_box = TextBox(
            "output_box",
            main_window,
            BoundingBox(0, 4, main_window.width, main_window.height - 4),
            ColorCode.OUPTUT_TEXT,
            top_to_bottom=False,
            has_box=True,
        )
        self.output_box.box_visible = True

        self._focused_box: TextBox = self.user_box
        self.input_mode = INPUT_MODE.COMMAND
        input_manager.on_keypress = self.handle_keypress

    @property
    def focused_box(self):
        return self._focused_box

    @focused_box.setter
    def focused_box(self, value: TextBox):
        self._focused_box.box_visible = False
        self._focused_box = value
        self._focused_box.box_visible = True

    def cycle_focus(self):
        if self.focused_box == self.user_box:
            self.focused_box = self.command_box
        elif self.focused_box == self.command_box:
            self.focused_box = self.user_box

    def enter_replace_mode(self):
        self.input_mode = INPUT_MODE.REPLACE
        self.focused_box = self.user_box
        self.command_box.set_text("-- REPLACE --")
        logger.info("Input Mode: REPLACE")
        self.focused_box.refresh()

    def enter_insert_mode(self, append: bool = False):
        self.focused_box = self.user_box
        # if append and self.input_mode != INPUT_MODE.INSERT:
        self.focused_box.column_ptr += 1
        self.focused_box.window.move(self.focused_box.cursor_coord)
        self.focused_box.window.refresh()
        self.input_mode = INPUT_MODE.INSERT
        self.command_box.set_text("-- INSERT --")
        logger.info("Input Mode: INSERT")
        self.focused_box.refresh()

    def enter_command_mode(self):
        if self.input_mode == INPUT_MODE.INSERT:
            self.focused_box.column_ptr -= 1
            self.focused_box.window.move(self.focused_box.cursor_coord)
            self.focused_box.window.refresh()
        self.input_mode = INPUT_MODE.COMMAND
        self.command_box.set_text("")
        self.focused_box = self.user_box
        logger.info("Input Mode: COMMAND")
        self.focused_box.refresh()

    def enter_command_entry_mode(self):
        self.input_mode = INPUT_MODE.COMMAND_ENTRY
        self.focused_box = self.command_box
        self.command_box.add_str(":")
        logger.info("Input Mode: COMMAND_ENTRY")
        self.focused_box.redraw()

    def handle_keypress(self, key: int):
        if self.input_mode == INPUT_MODE.COMMAND:
            self.command_handler(key)
        elif self.input_mode == INPUT_MODE.INSERT:
            self.text_handler(key)
        elif self.input_mode == INPUT_MODE.REPLACE:
            self.text_handler(key)
        elif self.input_mode == INPUT_MODE.COMMAND_ENTRY:
            self.command_entry_handler(key)

    def submit(self):
        self.focused_box: InputBox
        if len(self.focused_box.text) > 0:
            self.focused_box.append_history()
            self.output_box.print_line(self.focused_box.text)
            self.focused_box.clear()
            self.focused_box.redraw(with_cursor=True)

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
            logger.info("Command: j (cursor down)")
            self.focused_box.cursor_down()

        elif key == ord("k"):
            logger.info("Command: k (cursor up)")
            self.focused_box.cursor_up()

        elif key == ord("h"):
            logger.info("Command: h (cursor left)")
            self.focused_box.cursor_left()

        elif key == ord("l"):
            logger.info("Command: l (cursor right)")
            self.focused_box.cursor_right()

        elif key == ord("a"):
            logger.info("Command: i")
            self.enter_insert_mode(append=True)
            logger.info("Input Mode: %s", self.input_mode)

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

        elif key == ord("\n") or key == ord("\r"):
            logger.info("Key: Enter")
            self.submit()

        elif key in [27]:
            logger.info("Command: Escape (nop)")

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

import asyncio
import curses
from enum import Enum


from adventurebox.window import Window
from adventurebox.input_manager import AsyncInputManager
from adventurebox.input_box import InputBox
from adventurebox.text_box import TextBox
from adventurebox.box_types import BoundingBox, Dimensions
from adventurebox.signals import WindowQuit, DelayedRedraw
from adventurebox.color_code import ColorCode

import logging

logger = logging.getLogger()


class INPUT_MODE(Enum):
    INSERT = 0
    REPLACE = 1
    COMMAND = 2
    COMMAND_ENTRY = 3
    READ_ONLY = 4


class VimLikeInputBox:
    def __init__(self, main_window: Window, input_manager: AsyncInputManager):
        self.main_window = main_window
        self.command_box_height = 1
        self.user_box_height = 5
        self.command_box = InputBox(
            "command_box",
            main_window,
            BoundingBox(
                main_window.height - self.command_box_height,
                0,
                self.command_box_height,
                main_window.width,
            ),
            ColorCode.GREY,
            top_to_bottom=True,
        )
        logger.info("command_box: %s", self.command_box)
        self.user_box = InputBox(
            "user_box",
            main_window,
            BoundingBox(
                main_window.height - self.command_box.height - self.user_box_height,
                0,
                height=self.user_box_height,
                width=main_window.width,
            ),
            ColorCode.WHITE,
            top_to_bottom=True,
            has_box=True,
        )
        self.output_box = TextBox(
            "output_box",
            main_window,
            BoundingBox(
                0,
                0,
                height=main_window.height
                - self.user_box.height
                - self.command_box.height
                + 1,  # +1 for overlapping the box space with user_box
                width=main_window.width,
            ),
            ColorCode.OUPTUT_TEXT,
            top_to_bottom=False,
            has_box=True,
        )

        self._focused_box: TextBox = self.user_box
        self.input_mode = INPUT_MODE.COMMAND
        input_manager.on_keypress = self.handle_keypress
        input_manager.redraw = self.redraw

    async def resize(self):
        logger.info("Event: Resize")
        curses.update_lines_cols()
        curses.resize_term(curses.LINES, curses.COLS)
        self.main_window.resize(BoundingBox(0, 0, curses.COLS, curses.LINES))
        self.command_box.resize(BoundingBox(0, 0, self.main_window.width, 1))
        self.user_box.resize(BoundingBox(0, 1, self.main_window.width, self.input_box_height))
        self.output_box.resize(
            BoundingBox(0, 4, self.main_window.width, self.main_window.height - self.input_box_height)
        )
        raise DelayedRedraw()

    def redraw(self):
        logger.info("redraw")
        self.command_box.redraw()
        self.user_box.redraw()
        self.output_box.redraw()
        self.focused_box.redraw()

    @property
    def focused_box(self):
        return self._focused_box

    @focused_box.setter
    def focused_box(self, box_to_focus: TextBox):
        if box_to_focus != self.command_box:
            self._focused_box.box_visible = False
            self.focused_box.redraw()
            self._focused_box = box_to_focus
            self._focused_box.box_visible = True
        else:
            self._focused_box = box_to_focus

    def cycle_focus(self):
        if self.focused_box == self.user_box:
            self.enter_reading_mode()
        elif self.focused_box == self.output_box:
            self.enter_command_mode()

    def enter_reading_mode(self):
        logger.info("Input Mode: READ_ONLY")
        self.input_mode = INPUT_MODE.READ_ONLY
        self.focused_box = self.output_box
        self.command_box.set_text_to_str("-- READING --")
        self.focused_box.refresh()

    def enter_replace_mode(self):
        self.input_mode = INPUT_MODE.REPLACE
        self.focused_box = self.user_box
        self.command_box.set_text_to_str("-- REPLACE --")
        logger.info("Input Mode: REPLACE")
        self.focused_box.refresh()

    def enter_insert_mode(self, append: bool = False):
        self.focused_box = self.user_box
        self.focused_box.text.edit_mode = True
        if append and self.input_mode != INPUT_MODE.INSERT:
            self.focused_box.text.increment_column_ptr()
        self.focused_box.update_cursor()
        self.input_mode = INPUT_MODE.INSERT
        self.command_box.set_text_to_str("-- INSERT --")
        logger.info("Input Mode: INSERT")
        self.focused_box.refresh()

    def enter_command_mode(self):
        self.input_mode = INPUT_MODE.COMMAND
        self.command_box.set_text_to_str("")
        if self.focused_box != self.user_box:
            self.focused_box = self.user_box
        self.focused_box.text.edit_mode = False
        logger.info("Input Mode: COMMAND")
        self.focused_box.redraw(with_cursor=True)

    def enter_command_entry_mode(self):
        self.input_mode = INPUT_MODE.COMMAND_ENTRY
        self.focused_box = self.command_box
        self.command_box.set_text_to_str(":")
        self.focused_box.text.edit_mode = True
        self.focused_box.text.increment_column_ptr()
        logger.info("Input Mode: COMMAND_ENTRY")
        self.focused_box.redraw()

    async def handle_keypress(self, key: int):
        if key == curses.KEY_RESIZE:
            await self.resize()
        elif self.input_mode == INPUT_MODE.COMMAND:
            self.command_handler(key)
        elif self.input_mode == INPUT_MODE.INSERT:
            self.text_handler(key)
        elif self.input_mode == INPUT_MODE.REPLACE:
            self.text_handler(key)
        elif self.input_mode == INPUT_MODE.COMMAND_ENTRY:
            self.command_entry_handler(key)
        elif self.input_mode == INPUT_MODE.READ_ONLY:
            self.read_only_handler(key)

    def submit(self, print=True):
        logger.info("Submit(print=%s)", print)
        self.focused_box: InputBox
        if len(self.focused_box.text) > 0:
            logger.info("appending history")
            self.focused_box.append_history()
            if print:
                logger.info("Adding text to output box")
                self.output_box.add_text(self.focused_box.text.copy())
            logger.info("Erasing entry box")
            self.focused_box.text.erase()
            logger.info("Redrawing screen")
            self.focused_box.redraw(with_cursor=True)

    def execute_command(self, text):
        logger.info(f"Command: {text}")
        match text:
            case "q":
                raise WindowQuit()
            case _:
                pass

    def read_only_handler(self, key: int):
        if key == ord("\t"):
            logger.info("Command: Tab")
            self.cycle_focus()

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

        # elif key == ord("\n") or key == ord("\r"):
        #     logger.info("Key: Enter")
        #     self.submit()

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

        elif key == ord("\t"):
            logger.info("Command: Tab")
            self.cycle_focus()

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

        elif key == ord("b"):
            logger.info("Command: b (word backward)")
            self.focused_box.word_backward()

        elif key == ord("w"):
            logger.info("Command: w (word forward)")
            self.focused_box.word_forward()

        elif key == ord("$"):
            logger.info("Command: $ (end of line)")
            self.focused_box.end_of_line()

        elif key == ord("0"):
            logger.info("Command: 0 (start of line)")
            self.focused_box.start_of_line()

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
            self.execute_command(str(self.command_box.text)[1:])
            self.submit(print=False)
            self.enter_command_mode()

        else:
            self.text_handler(key)

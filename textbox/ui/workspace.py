import curses
from enum import Enum
from typing import Callable

from textbox.ui.window import Window
from textbox.ui.input_manager import AsyncInputManager
from textbox.ui.input_box import InputBox
from textbox.ui.text_box import TextBox
from textbox.core.text import Text
from textbox.core.commands import (
    CommandHistory,
    DeleteCharCommand,
    DeleteLineCommand,
    InsertLineBelowCommand,
    InsertLineAboveCommand,
    ChangeToEndOfLineCommand,
    DeleteToEndOfLineCommand,
    JoinLinesCommand,
    PasteAfterCommand,
    PasteBeforeCommand,
)
from textbox.utils.box_types import BoundingBox
from textbox.utils.signals import WindowQuit, DelayedRedraw
from textbox.utils.color_code import ColorCode
from textbox.utils.registers import RegisterManager

import logging

logger = logging.getLogger("textbox")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("textbox.log")
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class INPUT_MODE(Enum):
    INSERT = 0
    REPLACE = 1
    COMMAND = 2
    COMMAND_ENTRY = 3
    READ_ONLY = 4
    VISUAL = 5
    VISUAL_LINE = 6


class InputOutputWorkspace:
    def __init__(self, main_window: Window, input_manager: AsyncInputManager):
        self.main_window = main_window
        self.command_box_height = 1
        self.user_box_height = 5
        self.command_box = InputBox(
            "command_box", main_window, self.command_bounding_box, ColorCode.GREY, top_to_bottom=True
        )

        logger.info("command_box: %s", self.command_box)

        self.user_box = InputBox(
            "user_box", main_window, self.user_bounding_box, ColorCode.WHITE, top_to_bottom=True, has_box=True
        )
        self.output_box = TextBox(
            "output_box",
            main_window,
            self.output_bounding_box,
            ColorCode.OUPTUT_TEXT,
            top_to_bottom=False,
            has_box=True,
        )
        self._submit_callback = None
        self._command_callback = None
        # self.output_box.verbose = True

        self._focused_box: TextBox = self.user_box
        self.input_mode = INPUT_MODE.COMMAND
        self.register_manager = RegisterManager()  # Vim-style registers for copy/paste
        self.command_history = CommandHistory()  # Undo/redo history
        self._pending_register = None  # Register name specified by " prefix
        self._last_command_key = None  # Track last key for double-key commands (dd, yy, cc, etc)
        input_manager.on_keypress = self.handle_keypress
        input_manager.redraw = self.redraw

    def set_submit_callback(self, func: Callable[[Text], None]):
        self._submit_callback = func

    def set_command_callback(self, func: Callable[[str], None]):
        self._command_callback = func

    @property
    def command_bounding_box(self):
        return BoundingBox(
            self.main_window.height - self.command_box_height,
            0,
            self.command_box_height,
            self.main_window.width,
        )

    @property
    def user_bounding_box(self):
        return BoundingBox(
            self.main_window.height - self.command_box.height - self.user_box_height,
            0,
            height=self.user_box_height,
            width=self.main_window.width,
        )

    @property
    def output_bounding_box(self):
        return BoundingBox(
            0,
            0,
            height=self.main_window.height
            - self.user_box.height
            - self.command_box.height
            + 1,  # +1 for overlapping the box space with user_box
            width=self.main_window.width,
        )

    async def resize(self) -> None:
        logger.info("Event: Resize")
        curses.update_lines_cols()
        curses.resize_term(curses.LINES, curses.COLS)
        self.main_window.resize(BoundingBox(0, 0, curses.LINES, curses.COLS))
        self.command_box.resize(self.command_bounding_box)
        self.user_box.resize(self.user_bounding_box)
        self.output_box.resize(self.output_bounding_box)
        raise DelayedRedraw()

    def redraw(self):
        logger.info("Redraw All Boxes")
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
        curses.curs_set(0)
        self.focused_box.refresh()

    def enter_replace_mode(self) -> None:
        curses.curs_set(1)
        self.input_mode = INPUT_MODE.REPLACE
        self.focused_box = self.user_box
        self.command_box.set_text_to_str("-- REPLACE --")
        logger.info("Input Mode: REPLACE")
        self.focused_box.refresh()

    def enter_insert_mode(self, append: bool = False):
        curses.curs_set(1)
        self.focused_box = self.user_box
        self.focused_box.text.edit_mode = True
        if append and self.input_mode != INPUT_MODE.INSERT:
            self.focused_box.text.increment_column_ptr()
        self.focused_box.update_cursor()
        self.input_mode = INPUT_MODE.INSERT
        self.command_box.set_text_to_str("-- INSERT --")
        logger.info("Input Mode: INSERT")
        self.focused_box.refresh()

    def enter_command_mode(self) -> None:
        curses.curs_set(1)
        self.input_mode = INPUT_MODE.COMMAND
        self.command_box.set_text_to_str("")
        if self.focused_box != self.user_box:
            self.focused_box = self.user_box
        self.focused_box.text.edit_mode = False
        self.command_box.set_text_to_str("-- COMMAND --")
        logger.info("Input Mode: COMMAND")
        self.focused_box.redraw(with_cursor=True)

    def enter_command_entry_mode(self):
        curses.curs_set(2)
        self.input_mode = INPUT_MODE.COMMAND_ENTRY
        self.focused_box = self.command_box
        self.command_box.set_text_to_str(":")
        self.focused_box.text.edit_mode = True
        self.focused_box.text.increment_column_ptr()
        logger.info("Input Mode: COMMAND_ENTRY")
        self.focused_box.redraw()

    def enter_visual_mode(self) -> None:
        """Enter VISUAL mode (character-wise selection)."""
        curses.curs_set(1)
        self.input_mode = INPUT_MODE.VISUAL
        self.focused_box = self.user_box
        self.focused_box.text.edit_mode = False
        self.focused_box.text.start_selection()
        self.command_box.set_text_to_str("-- VISUAL --")
        logger.info("Input Mode: VISUAL")
        self.focused_box.redraw(with_cursor=True)

    def enter_visual_line_mode(self) -> None:
        """Enter VISUAL LINE mode (line-wise selection)."""
        curses.curs_set(1)
        self.input_mode = INPUT_MODE.VISUAL_LINE
        self.focused_box = self.user_box
        self.focused_box.text.edit_mode = False
        self.focused_box.text.start_selection()
        self.command_box.set_text_to_str("-- VISUAL LINE --")
        logger.info("Input Mode: VISUAL_LINE")
        self.focused_box.redraw(with_cursor=True)

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
        elif self.input_mode == INPUT_MODE.VISUAL:
            self.visual_mode_handler(key)
        elif self.input_mode == INPUT_MODE.VISUAL_LINE:
            self.visual_line_mode_handler(key)

    def submit(self):
        logger.info("Submit(print=%s)", print)
        self.focused_box: InputBox
        if len(self.focused_box.text) > 0:
            self.focused_box.append_history()
            if self._submit_callback is not None:
                self._submit_callback(self.focused_box.text.copy())
            logger.info("Erasing entry box")
            self.focused_box.text.erase()
            logger.info("Redrawing screen")
            self.focused_box.redraw(with_cursor=True)

    def submit_command(self):
        logger.info("Submit_command")
        self.focused_box: InputBox
        if len(self.focused_box.text) > 0:
            self.focused_box.append_history()
            logger.info("Erasing entry box")
            self.focused_box.text.erase()
            logger.info("Redrawing screen")
            self.focused_box.redraw(with_cursor=True)

    def execute_command(self, text):
        logger.info(f"Command: {text}")
        text = text.strip()
        command = text.split(" ")[0]
        match command:
            case "q":
                raise WindowQuit()
            case _:
                if self._command_callback is not None:
                    self._command_callback(text)

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

        elif key == ord("\n") or key == ord("\r"):
            logger.info("Key: Enter")
            self.submit()

        elif key == ord("\t"):
            logger.info("Command: Tab")
            self.cycle_focus()

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

        # Handle register prefix first
        if self._pending_register is True:
            # The previous key was ", this key is the register name
            register_char = chr(key)
            if register_char in "abcdefghijklmnopqrstuvwxyz0123456789\"":
                self._pending_register = register_char
                logger.info(f"Register selected: {register_char}")
                return
            else:
                # Invalid register, reset
                logger.warning(f"Invalid register: {register_char}")
                self._pending_register = None
                return

        # Handle double-key commands (dd, yy, cc)
        if key == ord("d") and self._last_command_key == ord("d"):
            logger.info("Command: dd (delete line)")
            # Use Command pattern for undo/redo support
            cmd = DeleteLineCommand(self.focused_box.text)
            self.command_history.execute_command(cmd)
            # Store deleted text in register
            deleted = cmd.deleted_line
            self.register_manager.delete_to_register(self._pending_register, deleted)
            self._pending_register = None
            self.focused_box.redraw(with_cursor=True)
            self._last_command_key = None
            return

        elif key == ord("y") and self._last_command_key == ord("y"):
            logger.info("Command: yy (yank line)")
            yanked = self.focused_box.text.get_current_line()
            self.register_manager.yank_to_register(self._pending_register, yanked)
            self._pending_register = None
            self.focused_box.redraw(with_cursor=True)
            self._last_command_key = None
            return

        elif key == ord("c") and self._last_command_key == ord("c"):
            logger.info("Command: cc (change line)")
            # Use Command pattern for undo/redo support
            cmd = DeleteLineCommand(self.focused_box.text)
            self.command_history.execute_command(cmd)
            # Store deleted text in register
            deleted = cmd.deleted_line
            self.register_manager.delete_to_register(self._pending_register, deleted)
            self._pending_register = None
            self.enter_insert_mode()
            self._last_command_key = None
            return

        # Reset last command key if different key pressed
        if key != self._last_command_key:
            self._last_command_key = None

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
            logger.info("Command: a (append)")
            self.enter_insert_mode(append=True)
            logger.info("Input Mode: %s", self.input_mode)

        elif key == ord("A"):
            logger.info("Command: A (append at end of line)")
            self.focused_box.text.to_end_of_line()
            self.enter_insert_mode(append=True)
            logger.info("Input Mode: %s", self.input_mode)

        elif key == ord("i"):
            logger.info("Command: i (insert)")
            self.enter_insert_mode()
            logger.info("Input Mode: %s", self.input_mode)

        elif key == ord("I"):
            logger.info("Command: I (insert at beginning of line)")
            self.focused_box.text.to_start_of_line()
            self.enter_insert_mode()
            logger.info("Input Mode: %s", self.input_mode)

        elif key == ord("o"):
            logger.info("Command: o (open line below)")
            # Use Command pattern for undo/redo support
            cmd = InsertLineBelowCommand(self.focused_box.text)
            self.command_history.execute_command(cmd)
            self.enter_insert_mode()
            logger.info("Input Mode: %s", self.input_mode)

        elif key == ord("O"):
            logger.info("Command: O (open line above)")
            # Use Command pattern for undo/redo support
            cmd = InsertLineAboveCommand(self.focused_box.text)
            self.command_history.execute_command(cmd)
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
            logger.info("Command: R (replace mode)")
            self.enter_replace_mode()
            logger.info("Input Mode: %s", self.input_mode)

        elif key == ord("x"):
            logger.info("Command: x (delete char)")
            # Use command pattern for undo/redo support
            cmd = DeleteCharCommand(self.focused_box.text)
            self.command_history.execute_command(cmd)
            self.focused_box.redraw(with_cursor=True)

        elif key == ord("u"):
            logger.info("Command: u (undo)")
            if self.command_history.undo():
                self.focused_box.redraw(with_cursor=True)
                self.command_box.set_text_to_str("Undone")
            else:
                logger.debug("Nothing to undo")
                self.command_box.set_text_to_str("Already at oldest change")

        elif key == 18:  # Ctrl-r
            logger.info("Command: Ctrl-r (redo)")
            if self.command_history.redo():
                self.focused_box.redraw(with_cursor=True)
                self.command_box.set_text_to_str("Redone")
            else:
                logger.debug("Nothing to redo")
                self.command_box.set_text_to_str("Already at newest change")

        elif key == ord('"'):
            logger.info("Command: \" (register prefix)")
            self._pending_register = True  # Next key will be register name

        elif key == ord("y"):
            logger.info("Command: y (waiting for second y)")
            self._last_command_key = ord("y")

        elif key == ord("d"):
            logger.info("Command: d (waiting for second d)")
            self._last_command_key = ord("d")

        elif key == ord("c"):
            logger.info("Command: c (waiting for second c)")
            self._last_command_key = ord("c")

        elif key == ord("p"):
            logger.info("Command: p (paste after)")
            register = self._pending_register if self._pending_register and self._pending_register is not True else None
            content = self.register_manager.get_register(register if register else '"')
            if content:
                # Use Command pattern for undo/redo support
                cmd = PasteAfterCommand(self.focused_box.text, content)
                self.command_history.execute_command(cmd)
                self.focused_box.redraw(with_cursor=True)
            self._pending_register = None

        elif key == ord("P"):
            logger.info("Command: P (paste before)")
            register = self._pending_register if self._pending_register and self._pending_register is not True else None
            content = self.register_manager.get_register(register if register else '"')
            if content:
                # Use Command pattern for undo/redo support
                cmd = PasteBeforeCommand(self.focused_box.text, content)
                self.command_history.execute_command(cmd)
                self.focused_box.redraw(with_cursor=True)
            self._pending_register = None

        elif key == ord("C"):
            logger.info("Command: C (change to end of line)")
            # Use Command pattern for undo/redo support
            cmd = ChangeToEndOfLineCommand(self.focused_box.text)
            self.command_history.execute_command(cmd)
            # Store deleted text in register
            deleted = cmd.deleted_text
            if deleted:
                self.register_manager.delete_to_register(self._pending_register, deleted)
            self._pending_register = None
            self.enter_insert_mode()

        elif key == ord("D"):
            logger.info("Command: D (delete to end of line)")
            # Use Command pattern for undo/redo support
            cmd = DeleteToEndOfLineCommand(self.focused_box.text)
            self.command_history.execute_command(cmd)
            # Store deleted text in register
            deleted = cmd.deleted_text
            self.register_manager.delete_to_register(self._pending_register, deleted)
            self._pending_register = None
            self.focused_box.redraw(with_cursor=True)

        elif key == ord("J"):
            logger.info("Command: J (join lines)")
            # Use Command pattern for undo/redo support
            cmd = JoinLinesCommand(self.focused_box.text)
            self.command_history.execute_command(cmd)
            self.focused_box.redraw(with_cursor=True)

        elif key == ord(":"):
            logger.info("Command: :")
            self.enter_command_entry_mode()

        elif key == ord("v"):
            logger.info("Command: v (visual mode)")
            self.enter_visual_mode()

        elif key == ord("V"):
            logger.info("Command: V (visual line mode)")
            self.enter_visual_line_mode()

        elif key == ord("\n") or key == ord("\r"):
            logger.info("Key: Enter")
            self.submit()
            self.enter_insert_mode(append=True)

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
            self.submit_command()
            self.enter_command_mode()

        else:
            self.text_handler(key)

    def visual_mode_handler(self, key: int):
        """Handle keypresses in VISUAL mode (character-wise selection)."""
        logger.debug("visual_mode_handler.key_pressed: %s", chr(key))

        # Navigation keys - move cursor and extend selection
        if key == ord("j") or key == curses.KEY_DOWN:
            logger.info("Command: j (cursor down)")
            self.focused_box.cursor_down()

        elif key == ord("k") or key == curses.KEY_UP:
            logger.info("Command: k (cursor up)")
            self.focused_box.cursor_up()

        elif key == ord("h") or key == curses.KEY_LEFT:
            logger.info("Command: h (cursor left)")
            self.focused_box.cursor_left()

        elif key == ord("l") or key == curses.KEY_RIGHT:
            logger.info("Command: l (cursor right)")
            self.focused_box.cursor_right()

        elif key == ord("w"):
            logger.info("Command: w (word forward)")
            self.focused_box.word_forward()

        elif key == ord("b"):
            logger.info("Command: b (word backward)")
            self.focused_box.word_backward()

        elif key == ord("$"):
            logger.info("Command: $ (end of line)")
            self.focused_box.end_of_line()

        elif key == ord("0"):
            logger.info("Command: 0 (start of line)")
            self.focused_box.start_of_line()

        # Operations on selection
        elif key == ord("d"):
            logger.info("Command: d (delete selection)")
            deleted = self.focused_box.text.delete_selection()
            self.register_manager.delete_to_register(self._pending_register, deleted)
            self._pending_register = None
            self.enter_command_mode()

        elif key == ord("y"):
            logger.info("Command: y (yank selection)")
            yanked = self.focused_box.text.get_selected_text()
            self.register_manager.yank_to_register(self._pending_register, yanked)
            self._pending_register = None
            self.focused_box.text.end_selection()
            self.enter_command_mode()

        elif key == ord("c"):
            logger.info("Command: c (change selection)")
            deleted = self.focused_box.text.delete_selection()
            self.register_manager.delete_to_register(self._pending_register, deleted)
            self._pending_register = None
            self.enter_insert_mode()

        # Exit visual mode
        elif key == 27:  # Escape
            logger.info("Command: Escape")
            self.focused_box.text.end_selection()
            self.enter_command_mode()

        elif key == ord("v"):
            # Pressing 'v' again exits visual mode
            logger.info("Command: v (exit visual mode)")
            self.focused_box.text.end_selection()
            self.enter_command_mode()

    def visual_line_mode_handler(self, key: int):
        """Handle keypresses in VISUAL LINE mode (line-wise selection)."""
        logger.debug("visual_line_mode_handler.key_pressed: %s", chr(key))

        # Navigation keys - move cursor and extend selection (line-wise)
        if key == ord("j") or key == curses.KEY_DOWN:
            logger.info("Command: j (cursor down)")
            self.focused_box.cursor_down()
            # In visual line mode, ensure we select full lines
            self.focused_box.start_of_line()

        elif key == ord("k") or key == curses.KEY_UP:
            logger.info("Command: k (cursor up)")
            self.focused_box.cursor_up()
            # In visual line mode, ensure we select full lines
            self.focused_box.start_of_line()

        # Line operations
        elif key == ord("d"):
            logger.info("Command: d (delete lines)")
            # For line mode, we want to delete entire lines
            # First, get selection range
            if self.focused_box.text.is_selecting:
                start = self.focused_box.text.selection_start
                end = self.focused_box.text.cursor_position

                # Ensure start is before end
                if start.lineno > end.lineno:
                    start, end = end, start

                # Expand to full lines
                self.focused_box.text.goto(start)
                self.focused_box.start_of_line()
                start = self.focused_box.text.cursor_position

                self.focused_box.text.goto(end)
                self.focused_box.end_of_line()

                # Delete the selection
                deleted = self.focused_box.text.delete_selection()
                self.register_manager.delete_to_register(self._pending_register, deleted)
                self._pending_register = None
            self.enter_command_mode()

        elif key == ord("y"):
            logger.info("Command: y (yank lines)")
            yanked = self.focused_box.text.get_selected_text()
            self.register_manager.yank_to_register(self._pending_register, yanked)
            self._pending_register = None
            self.focused_box.text.end_selection()
            self.enter_command_mode()

        # Exit visual line mode
        elif key == 27:  # Escape
            logger.info("Command: Escape")
            self.focused_box.text.end_selection()
            self.enter_command_mode()

        elif key == ord("V"):
            # Pressing 'V' again exits visual line mode
            logger.info("Command: V (exit visual line mode)")
            self.focused_box.text.end_selection()
            self.enter_command_mode()

import curses
from enum import Enum
from typing import Callable, Optional

from textbox.ui.window import Window
from textbox.ui.input_manager import AsyncInputManager
from textbox.ui.input_box import InputBox
from textbox.ui.text_box import TextBox
from textbox.core.text import Text
from textbox.core.events import EventBus
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
    VisualDeleteCommand,
    VisualChangeCommand,
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
    SEARCH_ENTRY = 7


class InputOutputWorkspace:
    def __init__(self, main_window: Window, input_manager: AsyncInputManager, event_bus: Optional[EventBus] = None):
        self.main_window = main_window
        self.command_box_height = 1
        self.user_box_height = 5
        self.event_bus = event_bus if event_bus is not None else EventBus()

        self.command_box = InputBox(
            "command_box", main_window, self.command_bounding_box, ColorCode.GREY,
            top_to_bottom=True, event_bus=self.event_bus
        )

        logger.info("command_box: %s", self.command_box)

        self.user_box = InputBox(
            "user_box", main_window, self.user_bounding_box, ColorCode.WHITE,
            top_to_bottom=True, has_box=True, event_bus=self.event_bus
        )
        self.output_box = TextBox(
            "output_box",
            main_window,
            self.output_bounding_box,
            ColorCode.OUPTUT_TEXT,
            top_to_bottom=False,
            has_box=True,
            event_bus=self.event_bus,
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

        # Search state
        self._search_pattern = ""
        self._search_forward = True  # True for '/', False for '?'
        self._last_search_pattern = ""
        self._last_search_forward = True

        input_manager.on_keypress = self.handle_keypress
        input_manager.redraw = self.redraw

    def set_submit_callback(self, func: Callable[[Text], None]):
        self._submit_callback = func

    def set_command_callback(self, func: Callable[[str], None]):
        self._command_callback = func

    def _publish_mode_changed(self, old_mode: INPUT_MODE, new_mode: INPUT_MODE) -> None:
        """Publish a ModeChangedEvent.

        Args:
            old_mode: Previous INPUT_MODE
            new_mode: New INPUT_MODE
        """
        from textbox.core.events import ModeChangedEvent
        event = ModeChangedEvent(old_mode=old_mode, new_mode=new_mode)
        self.event_bus.publish(event)

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
        old_mode = self.input_mode
        curses.curs_set(1)
        self.input_mode = INPUT_MODE.REPLACE
        self.focused_box = self.user_box
        self.command_box.set_text_to_str("-- REPLACE --")
        logger.info("Input Mode: REPLACE")
        self.focused_box.refresh()
        self._publish_mode_changed(old_mode, INPUT_MODE.REPLACE)

    def enter_insert_mode(self, append: bool = False):
        old_mode = self.input_mode
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
        self._publish_mode_changed(old_mode, INPUT_MODE.INSERT)

    def enter_command_mode(self) -> None:
        old_mode = self.input_mode
        curses.curs_set(1)
        self.input_mode = INPUT_MODE.COMMAND
        self.command_box.set_text_to_str("")
        if self.focused_box != self.user_box:
            self.focused_box = self.user_box
        self.focused_box.text.edit_mode = False
        self.command_box.set_text_to_str("-- COMMAND --")
        logger.info("Input Mode: COMMAND")
        self.focused_box.redraw(with_cursor=True)
        self._publish_mode_changed(old_mode, INPUT_MODE.COMMAND)

    def enter_command_entry_mode(self):
        old_mode = self.input_mode
        curses.curs_set(2)
        self.input_mode = INPUT_MODE.COMMAND_ENTRY
        self.focused_box = self.command_box
        self.command_box.set_text_to_str(":")
        self.focused_box.text.edit_mode = True
        self.focused_box.text.increment_column_ptr()
        logger.info("Input Mode: COMMAND_ENTRY")
        self.focused_box.redraw()
        self._publish_mode_changed(old_mode, INPUT_MODE.COMMAND_ENTRY)

    def enter_visual_mode(self) -> None:
        """Enter VISUAL mode (character-wise selection)."""
        old_mode = self.input_mode
        curses.curs_set(1)
        self.input_mode = INPUT_MODE.VISUAL
        self.focused_box = self.user_box
        self.focused_box.text.edit_mode = False
        self.focused_box.text.start_selection()
        self.command_box.set_text_to_str("-- VISUAL --")
        logger.info("Input Mode: VISUAL")
        self.focused_box.redraw(with_cursor=True)
        self._publish_mode_changed(old_mode, INPUT_MODE.VISUAL)

    def enter_visual_line_mode(self) -> None:
        """Enter VISUAL LINE mode (line-wise selection)."""
        old_mode = self.input_mode
        curses.curs_set(1)
        self.input_mode = INPUT_MODE.VISUAL_LINE
        self.focused_box = self.user_box
        self.focused_box.text.edit_mode = False
        self.focused_box.text.start_selection()
        self.command_box.set_text_to_str("-- VISUAL LINE --")
        logger.info("Input Mode: VISUAL_LINE")
        self.focused_box.redraw(with_cursor=True)
        self._publish_mode_changed(old_mode, INPUT_MODE.VISUAL_LINE)

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
        elif self.input_mode == INPUT_MODE.SEARCH_ENTRY:
            self.search_entry_handler(key)

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

        # Publish command executed event
        from textbox.core.events import CommandExecutedEvent
        event = CommandExecutedEvent(command_name=command, args=text)
        self.event_bus.publish(event)

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

        elif key == ord("/"):
            logger.info("Command: / (forward search)")
            self.enter_search_mode(forward=True)

        elif key == ord("?"):
            logger.info("Command: ? (backward search)")
            self.enter_search_mode(forward=False)

        elif key == ord("n"):
            logger.info("Command: n (next search result)")
            self.search_next()

        elif key == ord("N"):
            logger.info("Command: N (previous search result)")
            self.search_previous()

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
            # Use Command pattern for undo/redo support
            cmd = VisualDeleteCommand(self.focused_box.text)
            self.command_history.execute_command(cmd)
            # Store deleted text in register
            deleted = cmd.deleted_text
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
            # Use Command pattern for undo/redo support
            cmd = VisualChangeCommand(self.focused_box.text)
            self.command_history.execute_command(cmd)
            # Store deleted text in register
            deleted = cmd.deleted_text
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

                # Use Command pattern for undo/redo support
                cmd = VisualDeleteCommand(self.focused_box.text)
                self.command_history.execute_command(cmd)
                # Store deleted text in register
                deleted = cmd.deleted_text
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

    def enter_search_mode(self, forward: bool = True):
        """Enter search entry mode."""
        self.input_mode = INPUT_MODE.SEARCH_ENTRY
        self._search_forward = forward
        self._search_pattern = ""
        # Show search prompt in command box
        prompt = "/" if forward else "?"
        self.command_box.text.erase()
        self.command_box.text.edit_mode = True
        self.command_box.text.insert(prompt)
        self.command_box.redraw(with_cursor=True)
        logger.info("Input Mode: SEARCH_ENTRY (%s)", "forward" if forward else "backward")

    def search_entry_handler(self, key: int):
        """Handle keypresses in SEARCH_ENTRY mode."""
        if key == ord('\n') or key == ord('\r'):
            # Execute search
            logger.info("Executing search: %s", self._search_pattern)
            self.execute_search()
        elif key == 27:  # ESC
            # Cancel search
            logger.info("Search cancelled")
            self.command_box.text.erase()
            self.enter_command_mode()
        elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
            # Handle backspace
            if len(self._search_pattern) > 0:
                self._search_pattern = self._search_pattern[:-1]
                # Update command box
                prompt = "/" if self._search_forward else "?"
                self.command_box.text.erase()
                self.command_box.text.edit_mode = True
                self.command_box.text.insert(prompt + self._search_pattern)
                self.command_box.redraw(with_cursor=True)
        elif 32 <= key <= 126:  # Printable characters
            # Add character to search pattern
            self._search_pattern += chr(key)
            # Update command box
            self.command_box.text.insert(chr(key))
            self.command_box.redraw(with_cursor=True)

    def execute_search(self):
        """Execute the current search and move cursor to first match."""
        if not self._search_pattern:
            self.enter_command_mode()
            return

        # Save search pattern for n/N commands
        self._last_search_pattern = self._search_pattern
        self._last_search_forward = self._search_forward

        # Perform search
        found = self._perform_search(self._search_pattern, self._search_forward)

        # Return to command mode first
        self.input_mode = INPUT_MODE.COMMAND
        self.focused_box.text.edit_mode = False
        curses.curs_set(1)
        logger.info("Input Mode: COMMAND")

        # Then set the message in command box
        self.command_box.text.erase()
        if found:
            self.command_box.set_text_to_str(f"/{self._search_pattern}" if self._search_forward else f"?{self._search_pattern}")
        else:
            self.command_box.set_text_to_str(f"Pattern not found: {self._search_pattern}")

    def search_next(self):
        """Find next occurrence of last search pattern."""
        if not self._last_search_pattern:
            self.command_box.set_text_to_str("No previous search pattern")
            return

        found = self._perform_search(self._last_search_pattern, self._last_search_forward, skip_current=True)
        if not found:
            self.command_box.set_text_to_str("Search hit BOTTOM, continuing at TOP")

    def search_previous(self):
        """Find previous occurrence of last search pattern."""
        if not self._last_search_pattern:
            self.command_box.set_text_to_str("No previous search pattern")
            return

        # Reverse direction for N
        found = self._perform_search(self._last_search_pattern, not self._last_search_forward, skip_current=True)
        if not found:
            self.command_box.set_text_to_str("Search hit TOP, continuing at BOTTOM")

    def _perform_search(self, pattern: str, forward: bool = True, skip_current: bool = False) -> bool:
        """Perform search and move cursor to match. Returns True if found."""
        text = self.focused_box.text
        current_line = text.line_ptr
        current_col = text.column_ptr

        # If skipping current position (for n/N), start from next/previous position
        if skip_current:
            if forward:
                current_col += 1
            else:
                current_col -= 1

        # Search from current position
        if forward:
            # Search forward
            for line_idx in range(current_line, len(text._text_lines)):
                line_text = str(text._text_lines[line_idx])
                start_col = current_col if line_idx == current_line else 0
                pos = line_text.find(pattern, start_col)
                if pos != -1:
                    text._line_ptr = line_idx
                    text._column_ptr = pos
                    self.focused_box.redraw(with_cursor=True)
                    return True

            # Wrap around to beginning
            for line_idx in range(0, current_line):
                line_text = str(text._text_lines[line_idx])
                pos = line_text.find(pattern)
                if pos != -1:
                    text._line_ptr = line_idx
                    text._column_ptr = pos
                    self.focused_box.redraw(with_cursor=True)
                    return True
        else:
            # Search backward
            for line_idx in range(current_line, -1, -1):
                line_text = str(text._text_lines[line_idx])
                # For current line, only search up to current column
                if line_idx == current_line:
                    search_text = line_text[:current_col]
                else:
                    search_text = line_text
                pos = search_text.rfind(pattern)
                if pos != -1:
                    # If on current line, ensure the match doesn't overlap with cursor
                    if line_idx == current_line:
                        # Match ends at pos + len(pattern)
                        # If cursor is inside or right after the match, skip it
                        if pos + len(pattern) > current_col:
                            continue
                    text._line_ptr = line_idx
                    text._column_ptr = pos
                    self.focused_box.redraw(with_cursor=True)
                    return True

            # Wrap around to end
            for line_idx in range(len(text._text_lines) - 1, current_line, -1):
                line_text = str(text._text_lines[line_idx])
                pos = line_text.rfind(pattern)
                if pos != -1:
                    text._line_ptr = line_idx
                    text._column_ptr = pos
                    self.focused_box.redraw(with_cursor=True)
                    return True

        return False

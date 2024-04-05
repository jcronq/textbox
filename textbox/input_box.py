from typing import Union

from textbox.text_box import TextBox
from textbox.text import Text

import logging

logger = logging.getLogger()


class InputHistory:
    def __init__(self, max_size: int = 100):
        self._max_size = max_size
        self._history = []
        self._history_ptr = 0
        self._short_term_memory = None

    def has_short_term_memory(self) -> bool:
        return self._short_term_memory is not None

    def pop_short_term_memory(self) -> Text:
        tmp = self._short_term_memory
        self._short_term_memory = None
        return tmp

    def set_short_term_memory(self, text: Text) -> None:
        if not isinstance(text, Text):
            raise ValueError("Text must be a Text object")
        self._short_term_memory = text

    def at_present(self) -> bool:
        return self._history_ptr == len(self._history)

    def has_history(self) -> bool:
        return len(self._history) > 0 and self._history_ptr > 0

    def append(self, text: Text) -> None:
        if not isinstance(text, Text):
            raise ValueError("Text must be a Text object")

        self._history.append(text)
        if len(self._history) > self._max_size:
            self._history = self._history[-self._max_size :]
        self._history_ptr = len(self._history)

    def previous(self) -> Text:
        if self._history_ptr > 0:
            self._history_ptr -= 1
            return self._history[self._history_ptr]
        else:
            return self._history[0]

    def next(self) -> Text:
        if self._history_ptr < len(self._history) - 1:
            self._history_ptr += 1
            return self._history[self._history_ptr]
        elif self._history_ptr == len(self._history) - 1:
            self._history_ptr += 1
            return self.pop_short_term_memory()
        else:
            return None

    def __getitem__(self, item: Union[int, slice]) -> Text:
        return self._history[item]

    def __len__(self):
        return len(self._history)

    def __repr__(self):
        return f"InputHistory(len={len(self._history)}, ptr={self._history_ptr}, memory={str(self._short_term_memory)})"


class InputBox(TextBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.top_to_bottom:
            raise ValueError("InputBox must be top-to-bottom")

        # Initialize the text list with a single empty text.
        self._text_list.insert("")
        self._text_ptr = 0
        self._history = InputHistory()

    def set_text(self, text: Text):
        if self.verbose:
            logger.info("Setting text to %s", text)
        if not isinstance(text, Text):
            raise ValueError("Text must be a Text object")
        text.to_end_of_text()
        self._text_list.set_first_text(text.copy())
        self.redraw()

    def set_text_to_str(self, text: str):
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        self.text.set_text_to_str(text)
        self.redraw()

    @property
    def edit_mode(self):
        self.text.edit_mode = True

    @edit_mode.setter
    def edit_mode(self, value: bool):
        self.text.edit_mode = value

    @property
    def text(self) -> Text:
        return self._text_list.texts[0]

    @property
    def character_at_cursor(self) -> str:
        return self.text.character_at_cursor

    def history_scroll_up(self):
        if self.verbose:
            logger.info("History scroll up: %s", self._history)
        if not self._history.has_history():
            if self.verbose:
                logger.info("Key: Up (No History)")
            return
        elif self._history.at_present():
            if self.verbose:
                logger.info("Key: Up (History) - First Press")
            self._history.set_short_term_memory(self.text)
        else:
            if self.verbose:
                logger.info("Key: Up (History) - Press")
        self.set_text(self._history.previous())
        if self.verbose:
            logger.info("History: %s", self._history)

    def history_scroll_down(self):
        if self.verbose:
            logger.info("History scroll down: %s", self._history)
        if self._history.at_present():
            if self.verbose:
                logger.info("Key: Down (History) - No further history")
        else:
            if self.verbose:
                logger.info("Key: Down (History) - Press")
            self.set_text(self._history.next())
            self.update_cursor()
        if self.verbose:
            logger.info("History: %s", self._history)

    def append_history(self):
        if self.verbose:
            logger.info("Appending to history: %s", repr(self.text))
        self._history.append(self.text.copy())

    def cursor_down(self):
        self.text.increment_line_ptr()
        self.redraw(True)

    def cursor_up(self):
        self.text.decrement_line_ptr()
        self.redraw(True)

    def cursor_left(self):
        self.text.decrement_column_ptr()
        self.redraw(True)

    def cursor_right(self):
        self.text.increment_column_ptr()
        self.redraw(True)

    def handle_backspace(self):
        self.text.backspace()
        self.redraw(with_cursor=True)

    def insert_character_at_cursor(self, ch: str):
        self.text.insert(ch)
        self.redraw(with_cursor=True)

    def replace_character_at_cursor(self, ch: str):
        self.text.replace_character(ch)
        self.redraw(with_cursor=True)

    def word_forward(self):
        next_word_position = self.text.start_of_next_word()
        if next_word_position is not None:
            self.text.goto(next_word_position)
        self.redraw(with_cursor=True)

    def word_backward(self):
        prev_word_position = self.text.start_of_previous_word()
        if prev_word_position is not None:
            self.text.goto(prev_word_position)
        self.redraw(with_cursor=True)

    def end_of_line(self):
        self.text.to_end_of_line()
        self.redraw(with_cursor=True)

    def start_of_line(self):
        self.text.to_start_of_line()
        self.redraw(with_cursor=True)

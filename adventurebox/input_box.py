from adventurebox.text_box import TextBox
from adventurebox.text import Text

import logging

logger = logging.getLogger()


class InputHistory:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.history = []
        self.history_ptr = 0
        self.short_term_memory = None

    def has_short_term_memory(self):
        return self.short_term_memory is not None

    def pop_short_term_memory(self):
        tmp = self.short_term_memory
        self.short_term_memory = None
        return tmp

    def set_short_term_memory(self, text: str):
        self.short_term_memory = text

    def at_present(self):
        return self.history_ptr == len(self.history)

    def has_history(self):
        return len(self.history) > 0 and self.history_ptr > 0

    def append(self, text: str):
        self.history.append(text)
        if len(self.history) > self.max_size:
            self.history = self.history[-self.max_size :]
        self.history_ptr = len(self.history)

    def previous(self):
        if self.history_ptr > 0:
            self.history_ptr -= 1
            return self.history[self.history_ptr]
        else:
            return self.history[0]

    def next(self):
        if self.history_ptr < len(self.history) - 1:
            self.history_ptr += 1
            return self.history[self.history_ptr]
        elif self.history_ptr == len(self.history) - 1:
            self.history_ptr += 1
            return self.pop_short_term_memory()
        else:
            return None

    def __getitem__(self, item):
        return self.history[item]

    def __len__(self):
        return len(self.history)


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
        if not isinstance(text, Text):
            raise ValueError("Text must be a Text object")
        text.to_end_of_text()
        self._text_list.set_first_text(text)

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

    def history_scroll_up(self):
        if not self._history.has_history():
            logger.debug("Key: Up (No History)")
            return
        elif self._history.at_present():
            logger.debug("Key: Up (History) - First Press")
            self._history.set_short_term_memory(self.text)
        else:
            logger.debug("Key: Up (History) - Press")
        self.set_text(self._history.previous())
        # self.column_ptr = len(self.text)

    def history_scroll_down(self):
        if self._history.at_present():
            logger.debug("Key: Down (History) - No further history")
        else:
            logger.debug("Key: Down (History) - Press")
            self.set_text(self._history.next())
            self.update_cursor()

    def append_history(self):
        self._history.append(self.text)

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
        logger.info(repr(self.text))
        self.text.insert(ch)
        logger.info(repr(self.text))
        self.redraw(with_cursor=True)

    def replace_character_at_cursor(self, ch: str):
        self.text.replace_character(ch)
        self.redraw(with_cursor=True)

    def word_forward(self):
        self.text.to_start_of_next_word()
        self.redraw(with_cursor=True)

    def word_backward(self):
        print("not implemented")
        self.redraw(with_cursor=True)

    def end_of_line(self):
        self.text.to_end_of_line()
        self.redraw(with_cursor=True)

    def start_of_line(self):
        self.text.to_start_of_line()
        self.redraw(with_cursor=True)

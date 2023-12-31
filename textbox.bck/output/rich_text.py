from dataclasses import dataclass
from . import Printable

whitespace = [" ", "\n", "\t"]
tab_width = 2


@dataclass
class RichText(Printable):
    """The base unit of text in the textbox library. RichText is a string with formatting information."""

    text: str = ""

    @staticmethod
    def is_whitespace(word: str):
        return all([char in whitespace for char in word])

    def __len__(self):
        return sum([1 if char.isprintable() else 0 for char in self.text])

    def append(self, txt: str):
        self.text += txt
        return self

    def __add__(self, other: str):
        if isinstance(other, RichText):
            other = other.text
        elif isinstance(other, str):
            pass
        else:
            raise TypeError(f"Cannot add {type(other)} to RichText")
        self.text += other
        return self

    def clone_settings(self):
        return RichText(
            text="",
            foreground_color=self.foreground_color,
            background_color=self.background_color,
            bold=self.bold,
            underline=self.underline,
            italic=self.italic,
            strikethrough=self.strikethrough,
            inverse=self.inverse,
        )

    def clone(self):
        text = self.clone_settings()
        text.text = self.text
        return text

    def __eq__(self, other: "RichText"):
        if isinstance(other, RichText):
            return self.text == other.text and super().__eq__(other)
        else:
            return False

    def __repr__(self):
        options = ", ".join([f"{key}={value}" for key, value in self.__dict__.items() if value is not None])
        return f"RichText({options})"

    def __str__(self):
        return self.text

    def words(self):
        cur_word = ""
        is_whitespace = False
        for char in self.text:
            if self.is_whitespace(char):
                if is_whitespace or len(cur_word) == 0:
                    if char == "\t":
                        cur_word += " " * tab_width
                    elif char == "\n":
                        yield "\n"
                        cur_word = ""
                        is_whitespace = False
                    else:
                        cur_word += char
                        is_whitespace = True
                else:
                    yield cur_word
                    cur_word = char
                    is_whitespace = True
            else:
                if is_whitespace:
                    yield cur_word
                    cur_word = char
                    is_whitespace = False
                else:
                    cur_word += char
        yield cur_word

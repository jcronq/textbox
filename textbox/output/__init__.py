from typing import Optional
from dataclasses import dataclass


@dataclass
class Printable:
    foreground_color: Optional[str] = None
    background_color: Optional[str] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strikethrough: Optional[bool] = None
    inverse: Optional[bool] = None

    def __eq__(self, other):
        return (
            self.background_color == other.background_color
            and self.foreground_color == other.foreground_color
            and self.bold == other.bold
            and self.italic == other.italic
            and self.underline == other.underline
            and self.strikethrough == other.strikethrough
            and self.inverse == other.inverse
        )

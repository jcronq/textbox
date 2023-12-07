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

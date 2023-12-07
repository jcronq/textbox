from typing import List, Optional
from termcolor import cprint, colored
from textbox.config.colors import Colorizer
from textbox.output.block_text import LineText
from textbox.output.block_text import BlockText
from textbox.output.rich_text import RichText
from textbox.output import Printable
from functools import wraps

from . import PrinterBase


class TermcolorPrinter(PrinterBase):
    @staticmethod
    @wraps(cprint)
    def c_print(txt, color_name, *args, **kwargs):
        cprint(txt, color_name, *args, **kwargs)

    @staticmethod
    def print(printable_object: Printable):
        print(TermcolorPrinter.sprint(printable_object))

    @staticmethod
    def sprint(printable_object: Printable):
        if isinstance(printable_object, RichText):
            return TermcolorPrinter._print_richtext(printable_object)
        elif isinstance(printable_object, LineText):
            return TermcolorPrinter._print_linetext(printable_object)
        elif isinstance(printable_object, BlockText):
            return TermcolorPrinter._print_blocktext(printable_object)

    @staticmethod
    def _sprint_blocktext(text_block: BlockText, ancestry: Optional[List[Printable]] = None, print: bool = True):
        if ancestry == None:
            ancestry = []
        ancestry.append(text_block)
        return "".join(
            [TermcolorPrinter._sprint_linetext(text_line, ancestry=ancestry) for text_line in text_block.wrapped_lines]
        )

    def _sprint_linetext(text_line: LineText, ancestry: Optional[List[Printable]] = None, print: bool = True):
        if ancestry == None:
            ancestry = []
        ancestry.append(text_line)
        return (
            "".join(
                [
                    TermcolorPrinter._sprint_richtext(rich_text, ancestry, print)
                    for rich_text in text_line.rich_text_list
                ]
            )
            + "\n"
        )

    @staticmethod
    def _sprint_richtext(
        rich_text: RichText,
        ancestry: Optional[List[Printable]] = None,
    ):
        if ancestry == None:
            ancestry = []
        ancestry.append(rich_text)
        settings = Printable()
        for ancestor in ancestry[::-1]:
            settings.foreground_color = (
                ancestor.foreground_color if settings.foreground_color is None else settings.foreground_color
            )
            settings.background_color = (
                ancestor.background_color if settings.background_color is None else settings.background_color
            )
            settings.bold = ancestor.bold if settings.bold is None else settings.bold
            settings.italic = ancestor.italic if settings.italic is None else settings.italic
            settings.underline = ancestor.underline if settings.underline is None else settings.underline
            settings.strikethrough = (
                ancestor.strikethrough if settings.strikethrough is None else settings.strikethrough
            )
            settings.inverse = ancestor.inverse if settings.inverse is None else settings.inverse

        attributes = []
        if settings.bold:
            attributes.append("bold")
        if settings.italic:
            attributes.append("italic")
        if settings.underline:
            attributes.append("underline")
        if settings.strikethrough:
            attributes.append("strikethrough")
        if settings.inverse:
            foreground_color, background_color = background_color, foreground_color

        return colored(
            rich_text.text,
            foreground_color,
            on_color=background_color,
            attrs=attributes,
            end="",
        )

    # @staticmethod
    # def print(text_list: List[RichText], text_block: TextBlock):
    #     for text_line in text_block.wrapped_text(text_list):
    #         for rich_text in text_line.rich_text_list:
    #             TermcolorPrinter.c_print(rich_text.color, rich_text.text)
    #         print()


# def colorize(txt, noMatchColor, colored_words):
#     indexes = []
#     for colored_word in colored_words:
#         searchWord = colored_word['word']
#         color = colored_word['color']
#         reg_ex = re.compile(r'(([ .,!?\n\t]|^){1}'+searchWord+'([ .,!?\n\t]|$){1})')
#         res = reg_ex.findall(txt)
#         index = -1
#         if len(res) > 0:
#             pattern = res[0][0]
#             index = txt.find(pattern)
#             word_len = len(pattern)
#         if index >= 0:
#             indexes.append({'end': index + word_len, 'start': index, 'color': color})
#     indexes.sort(key=lambda i: i['start'])
#     colorized_words = []
#     for i, index in enumerate(indexes):
#         if i == 0 and index['start'] != 0:
#             colorized_words.append(colored(txt[0:index['start']],noMatchColor))
#         colorized_words.append(colored(txt[index['start']:index['end']], index['color']))
#         if i == len(indexes) - 1 and index['end'] != len(txt):
#             colorized_words.append(colored(txt[index['end']:], noMatchColor))

#     return ''.join(colorized_words)

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
    @wraps(print)
    def print(*printable_object: List[Printable], **kwargs):
        print(*TermcolorPrinter.sprint(*printable_object), **kwargs)

    @staticmethod
    def sprint(*printable_objects: List[Printable]):
        results = []
        for printable_object in printable_objects:
            if isinstance(printable_object, RichText):
                result = TermcolorPrinter._sprint_richtext(printable_object)
            elif isinstance(printable_object, LineText):
                result = TermcolorPrinter._sprint_linetext(printable_object)
            elif isinstance(printable_object, BlockText):
                result = TermcolorPrinter._sprint_blocktext(printable_object)
            else:
                result = str(printable_object)
            results.append(result)
        if len(results) == 0:
            return ""
        if len(results) == 1:
            # breakpoint()
            return results[0]
        return tuple(results)

    @staticmethod
    def _sprint_blocktext(text_block: BlockText, ancestry: Optional[List[Printable]] = None, print: bool = True):
        if ancestry == None:
            ancestry = []
        ancestry.append(text_block)
        return "\n".join(
            [TermcolorPrinter._sprint_linetext(text_line, ancestry=ancestry) for text_line in text_block.wrapped_lines]
        )

    def _sprint_linetext(text_line: LineText, ancestry: Optional[List[Printable]] = None, print: bool = True):
        if ancestry == None:
            ancestry = []
        ancestry.append(text_line)
        return "".join(
            [TermcolorPrinter._sprint_richtext(rich_text, ancestry, print) for rich_text in text_line.rich_text_list]
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
            # Strikethrough not supported
            # settings.strikethrough = (
            #     ancestor.strikethrough if settings.strikethrough is None else settings.strikethrough
            # )
            settings.inverse = ancestor.inverse if settings.inverse is None else settings.inverse

        attributes = []
        if settings.bold:
            attributes.append("bold")
        if settings.italic:
            attributes.append("italic")
        if settings.underline:
            attributes.append("underline")
        # Strikethrough not supported
        # if settings.strikethrough:
        #     attributes.append("strikethrough")
        if settings.inverse:
            foreground_color, background_color = background_color, foreground_color

        args = [rich_text.text]
        kwargs = {}
        if settings.foreground_color is not None:
            args.append(settings.foreground_color)
        if settings.background_color is not None:
            kwargs["on_color"] = f"on_{settings.background_color}"
        if len(attributes) > 0:
            kwargs["attrs"] = attributes

        if len(args) > 1 or len(kwargs) > 0:
            kwargs["force_color"] = True
            return colored(*args, **kwargs)
        return str(rich_text.text)

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

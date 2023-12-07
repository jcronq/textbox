from typing import List
from termcolor import cprint
from textbox.config.colors import Colorizer
from textbox.output.block_text import LineText
from textbox.output.block_text import BlockText
from textbox.output.rich_text import RichText
from textbox.output import Printable

from . import PrinterBase


class TermcolorPrinter(PrinterBase):
    @staticmethod
    def c_print(color_name, txt, end=""):
        cprint(txt, color_name, end=end)

    @staticmethod
    def util_print(colorizer: Colorizer, msg, end="\n"):
        cprint(msg, colorizer.color_from_text_type("color_util"), end=end)

    @staticmethod
    def print(printable_object: Printable):
        if isinstance(printable_object, RichText):
            TermcolorPrinter._print_richtext(printable_object)
        elif isinstance(printable_object, LineText):
            TermcolorPrinter._print_linetext(printable_object)
        elif isinstance(printable_object, BlockText):
            TermcolorPrinter._print_blocktext(printable_object)

    @staticmethod
    def _print_blocktext(text_block: BlockText):
        for text_line in text_block.wrapped_lines:
            TermcolorPrinter._print_linetext(text_line)

    def _print_linetext(text_line: LineText):
        for rich_text in text_line.rich_text_list:
            TermcolorPrinter._print_richtext(rich_text)
        print()

    @staticmethod
    def _print_richtext(rich_text: Printable, text_block: BlockText):
        TermcolorPrinter.c_print(rich_text.color, rich_text.text)

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

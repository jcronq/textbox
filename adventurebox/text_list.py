from typing import List, Union
from adventurebox.text import Text
from adventurebox.box_types import LineSpan


class TextList:
    def __init__(self, max_line_width: int = None):
        self._texts: List[Text] = []
        self._text_ptr = 0
        self._max_line_width = max_line_width

    def set_first_text(self, text: Text):
        self._texts[0] = text

    @property
    def max_line_width(self):
        return self._max_line_width

    @max_line_width.setter
    def max_line_width(self, value: int):
        self._max_line_width = value
        for text in self._texts:
            text.max_line_width = value

    @property
    def line_count(self):
        return sum([text.line_count for text in self._texts])

    @property
    def texts(self):
        return self._texts

    @property
    def _text_line_spans(self):
        accumulated_length = 0
        line_spans = []
        for text in self._texts:
            line_spans.append(LineSpan(accumulated_length, accumulated_length + text.line_count))
            accumulated_length += text.line_count
        return line_spans

    @property
    def current_text(self):
        if len(self._texts) == 0:
            return Text("", max_line_width=self._max_line_width)
        return self._texts[self._text_ptr - 1]

    def insert(self, text: str):
        if self._text_ptr >= len(self._texts):
            self._texts.append(Text(text, max_line_width=self.max_line_width))
        else:
            self._texts.insert(self._text_ptr, text)
        self._text_ptr += 1

    def add_text(self, text: Text):
        self._texts.append(text)
        self._text_ptr += 1

    def __len__(self):
        return sum([len(text) for text in self._texts])

    def __getitem__(self, lineaddr: Union[int, slice]) -> Union[str, List[str]]:
        """The slice is for line numbers."""
        # Determine whethe we're looking for a specific line, or a range of lines.
        if isinstance(lineaddr, int):
            start = lineaddr
            return_single = True
        elif isinstance(lineaddr, slice):
            if lineaddr.step is not None and lineaddr.step != 1:
                raise IndexError("TextList does not yet support slicing with a step.")

            start = lineaddr.start if lineaddr.start is not None else 0
            return_single = False
        else:
            raise TypeError(f"Invalid type lineaddr for indexing TextList: {type(lineaddr)}.  Expected int or slice.")

        if len(self._texts) == 0:
            return "" if return_single else []

        # Handle negative indices.
        if start < 0:
            start = self.line_count + start

        # Find the first text that contains the line number we're looking for.
        first_text_in_slice = None
        text_line_spans: List[LineSpan] = self._text_line_spans
        for text_idx, span in enumerate(text_line_spans):
            if start in span:
                if return_single:
                    for sub_lineno, line in enumerate(self._texts[text_idx].lines):
                        if sub_lineno + span.first_lineno == start:
                            return str(line)
                else:
                    first_text_in_slice = text_idx
                    break

        # If we didn't find a text that contains the line number we're looking for, raise an error.
        if first_text_in_slice is None:
            raise IndexError(f"Line number {start} is out of range for TextList.")

        # Gauranteed to be a slice if we get here.
        # Determine the stop value for the slice.
        step = lineaddr.step if lineaddr.step is not None else 1
        stop = lineaddr.stop if lineaddr.stop is not None else self.line_count
        if stop < 0:
            stop = self.line_count + stop

        # Determine the direction we're iterating through the texts.
        text_step = 1
        if step < 0:
            text_step = -1

        # Find the last text that contains the line number we're looking for.
        last_text_in_span = first_text_in_slice
        for idx, span in enumerate(text_line_spans[first_text_in_slice::text_step], start=first_text_in_slice):
            last_text_in_span = idx
            if stop in span:
                break

        # Get the lines from the texts.
        result = []
        global_lineno = text_line_spans[first_text_in_slice].first_lineno  # start
        for text_idx, text in enumerate(
            self._texts[first_text_in_slice : last_text_in_span + text_step : text_step], start=first_text_in_slice
        ):
            for _, line in enumerate(text.lines):
                if global_lineno >= start:
                    result.append(str(line))
                global_lineno += step
                if global_lineno >= stop:
                    break

            if global_lineno >= stop:
                break

        return result

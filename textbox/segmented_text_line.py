from typing import Union, List
from textbox.text_segment import TextSegment
from textbox.color_code import ColorCode


class SegmentedTextLine:
    """A line of text that can contain multiple TextSegments with different color pairs.
    This makes the individual, multi-colored segments of text easier to manage as a single line."""

    def __init__(self, text: Union[List[TextSegment], TextSegment] = None):
        if text is None:
            self._segments = []
        elif isinstance(text, TextSegment):
            self._segments = [text]
        elif isinstance(text, list):
            if not all([isinstance(segment, TextSegment) for segment in text]):
                raise ValueError("SegmentedTextLine must be initialized with a list of TextSegments")
            self._segments = text
        else:
            raise ValueError("TextLine must be initialized with a string or TextSegment")
        self.reduce()

        self._default_color_pair = ColorCode.DEFAULT

    @property
    def last_color_pair(self) -> int:
        """Get the color pair of the last TextSegment"""
        if len(self._segments) == 0:
            return self._default_color_pair
        return self._segments[-1].color_pair

    def copy(self):
        return SegmentedTextLine([segment.copy() for segment in self._segments])

    def reduce(self):
        """Combine all TextSegments with the same color pair"""
        reduced_segments = []
        for segment in self._segments:
            if segment._text == "":
                continue
            elif len(reduced_segments) == 0:
                reduced_segments.append(segment)
            elif reduced_segments[-1].color_pair == segment.color_pair:
                reduced_segments[-1] += segment
            else:
                reduced_segments.append(segment)
        self._segments = reduced_segments

    def __len__(self):
        return sum((len(segment) for segment in self._segments))

    def __str__(self):
        return "".join([str(segment) for segment in self._segments])

    def __repr__(self):
        items = [f"{repr(segment)}" for segment in self._segments]
        return f"SegmentedTextLine({items})"

    def __eq__(self, other: "SegmentedTextLine"):
        if not isinstance(other, SegmentedTextLine):
            return False
        if len(self._segments) != len(other._segments):
            return False
        return all([self._segments[idx] == other._segments[idx] for idx in range(len(self._segments))])

    def __add__(self, other: Union["SegmentedTextLine", TextSegment, str]):
        if isinstance(other, SegmentedTextLine):
            return SegmentedTextLine(self._segments + other._segments)
        elif isinstance(other, TextSegment):
            return SegmentedTextLine(self._segments + [other])
        elif isinstance(other, str):
            return SegmentedTextLine(self._segments + [TextSegment(other, self.last_color_pair)])
        else:
            raise ValueError(f"Cannot add SegmentedTextLine to {type(other)}")

    def __iter__(self):
        return iter(self._segments)

    def __contains__(self, item: str):
        if not isinstance(item, str):
            raise ValueError("SegmentedTextLine can only contain strings")
        return item in str(self)

    def __getitem__(self, item: Union[int, slice]) -> Union["SegmentedTextLine", TextSegment]:
        if isinstance(item, int):
            if item < 0:
                item = len(self) + item
            accumulated_length = 0
            for idx, segment in enumerate(self._segments):
                if accumulated_length <= item < len(segment) + accumulated_length:
                    return self._segments[idx][item - accumulated_length]
                accumulated_length += len(segment)
            raise IndexError(f"{str(self)} does not contain index: {item}")

        elif isinstance(item, slice):
            if item.step is not None and item.step != 1:
                raise IndexError("SegmentedTextLine does not support slicing with a step at this time")

            if item.start is None:
                start = 0
            else:
                if item.start < 0:
                    start = len(self) + item.start
                else:
                    start = item.start
            if item.stop is None:
                stop = len(self)
            else:
                if item.stop < 0:
                    stop = len(self) + item.stop
                else:
                    stop = item.stop

            if start == stop:
                return SegmentedTextLine()

            start_segment_idx = None
            start_col_idx = None
            stop_segment_idx = None
            stop_col_idx = None
            accumulated_length = 0
            for idx, segment in enumerate(self._segments):
                if accumulated_length <= start < len(segment) + accumulated_length:
                    start_segment_idx = idx
                    start_col_idx = start - accumulated_length
                if accumulated_length <= stop < len(segment) + accumulated_length:
                    stop_segment_idx = idx
                    stop_col_idx = stop - accumulated_length
                accumulated_length += len(segment)

            if start_segment_idx is None:
                return SegmentedTextLine()

            if stop_segment_idx is None and stop >= len(self):
                stop_segment_idx = len(self._segments) - 1
                stop_col_idx = len(self._segments[-1])

            new_segments = []
            while start_segment_idx < stop_segment_idx:
                new_segments += [self._segments[start_segment_idx][start_col_idx:]]
                start_col_idx = 0
                start_segment_idx += 1
            new_segments += [self._segments[stop_segment_idx][start_col_idx:stop_col_idx]]
            return SegmentedTextLine(new_segments)

        else:
            raise IndexError(f"SegmentedTextLine does not support indexing with {type(item)}")

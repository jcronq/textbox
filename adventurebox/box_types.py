from typing import NamedTuple, Union


# class Coordinate(NamedTuple):
#     x: int
#     y: int

#     def __repr__(self):
#         return f"Coordinate(x={self.x}, y={self.y})"

#     def __str__(self):
#         return f"[{self.x}, {self.y}]"

#     def __add__(self, other):
#         if isinstance(other, Coordinate):
#             return Coordinate(self.x + other.x, self.y + other.y)
#         elif isinstance(other, tuple) and len(other) == 2:
#             return Coordinate(self.x + other[0], self.y + other[1])
#         else:
#             raise TypeError(f"Cannot add {type(other)} to Coordinate")

#     def __sub__(self, other):
#         if isinstance(other, Coordinate):
#             return Coordinate(self.x - other.x, self.y - other.y)
#         elif isinstance(other, tuple) and len(other) == 2:
#             return Coordinate(self.x - other[0], self.y - other[1])
#         else:
#             raise TypeError(f"Cannot subtract {type(other)} from Coordinate")


class Dimensions(NamedTuple):
    height: int
    width: int

    @property
    def area(self):
        return self.width * self.height

    def __repr__(self):
        return f"Dimensions(height={self.height}, width={self.width})"


class Position(NamedTuple):
    lineno: int
    colno: int

    def __add__(self, other: "Position"):
        return Position(self.lineno + other.lineno, self.colno + other.colno)

    def __repr__(self):
        return f"Position(lineno={self.lineno}, colno={self.colno})"


class BoundingBox(NamedTuple):
    lineno: int
    colno: int
    height: int
    width: int

    @property
    def area(self):
        return self.width * self.height

    @property
    def first_lineno(self):
        return self.lineno

    @property
    def last_lineno(self):
        return self.lineno + self.height - 1

    @property
    def first_colno(self):
        return self.colno

    @property
    def last_colno(self):
        return self.colno + self.width - 1

    @property
    def top_left(self):
        return Position(self.first_lineno, self.first_colno)

    @property
    def top_right(self):
        return Position(self.first_lineno, self.last_lineno)

    @property
    def bottom_left(self):
        return Position(self.last_lineno, self.first_colno)

    @property
    def bottom_right(self):
        return Position(self.last_lineno, self.last_colno)

    @property
    def position(self):
        return Position(self.lineno, self.colno)

    @property
    def dimensions(self):
        return Dimensions(self.height, self.width)

    def __contains__(self, position: Union[Position, "BoundingBox"]):
        if isinstance(position, Position):
            return (
                self.first_lineno <= position.lineno <= self.last_lineno
                and self.first_colno <= position.colno <= self.last_colno
            )
        elif isinstance(position, BoundingBox):
            return (
                self.first_lineno <= position.first_lineno <= self.last_lineno
                and self.first_colno <= position.first_colno <= self.last_colno
                and self.first_lineno <= position.last_lineno <= self.last_lineno
                and self.first_colno <= position.last_colno <= self.last_colno
            )

    def __repr__(self):
        return f"BoundingBox(lineno={self.lineno}, colno={self.colno}, height={self.height}, width={self.width})"


class LineSpan(NamedTuple):
    """First is inclusive, last is exclusive"""

    first_lineno: int
    last_lineno: int

    def __contains__(self, lineno: int):
        return self.first_lineno <= lineno < self.last_lineno

from collections import namedtuple
from typing import NamedTuple


class Coordinate(NamedTuple):
    x: int
    y: int

    def __repr__(self):
        return f"Coordinate(x={self.x}, y={self.y})"

    def __str__(self):
        return f"[{self.x}, {self.y}]"

    def __add__(self, other):
        if isinstance(other, Coordinate):
            return Coordinate(self.x + other.x, self.y + other.y)
        elif isinstance(other, tuple) and len(other) == 2:
            return Coordinate(self.x + other[0], self.y + other[1])
        else:
            raise TypeError(f"Cannot add {type(other)} to Coordinate")

    def __sub__(self, other):
        if isinstance(other, Coordinate):
            return Coordinate(self.x - other.x, self.y - other.y)
        elif isinstance(other, tuple) and len(other) == 2:
            return Coordinate(self.x - other[0], self.y - other[1])
        else:
            raise TypeError(f"Cannot subtract {type(other)} from Coordinate")


class Dimensions(Coordinate):
    @property
    def width(self):
        return self.x

    @width.setter
    def width(self, value):
        self.y = value

    @property
    def height(self):
        return self.y

    @height.setter
    def height(self, value):
        self.y = value

    @property
    def area(self):
        return self.width * self.height

    def __repr__(self):
        return f"Dimensions(width={self.width}, height={self.height})"

    def __str__(self):
        return f"[{self.width}, {self.height}]"


class BoundingBox(NamedTuple):
    x: int
    y: int
    width: int
    height: int

    @property
    def area(self):
        return self.width * self.height

    @property
    def x2(self):
        return self.x + self.width - 1

    @property
    def y2(self):
        return self.y + self.height - 1

    @property
    def top_left(self):
        return Coordinate(self.x, self.y2)

    @property
    def top_right(self):
        return Coordinate(self.x2, self.y2)

    @property
    def bottom_left(self):
        return Coordinate(self.x, self.y)

    @property
    def bottom_right(self):
        return Coordinate(self.x2, self.y)

    @property
    def top(self):
        return self.y2

    @property
    def bottom(self):
        return self.y

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x2

    @property
    def coordinate(self):
        return Coordinate(self.x, self.y)

    @property
    def dimensions(self):
        return Dimensions(self.width, self.height)

    def __repr__(self):
        return f"BoundingBox(x={self.x}, y={self.y}, width={self.width}, height={self.height})"

    def __str__(self):
        return f"[{self.x}, {self.y}, {self.width}, {self.height}]"

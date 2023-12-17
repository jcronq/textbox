class ColoredString(str):
    def __new__(cls, value, color_pair: int = 0):
        obj = str.__new__(cls, value)
        obj.color_pair = color_pair
        return obj

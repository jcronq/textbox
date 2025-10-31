from enum import IntEnum


class ColorCode(IntEnum):
    WHITE = 0
    GREY = 1
    DARK_RED = 2
    GREEN = 3
    YELLOW = 4
    DARK_BLUE = 5
    DARK_PURPLE = 6
    LIGHT_BLUE = 7
    OFF_WHITE = 195
    LIGHT_PURPLE = 14
    OUTPUT_TEXT = 7

    # Backwards-compatible alias for typo
    OUPTUT_TEXT = 7  # Deprecated: Use OUTPUT_TEXT instead


# DEFAULT needs to be None for default color behavior, but IntEnum can't have None
# So we define it as a class attribute outside the enum values
ColorCode.DEFAULT = None

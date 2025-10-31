import pytest
from enum import IntEnum
from textbox.utils.color_code import ColorCode


def test_colorcode_is_intenum():
    """Test that ColorCode is a proper IntEnum.

    Bug #8 fix: ColorCode should inherit from IntEnum, not just import Enum.
    """
    # Verify ColorCode is an IntEnum subclass
    assert issubclass(ColorCode, IntEnum)

    # Verify all color values are integers
    assert isinstance(ColorCode.WHITE, int)
    assert isinstance(ColorCode.GREY, int)
    assert isinstance(ColorCode.DARK_RED, int)
    assert isinstance(ColorCode.GREEN, int)
    assert isinstance(ColorCode.YELLOW, int)
    assert isinstance(ColorCode.DARK_BLUE, int)
    assert isinstance(ColorCode.DARK_PURPLE, int)
    assert isinstance(ColorCode.LIGHT_BLUE, int)
    assert isinstance(ColorCode.OFF_WHITE, int)
    assert isinstance(ColorCode.LIGHT_PURPLE, int)


def test_colorcode_output_text_exists():
    """Test that OUTPUT_TEXT attribute exists (typo fix).

    Bug #8 fix: OUPTUT_TEXT was a typo, should be OUTPUT_TEXT.
    """
    # Verify OUTPUT_TEXT exists with correct value
    assert hasattr(ColorCode, 'OUTPUT_TEXT')
    assert ColorCode.OUTPUT_TEXT == 7


def test_colorcode_backwards_compatible_typo():
    """Test that OUPTUT_TEXT still exists for backwards compatibility."""
    # Verify the old typo still works for backwards compatibility
    assert hasattr(ColorCode, 'OUPTUT_TEXT')
    assert ColorCode.OUPTUT_TEXT == 7

    # Both should have the same value
    assert ColorCode.OUTPUT_TEXT == ColorCode.OUPTUT_TEXT


def test_colorcode_default_is_none():
    """Test that DEFAULT is None for default color behavior."""
    # DEFAULT needs to be None to represent "no color override"
    assert hasattr(ColorCode, 'DEFAULT')
    assert ColorCode.DEFAULT is None


def test_colorcode_values():
    """Test that ColorCode enum values are correct."""
    assert ColorCode.WHITE == 0
    assert ColorCode.GREY == 1
    assert ColorCode.DARK_RED == 2
    assert ColorCode.GREEN == 3
    assert ColorCode.YELLOW == 4
    assert ColorCode.DARK_BLUE == 5
    assert ColorCode.DARK_PURPLE == 6
    assert ColorCode.LIGHT_BLUE == 7
    assert ColorCode.OFF_WHITE == 195
    assert ColorCode.LIGHT_PURPLE == 14


def test_colorcode_enum_behavior():
    """Test that ColorCode behaves like a proper IntEnum."""
    # IntEnum members can be used in arithmetic operations
    assert ColorCode.WHITE + 1 == 1
    assert ColorCode.GREY - 1 == 0

    # IntEnum members can be compared with integers
    assert ColorCode.WHITE == 0
    assert ColorCode.GREY > 0
    assert ColorCode.DARK_RED < 10

    # IntEnum members can be used as dictionary keys
    color_dict = {ColorCode.WHITE: "white", ColorCode.GREY: "grey"}
    assert color_dict[ColorCode.WHITE] == "white"

    # IntEnum members can be used in integer contexts
    color_list = [None] * 3
    color_list[ColorCode.WHITE] = "first"
    color_list[ColorCode.GREY] = "second"
    assert color_list[0] == "first"
    assert color_list[1] == "second"

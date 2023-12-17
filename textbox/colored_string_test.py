from textbox.colored_string import ColoredString


def test_colorpair_exists():
    assert ColoredString("Hello").color_pair == 0
    assert ColoredString("Hello", color_pair=1).color_pair == 1
    assert ColoredString("Hello", 2).color_pair == 2


def test_slice():
    assert ColoredString("Hello")[:1].color_pair == 0


# def test_combination_persists():
#     orig_string = ColoredString("Hello", color_pair=1)
#     assert (orig_string[:2] + ColoredString("hi") + orig_string[2:]).color_pair == 1

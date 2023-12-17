from .rich_text import RichText


def test_rich_text_word_gen():
    expected_words = ["Hello,", " ", "world!", "\n", "This", " ", "is", " ", "a", " ", "test."]
    rt = RichText(text="Hello, world!  \nThis is a test.")

    words = list(rt.words())
    assert words == expected_words


def test_rich_text_word_gen_start_spacing():
    expected_words = ["  ", "Hello,", " ", "world!", "\n", "This", " ", "is", " ", "a", " ", "test."]
    rt = RichText(text="  Hello, world!  \nThis is a test.")

    words = list(rt.words())
    assert words == expected_words


def test_rich_text_word_gen_newline_spacing():
    expected_words = ["  ", "Hello,", " ", "world!", "\n", "  ", "This", " ", "is", " ", "a", " ", "test."]
    rt = RichText(text="  Hello, world!  \n  This is a test.")

    words = list(rt.words())
    assert words == expected_words


def test_rich_text_concatenation():
    rt1 = RichText(text="Hello, ")
    rt2 = RichText(text="world!")
    rt3 = RichText(text="This is a test.")
    rt1 += rt2
    rt1 += "  \n"
    rt1 += rt3
    assert rt1.text == "Hello, world!  \nThis is a test."


def test_clone_settings():
    rt1 = RichText(text="Hello, ")
    rt2 = rt1.clone_settings()
    assert rt1 is not rt2
    assert rt1.text == "Hello, "
    assert rt2.text == ""

    # No shared variables.
    rt2.text = "world"
    rt2.foreground_color = "red"
    rt2.background_color = "blue"
    rt2.bold = True
    rt2.underline = True
    rt2.italic = True
    rt2.strikethrough = True
    rt2.inverse = True
    assert rt1.text == "Hello, "
    assert rt2.text == "world"
    assert rt1.text != rt2.text
    assert rt1.foreground_color != rt2.foreground_color
    assert rt1.background_color != rt2.background_color
    assert rt1.bold != rt2.bold
    assert rt1.underline != rt2.underline
    assert rt1.italic != rt2.italic
    assert rt1.strikethrough != rt2.strikethrough
    assert rt1.inverse != rt2.inverse


def test_equality():
    rt1 = RichText(text="Hello, ")
    rt2 = RichText(text="Hello, ")
    assert rt1 == rt2

    rt1.background_color = "blue"
    assert rt1 != rt2

    rt2.background_color = "blue"
    assert rt1 == rt2

    rt1.foreground_color = "red"
    assert rt1 != rt2

    rt2.foreground_color = "red"
    assert rt1 == rt2

    rt1.bold = True
    assert rt1 != rt2

    rt2.bold = True
    assert rt1 == rt2

    rt1.underline = True
    assert rt1 != rt2

    rt2.underline = True
    assert rt1 == rt2

    rt1.italic = True
    assert rt1 != rt2

    rt2.italic = True
    assert rt1 == rt2

    rt1.strikethrough = True
    assert rt1 != rt2

    rt2.strikethrough = True
    assert rt1 == rt2

    rt1.inverse = True
    assert rt1 != rt2

    rt2.inverse = True
    assert rt1 == rt2

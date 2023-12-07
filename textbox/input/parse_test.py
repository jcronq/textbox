import pytest
from . import parse


def test_nop_function_parser():
    # Do not parse the input for functions
    assert parse.nop_function_parser("Hello") is None


def test_quit_function_parser():
    assert parse.quit_function_parser("bye") is None
    with pytest.raises(SystemExit):
        assert parse.quit_function_parser("quit()")
    with pytest.raises(SystemExit):
        assert parse.quit_function_parser("quit")
    with pytest.raises(SystemExit):
        assert parse.quit_function_parser(":quit")
    with pytest.raises(SystemExit):
        assert parse.quit_function_parser("/quit")
    with pytest.raises(SystemExit):
        assert parse.quit_function_parser(":q")
    with pytest.raises(SystemExit):
        assert parse.quit_function_parser("/q")


def test_is_yes_no_parser():
    assert parse.is_yes_no_parser("yes") is True
    assert parse.is_yes_no_parser("YeS") is True
    assert parse.is_yes_no_parser("YES") is True
    assert parse.is_yes_no_parser("Y") is True
    assert parse.is_yes_no_parser("y") is True

    assert parse.is_yes_no_parser("no") is True
    assert parse.is_yes_no_parser("No") is True
    assert parse.is_yes_no_parser("nO") is True
    assert parse.is_yes_no_parser("NO") is True
    assert parse.is_yes_no_parser("n") is True
    assert parse.is_yes_no_parser("N") is True

    assert parse.is_yes_no_parser("neS") is False
    assert parse.is_yes_no_parser("yo") is False
    assert parse.is_yes_no_parser("ye") is False
    assert parse.is_yes_no_parser("es") is False
    assert parse.is_yes_no_parser("o") is False
    assert parse.is_yes_no_parser("s") is False
    assert parse.is_yes_no_parser("ys") is False
    assert parse.is_yes_no_parser("e") is False

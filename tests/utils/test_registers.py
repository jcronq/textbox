"""Tests for the RegisterManager class."""

import pytest
from textbox.utils.registers import RegisterManager


class TestRegisterManagerBasics:
    """Test basic register operations."""

    def test_init_creates_empty_registers(self):
        """RegisterManager should initialize with empty registers."""
        rm = RegisterManager()
        assert rm.get_register("a") == ""
        assert rm.get_register("z") == ""
        assert rm.get_register('"') == ""  # unnamed register

    def test_init_creates_empty_numbered_registers(self):
        """RegisterManager should initialize numbered registers 0-9."""
        rm = RegisterManager()
        for i in range(10):
            assert rm.get_register(str(i)) == ""

    def test_set_and_get_named_register(self):
        """Should be able to set and get named registers."""
        rm = RegisterManager()
        rm.set_register("a", "test content")
        assert rm.get_register("a") == "test content"

    def test_set_multiple_named_registers(self):
        """Should be able to set multiple registers independently."""
        rm = RegisterManager()
        rm.set_register("a", "content a")
        rm.set_register("b", "content b")
        rm.set_register("z", "content z")
        assert rm.get_register("a") == "content a"
        assert rm.get_register("b") == "content b"
        assert rm.get_register("z") == "content z"

    def test_overwrite_register(self):
        """Setting a register should overwrite previous value."""
        rm = RegisterManager()
        rm.set_register("a", "first")
        rm.set_register("a", "second")
        assert rm.get_register("a") == "second"

    def test_get_nonexistent_register_returns_empty(self):
        """Getting an unset register should return empty string."""
        rm = RegisterManager()
        assert rm.get_register("x") == ""


class TestYankOperations:
    """Test yank operations."""

    def test_yank_to_named_register(self):
        """Yanking to a named register should store the text."""
        rm = RegisterManager()
        rm.yank_to_register("a", "yanked text")
        assert rm.get_register("a") == "yanked text"

    def test_yank_to_unnamed_register(self):
        """Yanking with None should use unnamed register."""
        rm = RegisterManager()
        rm.yank_to_register(None, "yanked text")
        assert rm.get_register('"') == "yanked text"

    def test_yank_updates_register_0(self):
        """Yanking should always update register 0."""
        rm = RegisterManager()
        rm.yank_to_register("a", "yanked text")
        assert rm.get_register("0") == "yanked text"

    def test_yank_to_unnamed_updates_both(self):
        """Yanking to unnamed should update both unnamed and 0."""
        rm = RegisterManager()
        rm.yank_to_register(None, "yanked text")
        assert rm.get_register('"') == "yanked text"
        assert rm.get_register("0") == "yanked text"

    def test_multiple_yanks_update_register_0(self):
        """Register 0 should always have most recent yank."""
        rm = RegisterManager()
        rm.yank_to_register("a", "first yank")
        rm.yank_to_register("b", "second yank")
        assert rm.get_register("0") == "second yank"
        assert rm.get_register("a") == "first yank"
        assert rm.get_register("b") == "second yank"


class TestDeleteOperations:
    """Test delete operations with numbered register history."""

    def test_delete_to_named_register(self):
        """Deleting to a named register should store the text."""
        rm = RegisterManager()
        rm.delete_to_register("a", "deleted text")
        assert rm.get_register("a") == "deleted text"

    def test_delete_to_unnamed_register(self):
        """Deleting with None should use unnamed register."""
        rm = RegisterManager()
        rm.delete_to_register(None, "deleted text")
        assert rm.get_register('"') == "deleted text"

    def test_delete_updates_register_1(self):
        """Delete should put text in register 1."""
        rm = RegisterManager()
        rm.delete_to_register(None, "deleted text")
        assert rm.get_register("1") == "deleted text"

    def test_delete_shifts_numbered_registers(self):
        """Subsequent deletes should shift numbered registers."""
        rm = RegisterManager()
        rm.delete_to_register(None, "delete 1")
        rm.delete_to_register(None, "delete 2")
        rm.delete_to_register(None, "delete 3")

        assert rm.get_register("1") == "delete 3"  # most recent
        assert rm.get_register("2") == "delete 2"
        assert rm.get_register("3") == "delete 1"  # oldest

    def test_delete_history_max_9_items(self):
        """Should only keep last 9 deletes in numbered registers."""
        rm = RegisterManager()
        for i in range(15):
            rm.delete_to_register(None, f"delete {i}")

        # Only last 9 should be kept
        assert rm.get_register("1") == "delete 14"
        assert rm.get_register("9") == "delete 6"

    def test_delete_to_named_register_no_numbered_update(self):
        """Deleting to named register should not update numbered registers."""
        rm = RegisterManager()
        rm.delete_to_register("a", "delete to a")
        assert rm.get_register("a") == "delete to a"
        assert rm.get_register("1") == ""  # should remain empty

    def test_yank_does_not_affect_numbered_registers(self):
        """Yanks should not shift numbered delete history."""
        rm = RegisterManager()
        rm.delete_to_register(None, "delete 1")
        rm.yank_to_register(None, "yank 1")
        rm.delete_to_register(None, "delete 2")

        assert rm.get_register("1") == "delete 2"
        assert rm.get_register("2") == "delete 1"
        assert rm.get_register("0") == "yank 1"  # yank register unchanged


class TestUnnamedRegister:
    """Test unnamed register behavior."""

    def test_unnamed_register_alias(self):
        """Empty string should be alias for unnamed register."""
        rm = RegisterManager()
        rm.set_register('"', "test")
        assert rm.get_register('"') == "test"

    def test_yank_updates_unnamed_when_none(self):
        """Yank with None should update unnamed register."""
        rm = RegisterManager()
        rm.yank_to_register(None, "yanked")
        assert rm.get_register('"') == "yanked"

    def test_delete_updates_unnamed_when_none(self):
        """Delete with None should update unnamed register."""
        rm = RegisterManager()
        rm.delete_to_register(None, "deleted")
        assert rm.get_register('"') == "deleted"


class TestRegisterValidation:
    """Test register name validation."""

    def test_invalid_register_name_raises_error(self):
        """Invalid register names should raise ValueError."""
        rm = RegisterManager()
        with pytest.raises(ValueError, match="Invalid register"):
            rm.set_register("@", "test")

    def test_valid_lowercase_letters(self):
        """Lowercase a-z should be valid."""
        rm = RegisterManager()
        for char in "abcdefghijklmnopqrstuvwxyz":
            rm.set_register(char, f"content {char}")
            assert rm.get_register(char) == f"content {char}"

    def test_valid_numbered_registers(self):
        """Digits 0-9 should be valid."""
        rm = RegisterManager()
        for i in range(10):
            rm.set_register(str(i), f"content {i}")
            assert rm.get_register(str(i)) == f"content {i}"

    def test_valid_unnamed_register(self):
        """Double quote should be valid for unnamed."""
        rm = RegisterManager()
        rm.set_register('"', "unnamed content")
        assert rm.get_register('"') == "unnamed content"

    def test_uppercase_letters_invalid(self):
        """Uppercase letters should be invalid (for now)."""
        rm = RegisterManager()
        with pytest.raises(ValueError, match="Invalid register"):
            rm.set_register("A", "test")


class TestEmptyContent:
    """Test handling of empty content."""

    def test_yank_empty_string(self):
        """Should be able to yank empty string."""
        rm = RegisterManager()
        rm.yank_to_register("a", "")
        assert rm.get_register("a") == ""

    def test_delete_empty_string(self):
        """Should be able to delete empty string."""
        rm = RegisterManager()
        rm.delete_to_register("a", "")
        assert rm.get_register("a") == ""

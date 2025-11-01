"""Vim-style register management for copy/paste operations.

This module implements a register system similar to vim's, supporting:
- Named registers (a-z)
- Numbered registers (0-9) for yank/delete history
- Special unnamed register (")
"""

from typing import Dict, List, Optional


class RegisterManager:
    """Manages vim-style registers for copy/paste operations.

    Registers:
        - Named registers: a-z (26 registers for user storage)
        - Numbered registers: 0-9 (yank and delete history)
            - 0: Most recent yank
            - 1-9: Delete history (1 is most recent delete)
        - Unnamed register: " (default register)

    Example:
        >>> rm = RegisterManager()
        >>> rm.yank_to_register("a", "hello")
        >>> rm.get_register("a")
        'hello'
        >>> rm.get_register("0")  # Also stored in yank register
        'hello'
    """

    def __init__(self) -> None:
        """Initialize register manager with empty registers."""
        # Named registers a-z
        self._registers: Dict[str, str] = {}

        # Numbered registers 0-9
        # 0 = most recent yank
        # 1-9 = delete history (1 is most recent)
        self._numbered_registers: List[str] = [""] * 10

        # Unnamed register (default)
        self._unnamed_register: str = ""

    def _validate_register_name(self, name: str) -> None:
        """Validate that register name is valid.

        Args:
            name: Register name to validate

        Raises:
            ValueError: If register name is invalid
        """
        valid_chars = set('abcdefghijklmnopqrstuvwxyz0123456789"')
        if name not in valid_chars:
            raise ValueError(f"Invalid register name: {name!r}")

    def set_register(self, name: str, value: str) -> None:
        """Set a register value directly.

        Args:
            name: Register name (a-z, 0-9, or ")
            value: Content to store in register

        Raises:
            ValueError: If register name is invalid
        """
        self._validate_register_name(name)

        if name == '"':
            self._unnamed_register = value
        elif name.isdigit():
            self._numbered_registers[int(name)] = value
        else:
            self._registers[name] = value

    def get_register(self, name: str) -> str:
        """Get a register value.

        Args:
            name: Register name (a-z, 0-9, or ")

        Returns:
            Register content, or empty string if not set

        Raises:
            ValueError: If register name is invalid
        """
        self._validate_register_name(name)

        if name == '"':
            return self._unnamed_register
        elif name.isdigit():
            return self._numbered_registers[int(name)]
        else:
            return self._registers.get(name, "")

    def yank_to_register(self, name: Optional[str], value: str) -> None:
        """Yank (copy) text to specified register.

        Yanking always updates register 0 (most recent yank).
        If no register is specified (None), updates unnamed register.

        Args:
            name: Register name (a-z) or None for unnamed register
            value: Text to yank
        """
        # Always update register 0 with most recent yank
        self._numbered_registers[0] = value

        if name is None:
            # Yank to unnamed register
            self._unnamed_register = value
        else:
            # Yank to specified named register
            self.set_register(name, value)

    def delete_to_register(self, name: Optional[str], value: str) -> None:
        """Delete text to specified register and update delete history.

        Deleting to unnamed register (name=None) shifts numbered delete history:
        - Content goes to register 1
        - Previous registers 1-8 shift to 2-9
        - Register 9 is lost

        Deleting to a named register does NOT affect numbered history.

        Args:
            name: Register name (a-z) or None for unnamed register
            value: Deleted text
        """
        if name is None:
            # Update unnamed register
            self._unnamed_register = value

            # Shift numbered delete history
            # Register 1 gets new delete, 2-9 shift down
            for i in range(8, 0, -1):  # 8 down to 1
                self._numbered_registers[i + 1] = self._numbered_registers[i]
            self._numbered_registers[1] = value
        else:
            # Delete to named register only (no numbered history update)
            self.set_register(name, value)

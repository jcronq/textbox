from typing import Callable, List


class KeyPressStateMachine:
    """A state machine for tracking the series of key presses that result in some action.

    Ex. pressing i enters insert mode immediately.  pressing d followed by d deletes the current line.
    """

    def __init__(self, matching_sequence: str, action: Callable[[], None]) -> None:
        self._state: int = 0
        self._key_sequence: List[str] = []
        self._key_sequence_string: str = ""
        self._key_sequence_string_history: List[str] = []
        self._key_sequence_string_history_ptr: int = 0
        self._key_sequence_string_history_max_size: int = 100

    def __repr__(self) -> str:
        return f"KeyPressStateMachine(state={self._state}, key_sequence={self._key_sequence})"

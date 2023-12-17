from typing import Callable


class KeyPressStateMachine:
    """A state machine for tracking the series of key presses that result in some action.

    Ex. pressing i enters insert mode immediately.  pressing d followed by d deletes the current line.
    """

    def __init__(self, matching_sequence: str, action: Callabe[[], None]):
        self._state = 0
        self._key_sequence = []
        self._key_sequence_string = ""
        self._key_sequence_string_history = []
        self._key_sequence_string_history_ptr = 0
        self._key_sequence_string_history_max_size = 100

    def __repr__(self):
        return f"KeyPressStateMachine(state={self._state}, key_sequence={self._key_sequence})"

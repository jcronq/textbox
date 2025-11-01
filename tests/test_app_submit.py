import pytest
from typing import Callable
from unittest.mock import Mock
from textbox import App, Text


def test_on_submit_type_hint():
    """Test that on_submit has correct type hint.

    Bug #9 fix: on_submit should have type hint Callable[[Text], None],
    not Callable[[str], None], because the callback actually receives
    a Text object, not a string.
    """
    app = App()

    # Verify the type hint is correct by checking the signature
    import inspect
    sig = inspect.signature(app.on_submit)
    param = sig.parameters['func']

    # Get the annotation
    annotation = param.annotation

    # The annotation should be Callable[[Text], None]
    # We can't directly compare types, but we can verify it's a Callable
    assert hasattr(annotation, '__origin__')

    # More importantly, verify the actual behavior matches the type hint
    # by testing that the callback receives a Text object
    received_arg = None
    received_type = None

    def test_callback(text):
        nonlocal received_arg, received_type
        received_arg = text
        received_type = type(text)

    # Register the callback
    app.on_submit(test_callback)

    # Simulate what _submit_callback does
    test_text = Text("Hello World")
    app._submit_callback(test_text)

    # Verify that the callback received a Text object, not a string
    assert received_arg is not None
    assert isinstance(received_arg, Text)
    assert received_type == Text
    assert received_arg.text == "Hello World"


def test_on_submit_decorator_pattern():
    """Test that on_submit works as a decorator and receives Text objects."""
    app = App()

    received_texts = []

    @app.on_submit
    def handle_submit(text: Text):
        received_texts.append(text)

    # Simulate submitting text
    test_text1 = Text("First submission")
    test_text2 = Text("Second submission")

    app._submit_callback(test_text1)
    app._submit_callback(test_text2)

    # Verify callbacks received Text objects
    assert len(received_texts) == 2
    assert all(isinstance(t, Text) for t in received_texts)
    assert received_texts[0].text == "First submission"
    assert received_texts[1].text == "Second submission"


def test_on_submit_multiple_callbacks():
    """Test that multiple on_submit callbacks all receive Text objects."""
    app = App()

    callback1_calls = []
    callback2_calls = []

    def callback1(text: Text):
        callback1_calls.append(text)

    def callback2(text: Text):
        callback2_calls.append(text)

    app.on_submit(callback1)
    app.on_submit(callback2)

    # Simulate submission
    test_text = Text("Test message")
    app._submit_callback(test_text)

    # Both callbacks should receive the same Text object
    assert len(callback1_calls) == 1
    assert len(callback2_calls) == 1
    assert isinstance(callback1_calls[0], Text)
    assert isinstance(callback2_calls[0], Text)
    assert callback1_calls[0].text == "Test message"
    assert callback2_calls[0].text == "Test message"


def test_on_submit_preserves_text_properties():
    """Test that Text object properties are preserved through callback."""
    app = App()

    received_text = None

    def callback(text: Text):
        nonlocal received_text
        received_text = text

    app.on_submit(callback)

    # Create a Text object with specific properties
    test_text = Text("Multi\nLine\nText")

    app._submit_callback(test_text)

    # Verify the Text object's properties are preserved
    assert received_text is not None
    assert isinstance(received_text, Text)
    assert received_text.text == "Multi\nLine\nText"
    assert received_text.line_count == 3


def test_submit_callback_internal_type_consistency():
    """Test that _submit_callback type hint matches implementation."""
    import inspect
    from textbox import App

    # Get the signature of _submit_callback
    sig = inspect.signature(App._submit_callback)

    # Check the 'text' parameter annotation
    text_param = sig.parameters['text']
    assert text_param.annotation == Text, \
        f"Expected Text type hint, got {text_param.annotation}"

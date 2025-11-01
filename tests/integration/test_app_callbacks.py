"""
Integration tests for App callback system.

Tests the on_submit decorator, callback registration, and callback invocation.
Target: Improve App coverage.
"""

import pytest
from textbox import App, Text, TextLine, TextSegment


class TestOnSubmitDecorator:
    """Test the @app.on_submit() decorator."""

    def test_on_submit_registers_callback(self):
        """Test that @on_submit decorator registers callback."""
        app = App()

        @app.on_submit
        def handler(text):
            pass

        assert len(app._submit_callbacks) == 1
        assert app._submit_callbacks[0] == handler

    def test_on_submit_returns_function(self):
        """Test that decorator returns the original function."""
        app = App()

        @app.on_submit
        def handler(text):
            return "result"

        assert handler(Text()) == "result"

    def test_multiple_on_submit_callbacks(self):
        """Test that multiple submit callbacks can be registered."""
        app = App()

        @app.on_submit
        def handler1(text):
            pass

        @app.on_submit
        def handler2(text):
            pass

        @app.on_submit
        def handler3(text):
            pass

        assert len(app._submit_callbacks) == 3
        assert handler1 in app._submit_callbacks
        assert handler2 in app._submit_callbacks
        assert handler3 in app._submit_callbacks


class TestSubmitCallback:
    """Test _submit_callback internal method."""

    def test_submit_callback_invokes_handlers(self):
        """Test that _submit_callback calls all registered handlers."""
        app = App()
        calls = []

        @app.on_submit
        def handler1(text):
            calls.append(('handler1', text))

        @app.on_submit
        def handler2(text):
            calls.append(('handler2', text))

        test_text = Text("test content")
        app._submit_callback(test_text)

        assert len(calls) == 2
        assert calls[0][0] == 'handler1'
        assert calls[1][0] == 'handler2'
        assert calls[0][1] == test_text
        assert calls[1][1] == test_text

    def test_submit_callback_receives_text_object(self):
        """Test that callbacks receive Text object, not string."""
        app = App()
        received_types = []

        @app.on_submit
        def handler(text):
            received_types.append(type(text))

        test_text = Text("test")
        app._submit_callback(test_text)

        assert len(received_types) == 1
        assert received_types[0] == Text

    def test_submit_callback_with_empty_callbacks(self):
        """Test that _submit_callback works with no registered callbacks."""
        app = App()
        text = Text("test")

        # Should not raise exception
        app._submit_callback(text)

    def test_submit_callback_order_preserved(self):
        """Test that callbacks are called in registration order."""
        app = App()
        call_order = []

        @app.on_submit
        def first(text):
            call_order.append(1)

        @app.on_submit
        def second(text):
            call_order.append(2)

        @app.on_submit
        def third(text):
            call_order.append(3)

        app._submit_callback(Text())

        assert call_order == [1, 2, 3]

    def test_submit_callback_exception_handling(self):
        """Test behavior when a callback raises an exception."""
        app = App()
        calls = []

        @app.on_submit
        def handler1(text):
            calls.append('handler1')

        @app.on_submit
        def handler2(text):
            calls.append('handler2')
            raise ValueError("Test exception")

        @app.on_submit
        def handler3(text):
            calls.append('handler3')

        # If no exception handling, this will raise
        # If exception is caught, handler3 might still run
        try:
            app._submit_callback(Text())
        except ValueError:
            pass

        # At least handler1 should have run
        assert 'handler1' in calls

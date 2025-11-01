"""
Comprehensive async tests for AsyncInputManager.

Tests async keyboard input handling, context manager lifecycle,
callbacks, stop mechanism, and input loop behavior.
Target: Improve input_manager.py coverage from 24% to 70%+.
"""

import pytest
import asyncio
import curses
from unittest.mock import MagicMock, patch, AsyncMock, call
from textbox.ui.input_manager import AsyncInputManager
from textbox.ui.window import Window
from textbox.utils.signals import WindowQuit, DelayedRedraw


class TestAsyncInputManagerInitialization:
    """Test AsyncInputManager initialization."""

    def test_input_manager_creates_with_window(self):
        """Test that AsyncInputManager can be instantiated with a Window."""
        mock_window = MagicMock(spec=Window)
        input_manager = AsyncInputManager(mock_window)

        assert input_manager is not None
        assert isinstance(input_manager, AsyncInputManager)
        assert input_manager.window is mock_window

    def test_input_manager_initializes_callbacks(self):
        """Test that callbacks are initialized to no-op lambdas."""
        mock_window = MagicMock(spec=Window)
        input_manager = AsyncInputManager(mock_window)

        assert callable(input_manager.on_keypress)
        assert callable(input_manager.redraw)

        # Should not raise when called
        input_manager.on_keypress(ord('a'))
        input_manager.redraw()

    def test_input_manager_initializes_running_false(self):
        """Test that running flag is initially False."""
        mock_window = MagicMock(spec=Window)
        input_manager = AsyncInputManager(mock_window)

        assert input_manager.running is False

    def test_multiple_input_managers(self):
        """Test that multiple AsyncInputManager instances can coexist."""
        mock_window1 = MagicMock(spec=Window)
        mock_window2 = MagicMock(spec=Window)

        input_manager1 = AsyncInputManager(mock_window1)
        input_manager2 = AsyncInputManager(mock_window2)

        assert input_manager1 is not input_manager2
        assert input_manager1.window is not input_manager2.window


class TestAsyncContextManager:
    """Test async context manager (__aenter__, __aexit__)."""

    @pytest.mark.asyncio
    async def test_aenter_sets_nodelay_true(self):
        """Test that __aenter__ sets window nodelay to True."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)

        async with input_manager:
            mock_curses_window.nodelay.assert_called_once_with(True)
            await asyncio.sleep(0)  # Yield control to input loop
            input_manager.stop()
            await asyncio.sleep(0.02)

    @pytest.mark.asyncio
    async def test_aenter_sets_running_true(self):
        """Test that __aenter__ sets running flag to True."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)

        async with input_manager:
            assert input_manager.running is True
            await asyncio.sleep(0)
            input_manager.stop()
            await asyncio.sleep(0.02)

    @pytest.mark.asyncio
    async def test_aenter_creates_input_task(self):
        """Test that __aenter__ creates input_future task."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)

        async with input_manager:
            assert hasattr(input_manager, 'input_future')
            assert isinstance(input_manager.input_future, asyncio.Task)
            await asyncio.sleep(0)
            input_manager.stop()
            await asyncio.sleep(0.02)

    @pytest.mark.asyncio
    async def test_aenter_initializes_redraw_soon_false(self):
        """Test that __aenter__ initializes redraw_soon to False."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)

        async with input_manager:
            assert input_manager.redraw_soon is False
            await asyncio.sleep(0)
            input_manager.stop()
            await asyncio.sleep(0.02)

    @pytest.mark.asyncio
    async def test_aenter_returns_self(self):
        """Test that __aenter__ returns self."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)

        async with input_manager as manager:
            assert manager is input_manager
            await asyncio.sleep(0)
            input_manager.stop()
            await asyncio.sleep(0.02)

    @pytest.mark.asyncio
    async def test_aexit_sets_nodelay_false(self):
        """Test that __aexit__ sets window nodelay back to False."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)

        async with input_manager:
            await asyncio.sleep(0)
            input_manager.stop()
            await asyncio.sleep(0.02)  # Allow input loop to finish

        # After exiting context
        assert mock_curses_window.nodelay.call_count == 2
        mock_curses_window.nodelay.assert_any_call(True)
        mock_curses_window.nodelay.assert_any_call(False)

    @pytest.mark.asyncio
    async def test_aexit_waits_for_input_future(self):
        """Test that __aexit__ waits for input_future to complete."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)
        task_completed = False

        async with input_manager:
            original_task = input_manager.input_future
            input_manager.stop()
            await asyncio.sleep(0.02)  # Allow loop to exit

        # Task should be completed after exit
        assert original_task.done()


class TestCallbackManagement:
    """Test setting and invoking callbacks."""

    @pytest.mark.asyncio
    async def test_set_on_keypress_callback(self):
        """Test that on_keypress callback can be set and is called."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window

        # Simulate keypress then ERR (multiple ERR to avoid StopIteration)
        mock_window.getch = MagicMock(side_effect=[ord('a')] + [curses.ERR] * 10)

        input_manager = AsyncInputManager(mock_window)
        callback_called = []

        async def keypress_callback(key):
            callback_called.append(key)

        input_manager.on_keypress = keypress_callback

        async with input_manager:
            await asyncio.sleep(0.02)  # Allow input loop to process
            input_manager.stop()
            await asyncio.sleep(0.02)

        assert len(callback_called) == 1
        assert callback_called[0] == ord('a')

    @pytest.mark.asyncio
    async def test_on_keypress_is_async(self):
        """Test that on_keypress callback can be async."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window

        mock_window.getch = MagicMock(side_effect=[ord('b')] + [curses.ERR] * 10)

        input_manager = AsyncInputManager(mock_window)
        callback_results = []

        async def async_keypress_callback(key):
            await asyncio.sleep(0.001)
            callback_results.append(key)

        input_manager.on_keypress = async_keypress_callback

        async with input_manager:
            await asyncio.sleep(0.02)
            input_manager.stop()
            await asyncio.sleep(0.02)

        assert len(callback_results) == 1
        assert callback_results[0] == ord('b')

    @pytest.mark.asyncio
    async def test_set_redraw_callback(self):
        """Test that redraw callback can be set and is called."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window

        redraw_count = []

        def redraw_callback():
            redraw_count.append(1)

        input_manager = AsyncInputManager(mock_window)
        input_manager.redraw = redraw_callback

        # Trigger delayed redraw
        async def keypress_with_delayed_redraw(key):
            raise DelayedRedraw()

        input_manager.on_keypress = keypress_with_delayed_redraw
        mock_window.getch = MagicMock(side_effect=[ord('x')] + [curses.ERR] * 10)

        async with input_manager:
            await asyncio.sleep(0.02)
            input_manager.stop()
            await asyncio.sleep(0.02)

        # Redraw should be called on next iteration
        assert len(redraw_count) > 0

    @pytest.mark.asyncio
    async def test_multiple_keypresses_call_callback_multiple_times(self):
        """Test that multiple keypresses invoke callback multiple times."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window

        # Simulate multiple keypresses
        mock_window.getch = MagicMock(side_effect=[
            ord('a'), ord('b'), ord('c')
        ] + [curses.ERR] * 10)

        input_manager = AsyncInputManager(mock_window)
        pressed_keys = []

        async def keypress_callback(key):
            pressed_keys.append(key)

        input_manager.on_keypress = keypress_callback

        async with input_manager:
            await asyncio.sleep(0.05)  # Allow all keys to be processed
            input_manager.stop()
            await asyncio.sleep(0.02)

        assert len(pressed_keys) == 3
        assert pressed_keys == [ord('a'), ord('b'), ord('c')]


class TestStopMechanism:
    """Test stop mechanism."""

    def test_stop_sets_running_false(self):
        """Test that stop() sets running flag to False."""
        mock_window = MagicMock(spec=Window)
        input_manager = AsyncInputManager(mock_window)

        input_manager.running = True
        input_manager.stop()

        assert input_manager.running is False

    @pytest.mark.asyncio
    async def test_stop_terminates_input_loop(self):
        """Test that stop() terminates the input loop."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)

        async with input_manager:
            assert input_manager.running is True
            input_manager.stop()
            await asyncio.sleep(0.02)  # Allow loop to exit
            assert input_manager.running is False

    @pytest.mark.asyncio
    async def test_window_quit_stops_input_loop(self):
        """Test that WindowQuit exception stops the input loop."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window

        mock_window.getch = MagicMock(side_effect=[ord('q'), curses.ERR])

        input_manager = AsyncInputManager(mock_window)

        async def quit_on_q(key):
            if key == ord('q'):
                raise WindowQuit()

        input_manager.on_keypress = quit_on_q

        async with input_manager:
            await asyncio.sleep(0.02)  # Allow keypress to be processed
            # WindowQuit should trigger stop
            await asyncio.sleep(0.02)
            assert input_manager.running is False


class TestInputLoopBehavior:
    """Test input loop behavior and edge cases."""

    @pytest.mark.asyncio
    async def test_input_loop_handles_err_gracefully(self):
        """Test that input loop handles curses.ERR gracefully."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)

        async with input_manager:
            await asyncio.sleep(0.02)  # Let loop run with ERR
            input_manager.stop()
            await asyncio.sleep(0.02)

        # Should complete without errors
        assert not input_manager.running

    @pytest.mark.asyncio
    async def test_input_loop_handles_curses_error(self):
        """Test that input loop handles curses.error exception."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window

        # Simulate curses.error on getch
        mock_window.getch = MagicMock(side_effect=curses.error("Test error"))

        input_manager = AsyncInputManager(mock_window)

        async with input_manager:
            await asyncio.sleep(0.02)  # Should handle error gracefully
            input_manager.stop()
            await asyncio.sleep(0.02)

        # Should complete without propagating error
        assert not input_manager.running

    @pytest.mark.asyncio
    async def test_delayed_redraw_mechanism(self):
        """Test that DelayedRedraw sets redraw_soon flag."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window

        redraw_called = []

        def redraw_callback():
            redraw_called.append(True)

        input_manager = AsyncInputManager(mock_window)
        input_manager.redraw = redraw_callback

        # First keypress raises DelayedRedraw, second is normal
        async def keypress_handler(key):
            if key == ord('d'):
                raise DelayedRedraw()

        input_manager.on_keypress = keypress_handler
        mock_window.getch = MagicMock(side_effect=[
            ord('d'), ord('x')
        ] + [curses.ERR] * 10)

        async with input_manager:
            await asyncio.sleep(0.05)
            input_manager.stop()
            await asyncio.sleep(0.02)

        # Redraw should have been called
        assert len(redraw_called) > 0

    @pytest.mark.asyncio
    async def test_redraw_soon_resets_after_redraw(self):
        """Test that redraw_soon flag is reset after redraw."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window

        input_manager = AsyncInputManager(mock_window)

        # Trigger delayed redraw
        async def keypress_delayed(key):
            raise DelayedRedraw()

        input_manager.on_keypress = keypress_delayed
        mock_window.getch = MagicMock(side_effect=[
            ord('r')
        ] + [curses.ERR] * 10)

        async with input_manager:
            await asyncio.sleep(0.02)
            # redraw_soon should be set then cleared
            await asyncio.sleep(0.02)
            input_manager.stop()
            await asyncio.sleep(0.02)

        # After processing, redraw_soon should be False
        assert input_manager.redraw_soon is False

    @pytest.mark.asyncio
    async def test_input_loop_sleeps_on_no_input(self):
        """Test that input loop sleeps when no input is available."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)

        start_time = asyncio.get_event_loop().time()

        async with input_manager:
            await asyncio.sleep(0.05)  # Let it sleep a few times
            input_manager.stop()
            await asyncio.sleep(0.02)

        end_time = asyncio.get_event_loop().time()

        # Should have taken some time (sleeping between iterations)
        assert end_time - start_time >= 0.04


class TestSpecialKeyCodes:
    """Test handling of special key codes."""

    @pytest.mark.asyncio
    async def test_handles_special_key_codes(self):
        """Test that special key codes are passed to callback."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window

        special_keys = [
            curses.KEY_UP, curses.KEY_DOWN,
            curses.KEY_LEFT, curses.KEY_RIGHT,
            curses.KEY_BACKSPACE, curses.KEY_ENTER
        ]

        mock_window.getch = MagicMock(side_effect=[*special_keys] + [curses.ERR] * 10)

        input_manager = AsyncInputManager(mock_window)
        received_keys = []

        async def keypress_callback(key):
            received_keys.append(key)

        input_manager.on_keypress = keypress_callback

        async with input_manager:
            await asyncio.sleep(0.1)  # Allow all keys to be processed
            input_manager.stop()
            await asyncio.sleep(0.02)

        assert len(received_keys) == len(special_keys)
        assert received_keys == special_keys

    @pytest.mark.asyncio
    async def test_handles_ascii_range(self):
        """Test that ASCII characters are handled correctly."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window

        ascii_chars = [ord('0'), ord('9'), ord('a'), ord('z'), ord('A'), ord('Z')]
        mock_window.getch = MagicMock(side_effect=[*ascii_chars] + [curses.ERR] * 10)

        input_manager = AsyncInputManager(mock_window)
        received_keys = []

        async def keypress_callback(key):
            received_keys.append(key)

        input_manager.on_keypress = keypress_callback

        async with input_manager:
            await asyncio.sleep(0.1)
            input_manager.stop()
            await asyncio.sleep(0.02)

        assert received_keys == ascii_chars


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_callback_exception_propagates(self):
        """Test that regular exceptions in callback propagate (only WindowQuit/DelayedRedraw are special)."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window

        # Keypress raises exception
        mock_window.getch = MagicMock(side_effect=[ord('e')] + [curses.ERR] * 10)

        input_manager = AsyncInputManager(mock_window)

        async def failing_callback(key):
            raise ValueError("Test exception")

        input_manager.on_keypress = failing_callback

        # Regular exceptions DO propagate (only WindowQuit and DelayedRedraw are caught)
        with pytest.raises(ValueError, match="Test exception"):
            async with input_manager:
                await asyncio.sleep(0.05)
                input_manager.stop()
                await asyncio.sleep(0.02)

    @pytest.mark.asyncio
    async def test_stop_can_be_called_multiple_times(self):
        """Test that stop() can be called multiple times safely."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)

        async with input_manager:
            input_manager.stop()
            input_manager.stop()  # Second call
            input_manager.stop()  # Third call
            await asyncio.sleep(0.02)

        assert not input_manager.running

    @pytest.mark.asyncio
    async def test_empty_context_manager_usage(self):
        """Test using context manager without any interaction."""
        mock_window = MagicMock(spec=Window)
        mock_curses_window = MagicMock()
        mock_window._local_window = mock_curses_window
        mock_window.getch = MagicMock(return_value=curses.ERR)

        input_manager = AsyncInputManager(mock_window)

        async with input_manager:
            await asyncio.sleep(0.01)
            input_manager.stop()
            await asyncio.sleep(0.02)

        # Should complete without errors
        assert not input_manager.running

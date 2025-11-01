"""
Integration tests for App lifecycle - creation, start, stop.

These tests verify the App class initialization, lifecycle methods,
and proper cleanup. Target: Improve App coverage from 33% to 80%.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from textbox import App
from textbox.utils.signals import WindowQuit


class TestAppInstantiation:
    """Test App object creation and initialization."""

    def test_app_creates_successfully(self):
        """Test that App can be instantiated."""
        app = App()
        assert app is not None
        assert isinstance(app, App)

    def test_app_initializes_callbacks_list(self):
        """Test that submit callbacks list is initialized empty."""
        app = App()
        assert app._submit_callbacks == []
        assert isinstance(app._submit_callbacks, list)

    def test_app_initializes_commands_dict(self):
        """Test that user commands dict is initialized with 'help'."""
        app = App()
        assert 'help' in app._user_defined_commands
        assert isinstance(app._user_defined_commands, dict)

    def test_app_initializes_help_dict(self):
        """Test that command help dict is initialized."""
        app = App()
        assert 'help' in app._user_defined_commands_help
        assert app._user_defined_commands_help['help'] is not None

    def test_app_workspace_initially_none(self):
        """Test that workspace is None before start()."""
        app = App()
        assert app.workspace is None

    def test_multiple_app_instances(self):
        """Test that multiple App instances can coexist."""
        app1 = App()
        app2 = App()
        assert app1 is not app2
        assert app1._submit_callbacks is not app2._submit_callbacks


class TestAppStop:
    """Test App stop method."""

    def test_stop_raises_window_quit(self):
        """Test that stop() raises WindowQuit signal."""
        app = App()
        with pytest.raises(WindowQuit):
            app.stop()

    def test_stop_can_be_caught(self):
        """Test that WindowQuit can be caught and handled."""
        app = App()
        try:
            app.stop()
            pytest.fail("stop() should raise WindowQuit")
        except WindowQuit:
            pass  # Expected


class TestAppDefaultHelp:
    """Test default help command functionality."""

    def test_default_help_exists(self):
        """Test that default help command is registered."""
        app = App()
        assert 'help' in app._user_defined_commands
        assert callable(app._user_defined_commands['help'])

    def test_default_help_has_description(self):
        """Test that default help has a description."""
        app = App()
        assert 'help' in app._user_defined_commands_help
        help_text = app._user_defined_commands_help['help']
        assert help_text is not None
        assert len(help_text) > 0

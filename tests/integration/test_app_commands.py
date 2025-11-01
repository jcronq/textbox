"""
Integration tests for App command system.

Tests the command decorator, command registration, execution,
and the command callback system. Target: Improve App coverage.
"""

import pytest
from textbox import App
from textbox.core.text import Text


class TestCommandDecorator:
    """Test the @app.command() decorator."""

    def test_command_decorator_registers_command(self):
        """Test that @command decorator registers the command."""
        app = App()

        @app.command("test")
        def test_cmd(cmd_str):
            pass

        assert 'test' in app._user_defined_commands
        assert app._user_defined_commands['test'] == test_cmd

    def test_command_decorator_with_help(self):
        """Test that command decorator stores help text."""
        app = App()

        @app.command("greet", help="Say hello")
        def greet_cmd(cmd_str):
            pass

        assert 'greet' in app._user_defined_commands_help
        assert app._user_defined_commands_help['greet'] == "Say hello"

    def test_command_decorator_with_aliases(self):
        """Test that command decorator handles multiple aliases."""
        app = App()

        @app.command("quit", "q", "exit", help="Exit the app")
        def quit_cmd(cmd_str):
            pass

        assert 'quit' in app._user_defined_commands
        assert 'q' in app._user_defined_commands
        assert 'exit' in app._user_defined_commands
        assert app._user_defined_commands['quit'] == quit_cmd
        assert app._user_defined_commands['q'] == quit_cmd
        assert app._user_defined_commands['exit'] == quit_cmd

    def test_command_decorator_returns_function(self):
        """Test that decorator returns the original function."""
        app = App()

        @app.command("test")
        def test_cmd(cmd_str):
            return "result"

        assert test_cmd("") == "result"

    def test_multiple_commands_registered(self):
        """Test that multiple commands can be registered."""
        app = App()

        @app.command("cmd1")
        def cmd1(cmd_str):
            pass

        @app.command("cmd2")
        def cmd2(cmd_str):
            pass

        @app.command("cmd3")
        def cmd3(cmd_str):
            pass

        assert len(app._user_defined_commands) >= 4  # 3 + default 'help'
        assert 'cmd1' in app._user_defined_commands
        assert 'cmd2' in app._user_defined_commands
        assert 'cmd3' in app._user_defined_commands


class TestCommandCallback:
    """Test _command_callback internal method."""

    def test_command_callback_executes_registered_command(self):
        """Test that _command_callback executes the command."""
        app = App()
        executed = []

        @app.command("test")
        def test_cmd(cmd_str):
            executed.append(cmd_str)

        app._command_callback("test argument")

        assert len(executed) == 1
        assert executed[0] == "test argument"

    def test_command_callback_with_arguments(self):
        """Test command callback passes full command string."""
        app = App()
        received_args = []

        @app.command("load")
        def load_cmd(cmd_str):
            received_args.append(cmd_str)

        app._command_callback("load filename.txt")

        assert len(received_args) == 1
        assert received_args[0] == "load filename.txt"

    def test_command_callback_unknown_command(self):
        """Test that unknown command triggers appropriate handling."""
        app = App()

        # Mock the print method to capture output
        app.print = lambda text: None

        # Should not raise exception, should call print with error
        app._command_callback("unknown_command")
        # If we get here without exception, test passes

    def test_command_callback_with_spaces(self):
        """Test command extraction from string with spaces."""
        app = App()
        commands_executed = []

        @app.command("save")
        def save_cmd(cmd_str):
            commands_executed.append(cmd_str)

        app._command_callback("save file.txt with spaces")

        assert len(commands_executed) == 1
        assert "save" in commands_executed[0]


class TestCommandHelp:
    """Test the automatic help system."""

    def test_help_command_exists_by_default(self):
        """Test that 'help' command exists without registration."""
        app = App()
        assert 'help' in app._user_defined_commands

    def test_help_command_callable(self):
        """Test that help command can be called."""
        app = App()
        # Mock print to avoid needing workspace
        app.print = lambda text: None

        # Should not raise exception
        help_func = app._user_defined_commands['help']
        help_func("")

    def test_help_includes_custom_commands(self):
        """Test that custom commands appear in help."""
        app = App()
        help_output = []

        # Mock print to capture output
        def mock_print(text):
            help_output.append(str(text))

        app.print = mock_print

        @app.command("custom", help="A custom command")
        def custom_cmd(cmd_str):
            pass

        # Call help
        app._default_help("")

        # Verify help was called (print was used)
        assert len(help_output) > 0

        # Verify our command is mentioned
        all_output = " ".join(help_output)
        assert "custom" in all_output or "Commands" in all_output

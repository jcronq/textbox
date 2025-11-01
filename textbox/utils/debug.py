"""Debug utilities for textbox applications.

Provides debug overlay, enhanced logging, and diagnostic tools.
"""

from typing import Dict, Any, Optional
import logging
import time
from dataclasses import dataclass, field


@dataclass
class DebugStats:
    """Statistics for debug overlay."""

    keypress_count: int = 0
    mode_changes: int = 0
    text_changes: int = 0
    commands_executed: int = 0
    undo_count: int = 0
    redo_count: int = 0
    last_keypress: Optional[str] = None
    last_command: Optional[str] = None
    start_time: float = field(default_factory=time.time)

    @property
    def uptime(self) -> float:
        """Get application uptime in seconds."""
        return time.time() - self.start_time


class DebugOverlay:
    """Debug overlay for displaying internal state.

    Shows real-time information about application state in a corner
    of the screen for debugging purposes.

    Example:
        >>> overlay = DebugOverlay()
        >>> overlay.update({'mode': 'COMMAND', 'cursor': 'Position(0, 5)'})
        >>> overlay.render()
    """

    def __init__(self, enabled: bool = True):
        """Initialize debug overlay.

        Args:
            enabled: Whether debug overlay is active
        """
        self.enabled = enabled
        self.state: Dict[str, Any] = {}
        self.stats = DebugStats()

    def update(self, updates: Dict[str, Any]) -> None:
        """Update overlay state.

        Args:
            updates: Dictionary of state updates
        """
        if not self.enabled:
            return
        self.state.update(updates)

    def increment_stat(self, stat_name: str) -> None:
        """Increment a statistic counter.

        Args:
            stat_name: Name of the stat to increment
        """
        if not self.enabled:
            return
        if hasattr(self.stats, stat_name):
            current = getattr(self.stats, stat_name)
            if isinstance(current, int):
                setattr(self.stats, stat_name, current + 1)

    def set_stat(self, stat_name: str, value: Any) -> None:
        """Set a statistic value.

        Args:
            stat_name: Name of the stat
            value: Value to set
        """
        if not self.enabled:
            return
        if hasattr(self.stats, stat_name):
            setattr(self.stats, stat_name, value)

    def get_debug_info(self) -> Dict[str, str]:
        """Get formatted debug information.

        Returns:
            Dictionary of debug key-value pairs
        """
        if not self.enabled:
            return {}

        info = {
            'Mode': str(self.state.get('mode', 'N/A')),
            'Cursor': str(self.state.get('cursor', 'N/A')),
            'Focus': str(self.state.get('focused', 'N/A')),
            'Text Len': str(self.state.get('text_length', 'N/A')),
            'Selection': str(self.state.get('selection', 'None')),
            'Keypresses': str(self.stats.keypress_count),
            'Mode Changes': str(self.stats.mode_changes),
            'Text Changes': str(self.stats.text_changes),
            'Commands': str(self.stats.commands_executed),
            'Undo': str(self.stats.undo_count),
            'Redo': str(self.stats.redo_count),
            'Uptime': f"{self.stats.uptime:.1f}s",
        }

        if self.stats.last_keypress:
            info['Last Key'] = self.stats.last_keypress
        if self.stats.last_command:
            info['Last Cmd'] = self.stats.last_command

        return info

    def render(self) -> str:
        """Render debug overlay as string.

        Returns:
            Formatted debug information
        """
        if not self.enabled:
            return ""

        info = self.get_debug_info()
        lines = ["=== DEBUG ==="]
        for key, value in info.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)


def setup_debug_logging(filename: str = "textbox_debug.log",
                       level: int = logging.DEBUG) -> logging.Logger:
    """Setup enhanced debug logging.

    Args:
        filename: Log file path
        level: Logging level

    Returns:
        Configured logger

    Example:
        >>> logger = setup_debug_logging()
        >>> logger.debug("Debug message")
    """
    logger = logging.getLogger("textbox.debug")
    logger.setLevel(level)

    # File handler
    fh = logging.FileHandler(filename, mode='w')
    fh.setLevel(level)

    # Detailed formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - '
        '%(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    logger.info("=" * 60)
    logger.info("Debug logging initialized")
    logger.info("=" * 60)

    return logger


def log_event(logger: logging.Logger, event_type: str, **kwargs) -> None:
    """Log an event with structured data.

    Args:
        logger: Logger instance
        event_type: Type of event
        **kwargs: Event data

    Example:
        >>> log_event(logger, "keypress", key="i", mode="COMMAND")
    """
    data = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.debug(f"[{event_type}] {data}")


class PerformanceTimer:
    """Simple performance timer for debugging.

    Example:
        >>> timer = PerformanceTimer()
        >>> with timer.measure("operation"):
        ...     # do work
        ...     pass
        >>> print(timer.get_results())
    """

    def __init__(self):
        """Initialize performance timer."""
        self.timings: Dict[str, list] = {}
        self._current_operation: Optional[str] = None
        self._start_time: Optional[float] = None

    def start(self, operation: str) -> None:
        """Start timing an operation.

        Args:
            operation: Operation name
        """
        self._current_operation = operation
        self._start_time = time.time()

    def stop(self) -> Optional[float]:
        """Stop timing current operation.

        Returns:
            Duration in seconds, or None if no operation was started
        """
        if self._current_operation is None or self._start_time is None:
            return None

        duration = time.time() - self._start_time

        if self._current_operation not in self.timings:
            self.timings[self._current_operation] = []
        self.timings[self._current_operation].append(duration)

        self._current_operation = None
        self._start_time = None

        return duration

    def measure(self, operation: str):
        """Context manager for measuring operation duration.

        Args:
            operation: Operation name

        Example:
            >>> timer = PerformanceTimer()
            >>> with timer.measure("render"):
            ...     render_screen()
        """
        return _TimerContext(self, operation)

    def get_results(self) -> Dict[str, Dict[str, float]]:
        """Get timing results with statistics.

        Returns:
            Dictionary with operation stats (count, total, avg, min, max)
        """
        results = {}

        for operation, times in self.timings.items():
            if not times:
                continue

            results[operation] = {
                'count': len(times),
                'total': sum(times),
                'avg': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
            }

        return results

    def reset(self) -> None:
        """Reset all timings."""
        self.timings.clear()
        self._current_operation = None
        self._start_time = None


class _TimerContext:
    """Context manager for PerformanceTimer."""

    def __init__(self, timer: PerformanceTimer, operation: str):
        self.timer = timer
        self.operation = operation

    def __enter__(self):
        self.timer.start(self.operation)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.timer.stop()
        return False


def format_bytes(size: int) -> str:
    """Format byte size as human-readable string.

    Args:
        size: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")

    Example:
        >>> format_bytes(1536)
        '1.5 KB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def get_text_stats(text: Any) -> Dict[str, Any]:
    """Get statistics about a Text object.

    Args:
        text: Text object to analyze

    Returns:
        Dictionary of statistics

    Example:
        >>> stats = get_text_stats(text)
        >>> print(f"Lines: {stats['lines']}")
    """
    text_str = str(text)

    return {
        'lines': len(text._text_lines) if hasattr(text, '_text_lines') else 0,
        'characters': len(text_str),
        'words': len(text_str.split()),
        'cursor_line': text.line_ptr if hasattr(text, 'line_ptr') else 0,
        'cursor_column': text.column_ptr if hasattr(text, 'column_ptr') else 0,
        'edit_mode': text.edit_mode if hasattr(text, 'edit_mode') else False,
    }

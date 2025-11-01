"""
Shared helper functions for textbox examples.
"""
import os
from typing import Optional

from textbox.utils.color_code import ColorCode

# Standard color palette for all examples
COLORS = {
    "user": ColorCode.WHITE,
    "ai": ColorCode.LIGHT_BLUE,  # Cyan-ish
    "system": ColorCode.GREEN,
    "error": ColorCode.DARK_RED,
    "highlight": ColorCode.YELLOW,
    "metadata": ColorCode.GREY,
}


def get_claude_client():
    """
    Get Anthropic client if API key is available.
    Returns None if anthropic package is not installed or no API key.
    """
    try:
        import anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        return anthropic.Anthropic(api_key=api_key)
    except ImportError:
        return None


def has_api_key() -> bool:
    """Check if ANTHROPIC_API_KEY is set."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def format_message(speaker: str, text: str, color: ColorCode) -> str:
    """Format a message with speaker prefix."""
    if speaker:
        return f"{speaker}: {text}"
    return text

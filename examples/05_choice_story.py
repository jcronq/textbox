#!/usr/bin/env python3
"""
Multi-Choice Story Game

A branching narrative where you make numbered choices to progress the story.
Use :back to explore different story branches.

Requires: ANTHROPIC_API_KEY environment variable (falls back to mock mode if not set)
"""
import asyncio
import re
from textbox import App, Text, TextLine, TextSegment
from textbox.utils.color_code import ColorCode
from shared_helpers import COLORS, get_claude_client, has_api_key

# System prompt for story generation
STORY_SYSTEM_PROMPT = """You are a creative storyteller for an interactive fiction game.

Rules:
1. Write engaging, atmospheric story scenes (2-3 sentences)
2. ALWAYS end with exactly 3 numbered choices
3. Format choices as: [1] 🎯 Description
4. Use relevant emoji for each choice type
5. Keep choices clear and meaningful
6. Remember previous choices to maintain story continuity

Example format:
[Story scene description]

What do you do?

[1] 🗡️ Fight the monster
[2] 💬 Try to negotiate
[3] 🏃 Run away

Start with: A lone traveler approaches a mysterious crossroads at dusk."""

# Mock story tree for demo mode
MOCK_STORY = {
    (): {  # Start
        "scene": "You stand at a mysterious crossroads as the sun sets. Three paths stretch before you, each leading into shadow. A weathered signpost offers cryptic directions.",
        "choices": [
            "🏔️ Take the mountain path (steep and dangerous)",
            "🌲 Enter the dark forest (unknown mysteries)",
            "🏰 Follow the road to the distant castle (safety, perhaps)",
        ],
    },
    (1,): {  # Mountain path
        "scene": "The mountain path is treacherous. As you climb, you hear a deep rumbling. A massive stone giant blocks your way, demanding you answer a riddle or turn back.",
        "choices": ["🧠 Answer the riddle", "⚔️ Challenge the giant to combat", "↩️ Turn back to the crossroads"],
    },
    (2,): {  # Forest path
        "scene": "The forest grows darker with each step. Glowing eyes watch from the shadows. You discover a fairy circle of mushrooms, pulsing with ethereal light.",
        "choices": ["💫 Step into the fairy circle", "🎵 Call out to the watchers", "🏃 Run deeper into the forest"],
    },
    (3,): {  # Castle path
        "scene": "You arrive at the castle gates. They're sealed shut, but you hear music and laughter from within. A small side door stands ajar, and you notice guards patrolling the walls.",
        "choices": ["🚪 Enter through the side door", "📣 Call up to the guards", "🔍 Search for another entrance"],
    },
    (1, 1): {  # Mountain + riddle
        "scene": "You solve the giant's riddle! He laughs heartily and steps aside, revealing a hidden cave filled with ancient treasure. You've found the legendary Dragon's Hoard!",
        "choices": ["🎉 Celebrate your victory!", "🔄 Play again", "👋 Exit game"],
    },
    (2, 1): {  # Forest + fairy circle
        "scene": "You step into the circle and the world transforms! The fairies crown you as their honored guest. They offer you a wish - anything your heart desires!",
        "choices": ["🎉 Make your wish!", "🔄 Play again", "👋 Exit game"],
    },
    (3, 1): {  # Castle + side door
        "scene": "Through the side door, you discover a grand feast! The lord welcomes you warmly - they've been expecting you. You're the legendary hero they've been waiting for!",
        "choices": ["🎉 Accept your destiny!", "🔄 Play again", "👋 Exit game"],
    },
}


class StoryState:
    """Track story state."""

    def __init__(self):
        self.choice_history = []  # Stack of choice numbers

    def add_choice(self, choice: int):
        """Add a choice to history."""
        self.choice_history.append(choice)

    def undo_last(self):
        """Remove last choice from history."""
        if self.choice_history:
            self.choice_history.pop()

    def get_history_tuple(self):
        """Get history as tuple for mock lookup."""
        return tuple(self.choice_history)


def create_colored_text(text: str, color: ColorCode) -> Text:
    """Create colored Text object."""
    return Text([TextLine([TextSegment(text, color)])])


def get_mock_story_node(history_tuple):
    """Get mock story node for current history."""
    if history_tuple in MOCK_STORY:
        return MOCK_STORY[history_tuple]
    # If exact match not found, try to find a close match or return default ending
    return {
        "scene": "Your journey takes an unexpected turn. The path becomes unclear, and you decide to rest and reflect on your adventure.",
        "choices": ["🔄 Start a new story", "↩️ Go back", "👋 Exit game"],
    }


def format_story_with_choices(scene: str, choices: list) -> Text:
    """Format story scene and choices with colors."""
    lines = []

    # Add scene text
    lines.append(create_colored_text(f"\n{scene}\n", COLORS["user"]))
    lines.append(create_colored_text("\nWhat do you do?\n\n", COLORS["system"]))

    # Add numbered choices
    for i, choice in enumerate(choices, 1):
        lines.append(create_colored_text(f"  [{i}] {choice}\n", COLORS["highlight"]))

    lines.append(create_colored_text("\nEnter choice (1-3): ", COLORS["metadata"]))

    return Text.from_text_list(lines)


async def handle_choice(choice_num: int, state: StoryState, app: App, client):
    """Handle player choice and generate next scene."""
    if choice_num < 1 or choice_num > 3:
        app.print(create_colored_text("\nPlease enter 1, 2, or 3.\n", COLORS["error"]))
        return

    # Add choice to history
    state.add_choice(choice_num)

    if client:
        # Real AI mode
        try:
            # Build context from history
            messages = []

            # Start with initial scene request
            if len(state.choice_history) == 1:
                messages.append({"role": "user", "content": "Begin the story."})
            else:
                # Add previous scenes (simplified - in production would store full context)
                messages.append({"role": "user", "content": f"Continue the story. The player chose option {choice_num}."})

            app.print(create_colored_text("\n", COLORS["ai"]))
            response_text = ""

            with client.messages.stream(
                max_tokens=400, messages=messages, model="claude-3-5-sonnet-20241022", system=STORY_SYSTEM_PROMPT
            ) as stream:
                for text in stream.text_stream:
                    response_text += text
                    app.print(create_colored_text(text, COLORS["ai"]))

            app.print(create_colored_text("\n", COLORS["ai"]))

        except Exception as e:
            app.print(create_colored_text(f"[Error: {str(e)}]\n", COLORS["error"]))
    else:
        # Mock mode
        node = get_mock_story_node(state.get_history_tuple())
        story_display = format_story_with_choices(node["scene"], node["choices"])
        app.print(story_display)


def main():
    """Run the choice story game."""
    app = App()
    client = get_claude_client()
    state = StoryState()

    # Welcome message
    if client:
        mode_msg = "Real AI mode (using Claude API)"
    else:
        mode_msg = "Mock mode (no API key found - pre-written story tree)"

    welcome = create_colored_text(
        f"""=== 🎭 The Dragon's Choice 🎭 ===

An interactive story where every choice matters!

{mode_msg}

How to play:
  • Read the story
  • Enter 1, 2, or 3 to make your choice
  • Use :back to explore different paths

Vim Commands:
  :back        - Undo last choice and try another path
  :restart     - Start the story over
  :quit        - Exit

Let's begin your adventure!
""",
        COLORS["system"],
    )
    app.print(welcome)

    # Show initial scene
    if client:
        asyncio.run(handle_choice(1, state, app, client))
        state.choice_history.clear()  # Reset after showing initial scene
    else:
        initial_node = get_mock_story_node(())
        app.print(format_story_with_choices(initial_node["scene"], initial_node["choices"]))

    @app.on_submit
    def handle_input(user_input: str):
        """Handle player input."""
        user_input = user_input.strip()

        # Try to parse as number
        try:
            choice = int(user_input)
            asyncio.run(handle_choice(choice, state, app, client))
        except ValueError:
            app.print(create_colored_text("\nPlease enter a number (1, 2, or 3).\n", COLORS["error"]))

    @app.command("back", help="Undo last choice")
    def undo_choice(cmd):
        """Undo the last choice."""
        if state.choice_history:
            state.undo_last()
            app.print(create_colored_text("\n[Undid last choice]\n", COLORS["metadata"]))

            # Redisplay previous state
            if not client:
                node = get_mock_story_node(state.get_history_tuple())
                app.print(format_story_with_choices(node["scene"], node["choices"]))
            else:
                app.print(create_colored_text("\n[Enter a choice to continue from previous point]\n", COLORS["system"]))
        else:
            app.print(create_colored_text("\nYou're at the beginning of the story.\n", COLORS["error"]))

    @app.command("restart", help="Restart the story")
    def restart_story(cmd):
        """Restart the story."""
        state.choice_history.clear()
        app.print(create_colored_text("\n=== Story Restarted ===\n", COLORS["system"]))

        # Show initial scene
        if not client:
            initial_node = get_mock_story_node(())
            app.print(format_story_with_choices(initial_node["scene"], initial_node["choices"]))

    @app.command("quit", "q", help="Exit the game")
    def quit_game(cmd):
        """Exit the game."""
        app.print(create_colored_text("\nThanks for playing!\n", COLORS["system"]))
        app.stop()

    app.start()


if __name__ == "__main__":
    main()

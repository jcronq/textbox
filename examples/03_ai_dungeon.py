#!/usr/bin/env python3
"""
Interactive AI Dungeon Master

An AI-generated text adventure with vim-style :back command to explore different paths.

Requires: ANTHROPIC_API_KEY environment variable (falls back to mock mode if not set)
"""
import asyncio
from textbox import App, Text, TextLine, TextSegment
from textbox.utils.color_code import ColorCode
from shared_helpers import COLORS, get_claude_client, has_api_key

# System prompt for dungeon master
DUNGEON_SYSTEM_PROMPT = """You are a dungeon master for a fantasy text adventure game.

Rules:
1. Generate rich, atmospheric descriptions in 2-3 sentences
2. Always list items in the room (if any) in UPPERCASE
3. Always list exits as directions (NORTH, SOUTH, EAST, WEST)
4. Respond naturally to player actions
5. Keep responses concise but engaging
6. Track a simple inventory when items are taken/dropped

Format your response like this:
[Description of the scene]

Items: [List items in UPPERCASE, or say NONE]
Exits: [List exits in UPPERCASE]

[Response to player action if any]

Start in an ancient castle entrance hall."""

# Mock dungeon for demo mode
MOCK_DUNGEON = {
    "start": {
        "description": "You stand in the entrance hall of an ancient castle. Dust motes dance in shafts of light from high windows. The air smells of age and mystery.",
        "items": ["TORCH"],
        "exits": ["NORTH", "EAST"],
        "actions": {
            "take torch": "You pick up the torch. It flickers to life in your hand, casting dancing shadows on the walls.",
            "go north": "hall",
            "go east": "library",
        },
    },
    "hall": {
        "description": "A long corridor stretches before you, lined with faded tapestries. The stone floor is worn smooth by countless footsteps over the centuries.",
        "items": ["SILVER KEY"],
        "exits": ["SOUTH", "WEST"],
        "actions": {"take key": "You take the silver key. It's cold to the touch and covered in ancient runes.", "go south": "start", "go west": "treasure"},
    },
    "library": {
        "description": "Towering bookshelves filled with ancient tomes surround you. A large reading desk sits in the center, covered in dust.",
        "items": ["ANCIENT BOOK"],
        "exits": ["WEST"],
        "actions": {
            "take book": "You carefully take the ancient book. The leather cover is embossed with strange symbols.",
            "go west": "start",
        },
    },
    "treasure": {
        "description": "You've found the treasure room! Gold coins and jewels sparkle in the torchlight. You've won!",
        "items": ["GOLDEN CROWN"],
        "exits": ["EAST"],
        "actions": {},
    },
}


class GameState:
    """Track game state."""

    def __init__(self):
        self.history = []  # List of (action, response) tuples
        self.inventory = []
        self.current_location = "start"  # For mock mode

    def add_action(self, action: str, response: str):
        """Add an action and response to history."""
        self.history.append((action, response))

    def undo_last(self):
        """Remove last action from history."""
        if self.history:
            self.history.pop()


def create_colored_text(text: str, color: ColorCode) -> Text:
    """Create colored Text object."""
    return Text([TextLine([TextSegment(text, color)])])


def parse_mock_response(location: str, action: str, state: GameState) -> str:
    """Generate mock response for demo mode."""
    room = MOCK_DUNGEON.get(location, MOCK_DUNGEON["start"])

    action_lower = action.lower().strip()

    # Check for specific actions
    if action_lower in room["actions"]:
        result = room["actions"][action_lower]

        # Handle movement
        if action_lower.startswith("go "):
            new_location = room["actions"][action_lower]
            state.current_location = new_location
            new_room = MOCK_DUNGEON[new_location]
            return f"{result}\n\n{new_room['description']}\n\nItems: {', '.join(new_room['items']) if new_room['items'] else 'NONE'}\nExits: {', '.join(new_room['exits'])}"

        # Handle taking items
        if action_lower.startswith("take "):
            item = action_lower.replace("take ", "").upper()
            if item in [i.split()[0] for i in room["items"]]:
                state.inventory.append(item)
            return result

        return result

    # Default response
    response = f"{room['description']}\n\nItems: {', '.join(room['items']) if room['items'] else 'NONE'}\nExits: {', '.join(room['exits'])}"

    if action_lower and action_lower != "look":
        response = f"You {action}, but nothing happens.\n\n" + response

    return response


def format_dungeon_response(response: str) -> Text:
    """Format dungeon response with colors."""
    lines = []
    for line in response.split("\n"):
        line_stripped = line.strip()

        # Color items line
        if line_stripped.startswith("Items:"):
            parts = line_stripped.split(":", 1)
            lines.append(
                create_colored_text(
                    parts[0] + ": ",
                    COLORS["system"],
                )
            )
            if len(parts) > 1:
                lines.append(create_colored_text(parts[1], COLORS["highlight"]))
            lines.append(create_colored_text("\n", COLORS["user"]))

        # Color exits line
        elif line_stripped.startswith("Exits:"):
            parts = line_stripped.split(":", 1)
            lines.append(create_colored_text(parts[0] + ": ", COLORS["system"]))
            if len(parts) > 1:
                lines.append(create_colored_text(parts[1], COLORS["system"]))
            lines.append(create_colored_text("\n", COLORS["user"]))

        # Normal description
        else:
            lines.append(create_colored_text(line + "\n", COLORS["ai"] if line_stripped else COLORS["user"]))

    return Text.from_text_list(lines)


async def handle_action(action: str, state: GameState, app: App, client):
    """Handle player action."""
    if not action.strip():
        return

    # Display player action
    app.print(create_colored_text(f"\n> {action}\n", COLORS["user"]))

    if client:
        # Real AI mode
        try:
            # Build context from history
            messages = []
            for hist_action, hist_response in state.history:
                messages.append({"role": "user", "content": hist_action})
                messages.append({"role": "assistant", "content": hist_response})

            # Add current action
            messages.append({"role": "user", "content": action})

            # Get AI response
            app.print(create_colored_text("", COLORS["ai"]))
            response_text = ""

            with client.messages.stream(
                max_tokens=400, messages=messages, model="claude-3-5-sonnet-20241022", system=DUNGEON_SYSTEM_PROMPT
            ) as stream:
                for text in stream.text_stream:
                    response_text += text
                    app.print(create_colored_text(text, COLORS["ai"]))

            app.print(create_colored_text("\n", COLORS["ai"]))

            # Save to history
            state.add_action(action, response_text)

        except Exception as e:
            app.print(create_colored_text(f"[Error: {str(e)}]\n", COLORS["error"]))
    else:
        # Mock mode
        response = parse_mock_response(state.current_location, action, state)
        formatted_response = format_dungeon_response(response)
        app.print(formatted_response)

        # Save to history
        state.add_action(action, response)


def main():
    """Run the AI dungeon game."""
    app = App()
    client = get_claude_client()
    state = GameState()

    # Welcome message
    if client:
        mode_msg = "Real AI mode (using Claude API)"
    else:
        mode_msg = "Mock mode (no API key found - exploring pre-made dungeon)"

    welcome_text = f"""=== 🏰 AI Dungeon Master 🏰 ===

An AI-generated fantasy adventure!

{mode_msg}

Commands:
  <action>     - Perform any action (e.g., "take torch", "go north")
  look         - Look around
  inventory    - Check inventory

Vim Commands:
  :back        - Undo last action and regenerate
  :restart     - Start over
  :quit        - Exit

Type "look" to begin your adventure!
"""

    first_run = [True]

    @app.on_submit
    def handle_input(user_input: str):
        """Handle player input."""
        if first_run[0]:
            first_run[0] = False
            app.print(create_colored_text(welcome_text, COLORS["system"]))

        if user_input.strip().lower() == "inventory":
            if state.inventory:
                inv_text = "Inventory: " + ", ".join(state.inventory)
            else:
                inv_text = "Inventory: Empty"
            app.print(create_colored_text(f"\n{inv_text}\n", COLORS["highlight"]))
        elif user_input.strip():
            asyncio.run(handle_action(user_input, state, app, client))

    @app.command("back", help="Undo last action")
    def undo_action(cmd):
        """Undo the last action."""
        if state.history:
            state.undo_last()
            app.print(create_colored_text("\n[Undid last action]\n", COLORS["metadata"]))

            # Redisplay last state
            if state.history:
                last_action, last_response = state.history[-1]
                if client:
                    app.print(create_colored_text(f"\n> {last_action}\n", COLORS["user"]))
                    app.print(create_colored_text(last_response + "\n", COLORS["ai"]))
                else:
                    formatted = format_dungeon_response(last_response)
                    app.print(formatted)
            else:
                app.print(create_colored_text("At the beginning of your adventure.\n", COLORS["system"]))
        else:
            app.print(create_colored_text("\nNothing to undo.\n", COLORS["error"]))

    @app.command("restart", help="Restart the game")
    def restart_game(cmd):
        """Restart the game."""
        state.history.clear()
        state.inventory.clear()
        state.current_location = "start"
        first_run[0] = True  # Reset first run flag
        app.print(create_colored_text("\n=== Game Restarted ===\n", COLORS["system"]))
        app.print(create_colored_text(welcome_text, COLORS["system"]))

    @app.command("quit", "q", help="Exit the game")
    def quit_game(cmd):
        """Exit the game."""
        app.print(create_colored_text("\nThanks for playing!\n", COLORS["system"]))
        app.stop()

    app.start()


if __name__ == "__main__":
    main()

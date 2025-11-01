#!/usr/bin/env python3
"""
Classic Interactive Fiction Engine - Cave Adventure

A simple text adventure game showcasing textbox's colored text and vim-style interface.
No AI required - pure game logic.

Commands: look, take <item>, drop <item>, go <direction>, inventory, help
Vim commands: :restart, :quit
"""
import sys
from textbox import App, Text, TextLine, TextSegment
from textbox.utils.color_code import ColorCode
from shared_helpers import COLORS

# Game world definition
ROOMS = {
    "cave_entrance": {
        "name": "Cave Entrance",
        "description": "You stand at the entrance to a dark cave. Sunlight filters in from behind you.",
        "items": ["torch"],
        "exits": {"north": "dark_tunnel", "east": "forest_path"},
    },
    "dark_tunnel": {
        "name": "Dark Tunnel",
        "description": "A narrow tunnel stretches before you. You can barely see without a light source.",
        "items": ["rusty_sword"],
        "exits": {"south": "cave_entrance", "north": "treasure_room"},
        "dark": True,
    },
    "treasure_room": {
        "name": "Treasure Room",
        "description": "A grand chamber filled with glittering treasure! You've found the dragon's hoard!",
        "items": ["golden_crown"],
        "exits": {"south": "dark_tunnel"},
        "locked": True,
        "requires": "silver_key",
    },
    "forest_path": {
        "name": "Forest Path",
        "description": "A winding path through dense forest. Birds chirp in the trees above.",
        "items": ["silver_key"],
        "exits": {"west": "cave_entrance"},
    },
}

ITEM_DESCRIPTIONS = {
    "torch": "A wooden torch that provides light",
    "rusty_sword": "An old rusty sword, still usable",
    "silver_key": "A silver key with ancient runes",
    "golden_crown": "A magnificent golden crown encrusted with gems",
}


class GameState:
    """Track game state."""

    def __init__(self):
        self.current_room = "cave_entrance"
        self.inventory = []
        self.moves = 0

    def reset(self):
        """Reset game to initial state."""
        self.current_room = "cave_entrance"
        self.inventory = []
        self.moves = 0


def create_colored_text(segments):
    """Create Text object from list of (text, color) tuples."""
    text_segments = [TextSegment(text, color) for text, color in segments]
    return Text([TextLine(text_segments)])


def look_room(state: GameState) -> Text:
    """Generate room description."""
    room = ROOMS[state.current_room]
    lines = []

    # Room name
    lines.append(create_colored_text([("=== ", COLORS["system"]), (room["name"], COLORS["ai"]), (" ===", COLORS["system"])]))

    # Check if room is dark
    if room.get("dark") and "torch" not in state.inventory:
        lines.append(create_colored_text([("It's too dark to see anything!", COLORS["error"])]))
        return Text.from_text_list(lines)

    # Description
    lines.append(create_colored_text([(room["description"], COLORS["user"])]))
    lines.append(create_colored_text([("", COLORS["user"])]))  # Blank line

    # Items
    if room["items"]:
        items_str = ", ".join([item.upper() for item in room["items"]])
        lines.append(create_colored_text([("Items: ", COLORS["system"]), (items_str, COLORS["highlight"])]))

    # Exits
    exits_str = ", ".join([exit.upper() for exit in room["exits"].keys()])
    lines.append(create_colored_text([("Exits: ", COLORS["system"]), (exits_str, COLORS["system"])]))

    return Text.from_text_list(lines)


def parse_command(command: str, state: GameState, app: App) -> Text:
    """Parse and execute player command."""
    command = command.strip().lower()
    parts = command.split(maxsplit=1)

    if not parts:
        return create_colored_text([("Please enter a command. Type 'help' for help.", COLORS["error"])])

    verb = parts[0]
    args = parts[1] if len(parts) > 1 else ""

    # Look command
    if verb in ["look", "l"]:
        return look_room(state)

    # Inventory command
    elif verb in ["inventory", "i"]:
        if not state.inventory:
            return create_colored_text([("You are not carrying anything.", COLORS["system"])])
        items_str = ", ".join([item.upper() for item in state.inventory])
        return create_colored_text([("You are carrying: ", COLORS["system"]), (items_str, COLORS["highlight"])])

    # Take command
    elif verb in ["take", "get", "pick"]:
        if not args:
            return create_colored_text([("Take what?", COLORS["error"])])
        item = args.lower().replace(" ", "_")
        room = ROOMS[state.current_room]

        if room.get("dark") and "torch" not in state.inventory:
            return create_colored_text([("It's too dark to see anything!", COLORS["error"])])

        if item in room["items"]:
            room["items"].remove(item)
            state.inventory.append(item)
            desc = ITEM_DESCRIPTIONS.get(item, "an item")
            return create_colored_text([(f"You take the {item.replace('_', ' ')}: {desc}", COLORS["system"])])
        else:
            return create_colored_text([(f"There is no {args} here.", COLORS["error"])])

    # Drop command
    elif verb in ["drop", "put"]:
        if not args:
            return create_colored_text([("Drop what?", COLORS["error"])])
        item = args.lower().replace(" ", "_")

        if item in state.inventory:
            state.inventory.remove(item)
            ROOMS[state.current_room]["items"].append(item)
            return create_colored_text([(f"You drop the {item.replace('_', ' ')}.", COLORS["system"])])
        else:
            return create_colored_text([(f"You don't have {args}.", COLORS["error"])])

    # Go command
    elif verb in ["go", "move", "walk", "n", "s", "e", "w", "north", "south", "east", "west"]:
        # Handle shorthand directions
        direction_map = {"n": "north", "s": "south", "e": "east", "w": "west"}
        if verb in ["n", "s", "e", "w"]:
            direction = direction_map[verb]
        elif verb in ["north", "south", "east", "west"]:
            direction = verb
        else:
            direction = args.lower()

        room = ROOMS[state.current_room]

        if direction not in room["exits"]:
            return create_colored_text([(f"You can't go {direction} from here.", COLORS["error"])])

        next_room_id = room["exits"][direction]
        next_room = ROOMS[next_room_id]

        # Check if room is locked
        if next_room.get("locked"):
            required_key = next_room.get("requires")
            if required_key not in state.inventory:
                return create_colored_text([(f"The door is locked. You need a {required_key.replace('_', ' ')}.", COLORS["error"])])
            else:
                # Unlock the room
                next_room["locked"] = False
                result = create_colored_text(
                    [
                        (f"You unlock the door with the {required_key.replace('_', ' ')}!", COLORS["highlight"]),
                        ("\n", COLORS["user"]),
                    ]
                )
                state.current_room = next_room_id
                state.moves += 1
                # Show new room
                new_room_desc = look_room(state)
                return Text.from_text_list([result, new_room_desc])

        state.current_room = next_room_id
        state.moves += 1

        # Check for win condition
        if next_room_id == "treasure_room":
            result = create_colored_text(
                [
                    ("\n🎉 CONGRATULATIONS! 🎉\n", COLORS["highlight"]),
                    (f"You found the treasure in {state.moves} moves!\n", COLORS["system"]),
                    ("Type :restart to play again or :quit to exit.\n", COLORS["metadata"]),
                ]
            )
            return Text.from_text_list([result, look_room(state)])

        return look_room(state)

    # Help command
    elif verb == "help":
        help_text = """
Available Commands:
  look (l)           - Look around the room
  inventory (i)      - Check your inventory
  take <item>        - Pick up an item
  drop <item>        - Drop an item
  go <direction>     - Move in a direction (or use n, s, e, w)
  help               - Show this help

Vim Commands:
  :restart           - Restart the game
  :quit              - Exit the game

Goal: Find the treasure room!
"""
        return create_colored_text([(help_text, COLORS["system"])])

    else:
        return create_colored_text([(f"I don't understand '{command}'. Type 'help' for help.", COLORS["error"])])


def main():
    """Run the text adventure game."""
    app = App()
    state = GameState()

    # Welcome message
    welcome_segments = [
        ("=== CAVE ADVENTURE ===\n", COLORS["highlight"]),
        ("A classic text adventure game\n\n", COLORS["system"]),
        ("Type 'help' for commands, or start exploring!\n", COLORS["metadata"]),
        ("Your goal: Find the treasure room!\n\n", COLORS["metadata"]),
    ]

    first_run = [True]

    @app.on_submit
    def handle_input(command: Text):
        """Handle player commands."""
        if first_run[0]:
            first_run[0] = False
            app.print(create_colored_text(welcome_segments))
            app.print(look_room(state))

        command_str = command.text.strip()
        if command_str:
            result = parse_command(command_str, state, app)
            app.print(result)

    @app.command("restart", help="Restart the game")
    def restart_game(cmd):
        """Restart the game."""
        state.reset()
        # Reset room states
        ROOMS["treasure_room"]["locked"] = True
        for room_id, room in ROOMS.items():
            room["items"] = []
        # Restore initial items
        ROOMS["cave_entrance"]["items"] = ["torch"]
        ROOMS["dark_tunnel"]["items"] = ["rusty_sword"]
        ROOMS["treasure_room"]["items"] = ["golden_crown"]
        ROOMS["forest_path"]["items"] = ["silver_key"]

        first_run[0] = True  # Reset first run flag
        app.print(create_colored_text(welcome_segments))
        app.print(look_room(state))

    @app.command("quit", "q", help="Exit the game")
    def quit_game(cmd):
        """Exit the game."""
        app.print(create_colored_text([("Thanks for playing!\n", COLORS["system"])]))
        app.stop()

    app.start()


if __name__ == "__main__":
    main()

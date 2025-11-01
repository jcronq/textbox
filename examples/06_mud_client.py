#!/usr/bin/env python3
"""
MUD-Style Game Client

A single-player MUD (Multi-User Dungeon) with AI-powered NPCs and ambient events.
Demonstrates async real-time updates.

Requires: ANTHROPIC_API_KEY environment variable (falls back to mock mode if not set)
"""
import asyncio
import random
from textbox import App, Text, TextLine, TextSegment
from textbox.utils.color_code import ColorCode
from shared_helpers import COLORS, get_claude_client, has_api_key

# NPC definitions
NPCS = {
    "merchant": {
        "name": "Grim the Merchant",
        "description": "A stout merchant with a bushy beard and twinkling eyes",
        "personality": "You are Grim, a friendly merchant who sells wares and shares gossip. You're jovial and helpful.",
        "ambient_messages": [
            "Grim arranges items on his counter.",
            "Grim hums a cheerful tune.",
            "Grim counts coins, muttering to himself.",
        ],
    },
    "guard": {
        "name": "Captain Aria",
        "description": "A stern guard captain in polished armor",
        "personality": "You are Captain Aria, a serious guard captain. You're protective of the town and suspicious of strangers.",
        "ambient_messages": [
            "Captain Aria scans the square carefully.",
            "Captain Aria adjusts her sword belt.",
            "Captain Aria walks the perimeter, vigilant.",
        ],
    },
    "wizard": {
        "name": "Eldrin the Wise",
        "description": "An elderly wizard with flowing robes and a gnarled staff",
        "personality": "You are Eldrin, an ancient wizard who speaks in riddles and offers cryptic wisdom.",
        "ambient_messages": [
            "Eldrin's staff glows faintly.",
            "Eldrin mumbles arcane words.",
            "Eldrin gazes at the stars thoughtfully.",
        ],
    },
}

# Game world
LOCATION = {
    "name": "Town Square",
    "description": "A bustling town square with a fountain in the center. Market stalls line the edges, and a guard tower looms to the north.",
    "npcs": ["merchant", "guard", "wizard"],
}


def create_colored_text(text: str, color: ColorCode) -> Text:
    """Create colored Text object."""
    return Text([TextLine([TextSegment(text, color)])])


class MUDClient:
    """MUD client state."""

    def __init__(self, app: App, client):
        self.app = app
        self.client = client
        self.running = False
        self.npc_task = None

    async def ambient_npc_events(self):
        """Generate ambient NPC messages."""
        while self.running:
            # Wait random time between events (10-30 seconds)
            await asyncio.sleep(random.uniform(10, 30))

            if not self.running:
                break

            # Pick random NPC
            npc_id = random.choice(list(NPCS.keys()))
            npc = NPCS[npc_id]

            # Pick random ambient message
            message = random.choice(npc["ambient_messages"])

            # Display ambient event
            self.app.print(create_colored_text(f"\n[NPC] {message}\n", COLORS["system"]))

    def start_ambient_events(self):
        """Start ambient event generation."""
        self.running = True
        # Note: Can't use asyncio.create_task directly in textbox
        # We'll simulate with scheduled calls instead

    def stop_ambient_events(self):
        """Stop ambient event generation."""
        self.running = False

    async def talk_to_npc(self, npc_id: str, message: str):
        """Talk to an NPC."""
        if npc_id not in NPCS:
            self.app.print(create_colored_text(f"\nThere is no NPC named '{npc_id}' here.\n", COLORS["error"]))
            return

        npc = NPCS[npc_id]
        self.app.print(create_colored_text(f"\nYou say to {npc['name']}: \"{message}\"\n", COLORS["user"]))

        if self.client:
            # Real AI response
            try:
                self.app.print(create_colored_text(f"{npc['name']}: ", COLORS["ai"]))

                prompt = f"You are in a town square. A player says to you: \"{message}\". Respond in character (1-2 sentences)."

                with self.client.messages.stream(
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}],
                    model="claude-3-5-sonnet-20241022",
                    system=npc["personality"],
                ) as stream:
                    for text in stream.text_stream:
                        self.app.print(create_colored_text(text, COLORS["ai"]))

                self.app.print(create_colored_text("\n", COLORS["ai"]))

            except Exception as e:
                self.app.print(create_colored_text(f"[Error: {str(e)}]\n", COLORS["error"]))
        else:
            # Mock responses
            mock_responses = {
                "merchant": "Ah, hello friend! Looking for fine wares? I have the best prices in town!",
                "guard": "State your business. We don't tolerate troublemakers here.",
                "wizard": "The stars whisper secrets to those who listen... What brings you to seek old Eldrin?",
            }
            response = mock_responses.get(npc_id, "...")
            self.app.print(create_colored_text(f"{npc['name']}: {response}\n", COLORS["ai"]))


def parse_command(command: str, mud: MUDClient):
    """Parse and execute player command."""
    command = command.strip()
    parts = command.split(maxsplit=1)

    if not parts:
        return

    verb = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    # Look command
    if verb in ["look", "l"]:
        location = LOCATION
        output = f"\n=== {location['name']} ===\n{location['description']}\n\nNPCs present:\n"
        for npc_id in location["npcs"]:
            npc = NPCS[npc_id]
            output += f"  • {npc['name']} - {npc['description']}\n"
        mud.app.print(create_colored_text(output, COLORS["system"]))

    # Say to NPC
    elif verb in ["say", "talk", "speak"]:
        # Format: say <npc> <message>
        if not args:
            mud.app.print(create_colored_text("\nSay what to whom? Usage: say <npc> <message>\n", COLORS["error"]))
            return

        # Parse NPC name and message
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            mud.app.print(create_colored_text("\nUsage: say <npc> <message>\n", COLORS["error"]))
            return

        npc_name = parts[0].lower()
        message = parts[1]

        # Find NPC by partial name match
        npc_id = None
        for nid, npc in NPCS.items():
            if npc_name in nid.lower() or npc_name in npc["name"].lower():
                npc_id = nid
                break

        if npc_id:
            asyncio.run(mud.talk_to_npc(npc_id, message))
        else:
            mud.app.print(create_colored_text(f"\nCouldn't find NPC '{npc_name}'.\n", COLORS["error"]))

    # Who command - list NPCs
    elif verb == "who":
        output = "\n=== NPCs in Town Square ===\n"
        for npc_id, npc in NPCS.items():
            output += f"  • {npc['name']} ({npc_id})\n"
        mud.app.print(create_colored_text(output, COLORS["highlight"]))

    # Help command
    elif verb == "help":
        help_text = """
=== MUD Client Commands ===

  look (l)           - Look around the area
  say <npc> <msg>    - Talk to an NPC
  who                - List NPCs in the area
  help               - Show this help

Examples:
  say merchant hello
  say guard what's happening?
  say wizard teach me magic

Vim Commands:
  :quit              - Exit the game
"""
        mud.app.print(create_colored_text(help_text, COLORS["system"]))

    else:
        mud.app.print(create_colored_text(f"\nUnknown command: {verb}. Type 'help' for help.\n", COLORS["error"]))


def main():
    """Run the MUD client."""
    app = App()
    client = get_claude_client()
    mud = MUDClient(app, client)

    # Welcome message
    if client:
        mode_msg = "Real AI mode (NPCs powered by Claude API)"
    else:
        mode_msg = "Mock mode (no API key found - NPCs use canned responses)"

    welcome = create_colored_text(
        f"""=== 🏰 MUD Client - Town Square 🏰 ===

A single-player MUD with AI-powered NPCs!

{mode_msg}

Commands:
  look               - Look around
  say <npc> <msg>    - Talk to an NPC
  who                - List NPCs
  help               - Show commands

Try:
  look
  who
  say merchant hello

Note: NPCs will occasionally do things on their own!

:quit to exit
""",
        COLORS["system"],
    )
    app.print(welcome)

    # Show initial location
    parse_command("look", mud)

    # Start ambient events
    mud.start_ambient_events()

    @app.on_submit
    def handle_input(user_input: str):
        """Handle player input."""
        if user_input.strip():
            parse_command(user_input, mud)

    @app.command("quit", "q", help="Exit the game")
    def quit_game(cmd):
        """Exit the game."""
        mud.stop_ambient_events()
        app.print(create_colored_text("\nFarewell, adventurer!\n", COLORS["system"]))
        app.stop()

    # Try to start async ambient events (if supported)
    # Note: This is a simplified version - true async would need proper event loop integration
    import threading

    def ambient_loop():
        """Run ambient events in background."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(mud.ambient_npc_events())

    # Start ambient thread
    ambient_thread = threading.Thread(target=ambient_loop, daemon=True)
    ambient_thread.start()

    try:
        app.start()
    finally:
        mud.stop_ambient_events()


if __name__ == "__main__":
    main()

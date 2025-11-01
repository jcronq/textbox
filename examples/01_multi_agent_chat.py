#!/usr/bin/env python3
"""
Multi-Agent Conversation Viewer

Shows multiple AI agents responding to user queries in sequence.
Demonstrates streaming responses and colored output.

Requires: ANTHROPIC_API_KEY environment variable (falls back to mock mode if not set)
"""
import asyncio
from textbox import App, Text, TextLine, TextSegment
from textbox.utils.color_code import ColorCode
from shared_helpers import COLORS, get_claude_client, has_api_key, create_text_from_string

# Agent configurations
AGENTS = {
    "agent_1": {
        "name": "Agent_1",
        "color": ColorCode.LIGHT_BLUE,
        "system_prompt": "You are a helpful AI assistant. Provide concise, factual answers. Keep responses to 2-3 sentences.",
    },
    "agent_2": {
        "name": "Agent_2",
        "color": ColorCode.GREEN,
        "system_prompt": "You are a critical thinking AI. After seeing another agent's response, provide additional perspective, alternative viewpoints, or point out potential considerations. Keep responses to 2-3 sentences.",
    },
}

# Mock responses for demo mode
MOCK_RESPONSES = {
    "what is python": {
        "agent_1": "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in web development, data science, automation, and AI applications.",
        "agent_2": "While Python is indeed versatile, it's worth noting that its interpreted nature can make it slower than compiled languages for performance-critical applications. However, libraries like NumPy and frameworks like TensorFlow mitigate this for many use cases.",
    },
    "default": {
        "agent_1": "I understand your question. Let me provide a thoughtful response based on the information available.",
        "agent_2": "That's a good starting point. It's also worth considering multiple perspectives on this topic and examining potential edge cases.",
    },
}


def create_colored_text(text: str, color: ColorCode) -> Text:
    """Create colored Text object."""
    return Text([TextLine([TextSegment(text, color)])])


def get_mock_response(query: str, agent_id: str) -> str:
    """Get mock response for demo mode."""
    query_lower = query.lower().strip()
    for key in MOCK_RESPONSES:
        if key in query_lower:
            return MOCK_RESPONSES[key][agent_id]
    return MOCK_RESPONSES["default"][agent_id]


async def stream_agent_response(client, agent_id: str, user_query: str, app: App):
    """Stream response from an agent."""
    agent = AGENTS[agent_id]

    if client is None:
        # Mock mode - simulate streaming
        response_text = get_mock_response(user_query, agent_id)
        app.print(create_colored_text(f"\n{agent['name']}: ", agent["color"]))

        # Simulate streaming with delays
        words = response_text.split()
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)  # Simulate network delay
            if i == 0:
                app.print(create_colored_text(word, agent["color"]))
            else:
                app.print(create_colored_text(f" {word}", agent["color"]))
        app.print(create_colored_text("\n", agent["color"]))
    else:
        # Real API call with streaming
        app.print(create_colored_text(f"\n{agent['name']}: ", agent["color"]))

        try:
            with client.messages.stream(
                max_tokens=300,
                messages=[{"role": "user", "content": user_query}],
                model="claude-3-5-sonnet-20241022",
                system=agent["system_prompt"],
            ) as stream:
                for text in stream.text_stream:
                    app.print(create_colored_text(text, agent["color"]))
            app.print(create_colored_text("\n", agent["color"]))
        except Exception as e:
            app.print(create_colored_text(f"\n[Error: {str(e)}]\n", COLORS["error"]))


async def handle_user_query(user_query: str, app: App, client):
    """Handle user query by getting responses from both agents."""
    if not user_query.strip():
        return

    # Display user query
    app.print(create_colored_text(f"\nUser: {user_query}\n", COLORS["user"]))

    # Get Agent 1 response
    await stream_agent_response(client, "agent_1", user_query, app)

    # Get Agent 2 response (providing context of Agent 1's response)
    agent_2_query = f"The user asked: '{user_query}'. Another agent responded with their perspective. Now provide your additional perspective or alternative viewpoint."
    await stream_agent_response(client, "agent_2", agent_2_query, app)


def main():
    """Run the multi-agent chat interface."""
    app = App()
    client = get_claude_client()

    # Display welcome message
    if client:
        mode_msg = "Real AI mode (using Claude API)"
    else:
        mode_msg = "Mock mode (no API key found - using canned responses)"

    welcome_text = f"""=== Multi-Agent Conversation ===

Two AI agents will respond to your questions in sequence.

{mode_msg}

Commands:
  :clear   - Clear conversation
  :agents  - List agents
  :quit    - Exit

Try asking: "What is Python?" or "Explain quantum computing"
"""

    first_run = [True]  # Use list to allow modification in closure

    @app.on_submit
    def handle_input(user_input: Text):
        """Handle user input."""
        # Print welcome on first run
        if first_run[0]:
            first_run[0] = False
            app.print(create_text_from_string(welcome_text, COLORS["system"]))

        # Convert Text to string
        input_str = user_input.text.strip()
        if input_str:
            # Schedule async handler
            asyncio.create_task(handle_user_query(input_str, app, client))

    @app.command("clear", help="Clear conversation")
    def clear_conversation(cmd):
        """Clear the conversation."""
        # Note: textbox doesn't have a clear screen method, so we just add space
        app.print(create_colored_text("\n" * 5 + "=== Conversation Cleared ===\n", COLORS["system"]))

    @app.command("agents", help="List agents")
    def list_agents(cmd):
        """List available agents."""
        agent_info = "\n=== Available Agents ===\n"
        for agent_id, agent in AGENTS.items():
            agent_info += f"\n{agent['name']}: {agent['system_prompt'][:60]}...\n"
        app.print(create_colored_text(agent_info, COLORS["system"]))

    @app.command("quit", "q", help="Exit the application")
    def quit_app(cmd):
        """Exit the application."""
        app.print(create_colored_text("\nGoodbye!\n", COLORS["system"]))
        app.stop()

    app.start()


if __name__ == "__main__":
    main()

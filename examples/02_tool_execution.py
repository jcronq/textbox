#!/usr/bin/env python3
"""
AI Agent with Tool Execution Display

Shows an AI agent's thinking process and tool calls.
Demonstrates simulated tool calling with colored visualization.

Requires: ANTHROPIC_API_KEY environment variable (falls back to mock mode if not set)
"""
import asyncio
import json
from datetime import datetime
from textbox import App, Text, TextLine, TextSegment
from textbox.utils.color_code import ColorCode
from shared_helpers import COLORS, get_claude_client, has_api_key, create_text_from_string

# Mock tools
TOOLS = {
    "get_weather": {
        "description": "Get current weather for a location",
        "parameters": {"location": "string"},
        "mock_data": {"San Francisco": {"temp": 65, "condition": "Sunny ☀️"}, "New York": {"temp": 45, "condition": "Cloudy ☁️"}},
    },
    "get_time": {"description": "Get current time", "parameters": {}, "mock_data": None},
    "calculator": {
        "description": "Perform a mathematical calculation",
        "parameters": {"expression": "string"},
        "mock_data": None,
    },
}


def create_colored_text(text: str, color: ColorCode) -> Text:
    """Create colored Text object."""
    return Text([TextLine([TextSegment(text, color)])])


def execute_mock_tool(tool_name: str, params: dict) -> str:
    """Execute a mock tool and return result."""
    if tool_name == "get_weather":
        location = params.get("location", "San Francisco")
        data = TOOLS["get_weather"]["mock_data"].get(location, {"temp": 70, "condition": "Clear"})
        return json.dumps(data)
    elif tool_name == "get_time":
        return json.dumps({"time": datetime.now().strftime("%H:%M:%S"), "timezone": "UTC"})
    elif tool_name == "calculator":
        expression = params.get("expression", "0")
        try:
            # Safe eval for simple math
            result = eval(expression, {"__builtins__": {}}, {})
            return json.dumps({"result": result})
        except:
            return json.dumps({"error": "Invalid expression"})
    return json.dumps({"error": "Unknown tool"})


async def simulate_tool_workflow(query: str, app: App, client):
    """Simulate tool calling workflow with visual display."""
    # Display user query
    app.print(create_colored_text(f"\n> User: {query}\n", COLORS["user"]))

    # Detect if query needs tools (simple pattern matching)
    query_lower = query.lower()
    needs_weather = any(word in query_lower for word in ["weather", "temperature", "forecast"])
    needs_time = any(word in query_lower for word in ["time", "clock", "hour"])
    needs_calc = any(word in query_lower for word in ["calculate", "math", "compute", "+"," -", "*", "/"])

    if not (needs_weather or needs_time or needs_calc):
        # No tools needed, just respond
        if client:
            try:
                app.print(create_colored_text("[Agent] ", COLORS["metadata"]))
                with client.messages.stream(
                    max_tokens=200, messages=[{"role": "user", "content": query}], model="claude-3-5-sonnet-20241022"
                ) as stream:
                    for text in stream.text_stream:
                        app.print(create_colored_text(text, COLORS["ai"]))
                app.print(create_colored_text("\n", COLORS["ai"]))
                return
            except Exception as e:
                app.print(create_colored_text(f"[Error: {str(e)}]\n", COLORS["error"]))
                return
        else:
            # Mock response
            app.print(create_colored_text("[Agent] I can help with that. Let me think about your question.\n", COLORS["ai"]))
            return

    # Show thinking
    app.print(create_colored_text("[Agent] ", COLORS["metadata"]))
    thinking_msg = "Thinking: I need to use tools to answer this question...\n"
    for char in thinking_msg:
        await asyncio.sleep(0.02)
        app.print(create_colored_text(char, COLORS["metadata"]))

    # Determine which tool to use
    tool_name = None
    params = {}

    if needs_weather:
        tool_name = "get_weather"
        # Extract location if mentioned
        for city in ["san francisco", "new york", "sf", "nyc"]:
            if city in query_lower:
                if city == "sf":
                    params["location"] = "San Francisco"
                elif city == "nyc":
                    params["location"] = "New York"
                else:
                    params["location"] = city.title()
                break
        if "location" not in params:
            params["location"] = "San Francisco"

    elif needs_time:
        tool_name = "get_time"
        params = {}

    elif needs_calc:
        tool_name = "calculator"
        # Extract expression (simple approach)
        import re

        match = re.search(r"(\d+\s*[\+\-\*/]\s*\d+)", query)
        if match:
            params["expression"] = match.group(1)
        else:
            params["expression"] = "0"

    # Show tool call
    await asyncio.sleep(0.3)
    tool_call_msg = f"[Tool] Calling: {tool_name}({json.dumps(params)})\n"
    app.print(create_colored_text(tool_call_msg, COLORS["highlight"]))

    # Execute tool
    await asyncio.sleep(0.5)
    result = execute_mock_tool(tool_name, params)
    result_msg = f"[Tool] Result: {result}\n"
    app.print(create_colored_text(result_msg, COLORS["highlight"]))

    # Generate response
    await asyncio.sleep(0.3)
    app.print(create_colored_text("\n[Agent] ", COLORS["ai"]))

    if client:
        # Use real API to synthesize response
        try:
            synthesis_prompt = f"The user asked: '{query}'. A tool was called and returned: {result}. Provide a natural, concise response (1-2 sentences) incorporating this information."
            with client.messages.stream(
                max_tokens=200,
                messages=[{"role": "user", "content": synthesis_prompt}],
                model="claude-3-5-sonnet-20241022",
            ) as stream:
                for text in stream.text_stream:
                    app.print(create_colored_text(text, COLORS["ai"]))
            app.print(create_colored_text("\n", COLORS["ai"]))
        except Exception as e:
            app.print(create_colored_text(f"[Error: {str(e)}]\n", COLORS["error"]))
    else:
        # Mock synthesized response
        result_data = json.loads(result)
        if tool_name == "get_weather":
            response = f"The current weather in {params['location']} is {result_data['temp']}°F and {result_data['condition']}.\n"
        elif tool_name == "get_time":
            response = f"The current time is {result_data['time']}.\n"
        elif tool_name == "calculator":
            response = f"The result of {params['expression']} is {result_data['result']}.\n"
        else:
            response = "Here's the information you requested.\n"

        for char in response:
            await asyncio.sleep(0.02)
            app.print(create_colored_text(char, COLORS["ai"]))


def main():
    """Run the tool execution demo."""
    app = App()
    client = get_claude_client()

    # Welcome message
    if client:
        mode_msg = "Real AI mode (using Claude API)"
    else:
        mode_msg = "Mock mode (no API key found)"

    welcome_text = f"""=== AI Agent with Tools ===

Watch the agent think and use tools to answer your questions.

{mode_msg}

Available Tools:
  • get_weather(location) - Get weather information
  • get_time() - Get current time
  • calculator(expression) - Perform calculations

Commands:
  :tools   - List available tools
  :clear   - Clear screen
  :quit    - Exit

Try asking:
  "What's the weather in San Francisco?"
  "What time is it?"
  "Calculate 15 + 27"
"""

    first_run = [True]

    @app.on_submit
    def handle_input(user_input: str):
        """Handle user input."""
        if first_run[0]:
            first_run[0] = False
            app.print(create_text_from_string(welcome_text, COLORS["system"]))

        if user_input.strip():
            asyncio.run(simulate_tool_workflow(user_input, app, client))

    @app.command("tools", help="List available tools")
    def list_tools(cmd):
        """List available tools."""
        tools_info = "\n=== Available Tools ===\n"
        for tool_name, tool_info in TOOLS.items():
            tools_info += f"\n{tool_name}: {tool_info['description']}\n"
        app.print(create_colored_text(tools_info, COLORS["system"]))

    @app.command("clear", help="Clear screen")
    def clear_screen(cmd):
        """Clear the screen."""
        app.print(create_colored_text("\n" * 5 + "=== Screen Cleared ===\n", COLORS["system"]))

    @app.command("quit", "q", help="Exit the application")
    def quit_app(cmd):
        """Exit the application."""
        app.print(create_colored_text("\nGoodbye!\n", COLORS["system"]))
        app.stop()

    app.start()


if __name__ == "__main__":
    main()

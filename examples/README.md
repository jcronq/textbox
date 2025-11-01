# Textbox Examples

Demo applications showcasing Textbox for AI agents and text adventures.

## Setup

### Installation

```bash
# Install textbox
pip install -e ..

# For AI-powered examples, install anthropic
pip install anthropic
```

### API Key (Optional)

For AI-powered examples, set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

**All examples work without an API key** - they fall back to mock mode with pre-scripted content.

## Examples

### 1. Multi-Agent Conversation (`01_multi_agent_chat.py`)

Two AI agents respond to your questions in sequence, each providing different perspectives.

**Features:**
- Streaming AI responses
- Color-coded agents
- Works in mock mode without API

**Run:**
```bash
python3 01_multi_agent_chat.py
```

**Try asking:**
- "What is Python?"
- "Explain quantum computing"

---

### 2. AI Agent with Tools (`02_tool_execution.py`)

Watch an AI agent think and call tools to answer questions.

**Features:**
- Simulated tool calling (weather, time, calculator)
- Color-coded thinking process
- Visual tool execution

**Run:**
```bash
python3 02_tool_execution.py
```

**Try:**
- "What's the weather in San Francisco?"
- "What time is it?"
- "Calculate 15 + 27"

---

### 3. AI Dungeon Master (`03_ai_dungeon.py`)

An AI-generated fantasy text adventure with vim-style `:back` command.

**Features:**
- AI generates story and responds to actions
- Free-form text input
- `:back` to undo and try different actions
- Persistent inventory

**Run:**
```bash
python3 03_ai_dungeon.py
```

**Try:**
- "look"
- "take torch"
- "go north"
- ":back" (undo last action)

---

### 4. Classic Text Adventure (`04_text_adventure.py`)

A traditional interactive fiction game - no AI required!

**Features:**
- Hardcoded game world (5 rooms)
- Puzzle to solve (find the treasure)
- Pure game logic, no API calls
- Command parser

**Run:**
```bash
python3 04_text_adventure.py
```

**Commands:**
- look, take, drop, go, inventory
- `:restart`, `:quit`

---

### 5. Choice-Driven Story (`05_choice_story.py`)

A branching narrative where you make numbered choices.

**Features:**
- AI-generated story branches
- Only numbered choices (simpler than dungeon)
- `:back` to explore different paths
- Emoji-enhanced choices

**Run:**
```bash
python3 05_choice_story.py
```

**How to play:**
- Read the story
- Enter 1, 2, or 3 to choose
- Use `:back` to try different choices

---

### 6. MUD Client (`06_mud_client.py`)

A single-player MUD (Multi-User Dungeon) with AI NPCs.

**Features:**
- AI-powered NPC conversations
- Ambient NPC behaviors (async)
- Real-time events
- Multiple NPCs with personalities

**Run:**
```bash
python3 06_mud_client.py
```

**Commands:**
- `look` - Look around
- `say <npc> <message>` - Talk to NPC
- `who` - List NPCs
- `help` - Show commands

**Try:**
- `say merchant hello`
- `say guard what's happening?`
- `say wizard teach me magic`

---

## Key Features Demonstrated

| Example | AI Integration | Async/Streaming | Vim Features | Color Usage |
|---------|---------------|----------------|--------------|-------------|
| 1. Multi-Agent | ✅ Dual agents | ✅ Streaming | `:clear`, `:quit` | Agent colors |
| 2. Tool Execution | ✅ Single agent | ✅ Simulated | `:tools`, `:quit` | Tool highlights |
| 3. AI Dungeon | ✅ Story generation | ✅ Streaming | `:back`, `:restart` | Items/exits |
| 4. Text Adventure | ❌ Pure logic | ❌ Synchronous | `:restart` | Rich scene colors |
| 5. Choice Story | ✅ Branching narrative | ✅ Streaming | `:back`, `:restart` | Choice highlights |
| 6. MUD Client | ✅ NPC AI | ✅ Ambient events | `:quit` | NPC events |

## Development

### File Structure

```
examples/
├── README.md                    # This file
├── shared_helpers.py            # Common utilities
├── 01_multi_agent_chat.py      # Multi-agent conversation
├── 02_tool_execution.py        # Tool calling demo
├── 03_ai_dungeon.py            # AI text adventure
├── 04_text_adventure.py        # Classic adventure (no AI)
├── 05_choice_story.py          # Branching story
└── 06_mud_client.py            # MUD with NPCs
```

### Color Palette

All examples use a consistent color scheme (defined in `shared_helpers.py`):

- **User input:** White
- **AI responses:** Light Blue (cyan-ish)
- **System messages:** Green
- **Errors:** Dark Red
- **Highlights:** Yellow (items, choices, tools)
- **Metadata:** Grey (thinking, status)

## Tips

1. **Try without API key first** - All examples have mock modes for testing
2. **Use :back liberally** - In dungeon and story examples, explore different paths
3. **Check :help** - Most examples have built-in help commands
4. **Vim navigation** - Use vim commands you know (`:quit`, `:restart`, etc.)

## Troubleshooting

**"No module named 'anthropic'"**
```bash
pip install anthropic
```

**"API key not found"**
- Examples will run in mock mode automatically
- To enable AI: `export ANTHROPIC_API_KEY="your-key"`

**"Module not found 'textbox'"**
```bash
# Install from parent directory
pip install -e ..
```

## Next Steps

- Take screenshots of examples for documentation
- Try creating your own textbox application
- Explore the textbox API in `../docs/`

---

**Built with [Textbox](https://github.com/jcronq/textbox)** - A vim-inspired terminal UI library for Python

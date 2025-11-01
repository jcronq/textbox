# Example Implementation Plans

Simple demo examples showcasing Textbox for AI agents and text adventures.

---

## 1. Multi-Agent Conversation Viewer

**Purpose**: Show multiple AI agents conversing with streaming responses

**Visual Layout**:
```
┌─────────────────────────────────────────────┐
│ Multi-Agent Conversation                    │
│                                             │
│ User: What's the capital of France?         │
│                                             │
│ Agent_1: Let me look that up...            │
│ Agent_1: The capital of France is Paris.   │
│                                             │
│ Agent_2: I can confirm that's correct.     │
│                                             │
│ > [Your input here]                         │
│                                             │
│ :help for commands                          │
└─────────────────────────────────────────────┘
```

**Features**:
- 3 colored speakers: User (white), Agent_1 (blue), Agent_2 (green)
- Streaming responses with anthropic API
- Commands: `:clear`, `:agents` (list agents), `:quit`
- Agents respond in sequence to user input (not to each other)
- Mock mode: Uses canned responses if no API key

**Implementation**:
1. Use existing `llm_interface.py` as base
2. Two system prompts (one per agent personality)
3. Simple flow: User → Agent_1 responds → Agent_2 adds perspective
4. Color each agent differently using ColorCode
5. Mock responses for testing without API
6. ~150-200 lines of code

**API Usage**: 2 Claude API calls per user message (sequential, not parallel)

---

## 2. AI Agent with Tool Execution Display

**Purpose**: Show AI agent thinking process and tool calls

**Visual Layout**:
```
┌─────────────────────────────────────────────┐
│ AI Agent with Tools                         │
│                                             │
│ > User: What's the weather in SF?          │
│                                             │
│ [Agent] Thinking: I need weather data...   │
│ [Tool] Calling: get_weather("SF")          │
│ [Tool] Result: {"temp": 65, "sky": "☀️"}   │
│                                             │
│ > Agent: It's 65°F and sunny in SF!        │
│                                             │
│ > [Your input here]                         │
│                                             │
│ :help for commands                          │
└─────────────────────────────────────────────┘
```

**Features**:
- Mock tool functions (weather, time, calculator)
- Color scheme: User (white), Thinking (grey), Tools (yellow), Response (blue)
- Simulated streaming with delays (not real Claude tools API)
- Commands: `:tools` (list available), `:clear`, `:quit`
- Mock mode: Pre-scripted tool usage demo

**Implementation**:
1. Define 3 simple mock tools (return hardcoded data)
2. Simple pattern matching to detect when tools are needed
3. Display "[Agent] Thinking..." then "[Tool] Calling..." with delays
4. Show mock tool results in yellow
5. Display final synthesized response
6. **Simplified**: Mock the tool calling display, don't use real Claude tools API
7. ~180-220 lines of code

**API Usage**: 1 Claude API call per query (or 0 in mock mode with scripted demo)

---

## 3. Interactive AI Dungeon Master

**Purpose**: AI-generated text adventure with vim commands

**Visual Layout**:
```
┌─────────────────────────────────────────────┐
│ AI Dungeon Master                           │
│                                             │
│ 🏰 The Ancient Castle                       │
│                                             │
│ You stand before massive oak doors. Torches │
│ flicker on stone walls. A SILVER KEY lies   │
│ on the ground. Exits: NORTH, EAST          │
│                                             │
│ > take key                                  │
│ You pick up the silver key.                │
│                                             │
│ > [Your action]                             │
│                                             │
│ :back, :save, :load, :quit                 │
└─────────────────────────────────────────────┘
```

**Features**:
- AI generates room descriptions and responses to actions
- Color scheme: Locations (blue), Items (yellow), Exits (green), Actions (white)
- Vim commands: `:back` (undo last action), `:restart`
- Simple inventory system
- System prompt defines game world and rules
- Mock mode: Pre-defined dungeon with 3-4 rooms

**Implementation**:
1. System prompt with game rules and response format
2. Maintain game state (inventory, action history)
3. Claude generates responses to player actions
4. Parse AI responses for items, exits, descriptions
5. `:back` removes last action from history and regenerates
6. **Simplified**: Removed save/load, focus on `:back` for exploration
7. ~200-250 lines of code

**API Usage**: 1 Claude API call per player action (cumulative context)

---

## 4. Classic Interactive Fiction Engine

**Purpose**: Pure text adventure (no AI) showing vim features

**Visual Layout**:
```
┌─────────────────────────────────────────────┐
│ Cave Adventure                              │
│                                             │
│ === Dark Cave ===                           │
│ You are in a dimly lit cave. Water drips   │
│ from stalactites above.                     │
│                                             │
│ Items: RUSTY SWORD, TORCH                   │
│ Exits: NORTH, EAST                          │
│                                             │
│ > take sword                                │
│ You take the rusty sword.                   │
│                                             │
│ > [Your command]                            │
│                                             │
│ Commands: look, take, go, inventory, help  │
└─────────────────────────────────────────────┘
```

**Features**:
- Hardcoded game world (4-5 rooms)
- Parser for commands: take, drop, go, look, inventory
- Color scheme: Room names (blue), Items (yellow), Exits (green)
- Vim features: command history via textbox
- Commands: `:restart`, `:help`
- Win condition: Simple puzzle (unlock door with key)

**Implementation**:
1. Define room dict with connections, items, descriptions
2. Game state: current room, inventory
3. Command parser (simple split and match)
4. Room transition logic with locked doors
5. **Simplified**: No save/load, just `:restart`
6. NO AI - pure logic
7. ~150-180 lines of code

**API Usage**: None (no AI)

---

## 5. Multi-Choice Story Game

**Purpose**: Branching narrative with undo/redo exploration

**Visual Layout**:
```
┌─────────────────────────────────────────────┐
│ The Dragon's Choice                         │
│                                             │
│ A massive dragon blocks your path, smoke    │
│ billowing from its nostrils. Its eyes glow  │
│ with ancient intelligence.                  │
│                                             │
│ What do you do?                             │
│                                             │
│   [1] 🗡️  Fight the dragon                  │
│   [2] 💬 Try to negotiate                   │
│   [3] 🏃 Run away                           │
│                                             │
│ Enter choice (1-3): _                       │
│                                             │
│ :back to undo, :restart, :quit             │
└─────────────────────────────────────────────┘
```

**Features**:
- AI generates story and choices based on previous selections
- Color scheme: Story (white), Choices (yellow with emoji), Outcomes (blue)
- Vim `:back` to explore different paths
- System tracks choice history
- Emoji indicators for choice types
- **Only numbered choices** - no free text input (simpler than dungeon)
- Mock mode: Pre-scripted story tree

**Implementation**:
1. System prompt for story generation with strict choice format
2. Maintain choice history stack (number selected at each step)
3. Claude generates next scene + exactly 3 choices with emoji
4. Parse choices with regex and present numbered list
5. User enters 1-3, no other input accepted
6. `:back` pops history and regenerates previous scene
7. **Simplified**: Only choice-driven, distinct from free-text dungeon
8. ~170-200 lines of code

**API Usage**: 1 Claude API call per choice made

---

## 6. MUD-Style Game Client

**Purpose**: Real-time multiplayer text game interface (simulated)

**Visual Layout**:
```
┌─────────────────────────────────────────────┐
│ MUD Client - Town Square                   │
│                                             │
│ [Server] PlayerX has entered the room.     │
│ [Look] You are in a bustling town square.  │
│ [Server] PlayerY says: "Hello everyone!"   │
│                                             │
│ > say Hello!                                │
│ [You] Hello!                                │
│                                             │
│ [Server] PlayerX waves at you.             │
│                                             │
│ > [Your command]                            │
│                                             │
│ Commands: say, emote, look, go, who        │
└─────────────────────────────────────────────┘
```

**Features**:
- Simulated NPC events (async background task)
- AI generates NPC responses and environment descriptions
- Color scheme: NPC events (green), You (white), NPCs (blue), System (yellow)
- Real-time async updates
- Commands: `say`, `look`, `go`, `who`
- **Simplified**: Single-player with NPCs, not multiplayer simulation
- Mock mode: Pre-scripted NPC behaviors

**Implementation**:
1. Background async task generates NPC ambient messages (every 10-30s)
2. Claude API responds as specific NPCs when player talks to them
3. System prompt defines 2-3 NPCs with personalities
4. Parse player commands (say [npc] [message], look, go, who)
5. Async message queue for NPC events
6. Display messages with color based on source
7. **Simplified**: NPCs only, no "other players"
8. ~220-250 lines of code

**API Usage**: 1 Claude API call per player interaction with specific NPC

---

## Implementation Order & Dependencies

### Phase 1: Foundation (No AI)
**Example 4: Classic Interactive Fiction** - Establishes patterns without API complexity

### Phase 2: Simple AI Integration
**Example 1: Multi-Agent Conversation** - Basic Claude API streaming
**Example 2: Tool Execution Display** - Claude API with tools

### Phase 3: Advanced AI Features
**Example 3: AI Dungeon Master** - Complex state + AI generation
**Example 5: Multi-Choice Story** - AI with undo/redo tree

### Phase 4: Async Features
**Example 6: MUD Client** - Async updates + AI NPCs

---

## Common Dependencies

All examples will need:
- `anthropic` package: `pip install anthropic`
- API key in environment: `ANTHROPIC_API_KEY` (optional - falls back to mock mode)
- Base imports from textbox
- Shared helper functions in `shared_helpers.py`:
  - `get_claude_client()` - Returns Anthropic client or None
  - `has_api_key()` - Check if API key is available
  - Standard color palette constants

## Standard Color Palette

All examples use consistent colors:
- **User input**: `ColorCode.WHITE`
- **AI/Agent responses**: `ColorCode.BLUE` (cyan-ish)
- **System messages**: `ColorCode.GREEN`
- **Errors**: `ColorCode.RED`
- **Highlights** (items, choices): `ColorCode.YELLOW`
- **Metadata** (thinking, tools): `ColorCode.GREY`

## File Structure

```
examples/
├── 01_multi_agent_chat.py
├── 02_tool_execution.py
├── 03_ai_dungeon.py
├── 04_text_adventure.py
├── 05_choice_story.py
├── 06_mud_client.py
├── shared_helpers.py (optional)
└── README.md (usage instructions)
```

---

## Next Steps

1. Review this plan
2. Identify any issues or improvements
3. Begin implementation in order
4. Test each example
5. Take screenshots
6. Update documentation

# Smart Meeting Assistant with Background Task Execution

A meeting assistant that can execute tasks in the background while the meeting continues. Uses collaborative mode — GetSun (collaborative voice intelligence) handles conversation naturally while the agent executes tools in parallel and delivers results back to the meeting.

## The Key Pattern

```
Alice: "Juno, can you pull up Q3 revenue by region?"

GetSun (INSTANT — from capabilities context):
  "Sure, I'll pull up the Q3 regional revenue right now."
  ↑ This is instant because GetSun's context describes the database lookup capability.
    It knows it can promise this.

Meanwhile (meeting continues normally):
  Agent detects task → spawns background coroutine → queries database...

3 seconds later, results ready:
  Agent → voice.context_update (data now in GetSun's memory)
  Agent → inject.natural ("Q3 revenue: NA $1.2M, Europe $800K, APAC $400K")

GetSun (at next natural pause):
  "I've got those Q3 numbers. North America led with 1.2 million,
   Europe came in at 800K, and Asia Pacific at 400K."

Later:
  Bob: "Juno, how does Europe compare to last quarter?"
  GetSun: "Based on the data I pulled up, Europe's 800K this quarter was..."
  ↑ Follow-up works because the data is in GetSun's context
```

## Why Each Pattern Matters

### Why voice.context_update (persistent knowledge)

When the agent updates GetSun's context with task results, that data becomes part of GetSun's knowledge for the rest of the meeting. Without this:

- ❌ Someone asks a follow-up → GetSun says "I don't have that information"
- ✅ Someone asks a follow-up → GetSun answers from the data in its context

Context update makes results **persistent and queryable** — not just a one-time announcement.

### Why inject.natural (immediate delivery)

GetSun won't volunteer information it hasn't been asked about. Even after a context update, GetSun waits to be asked. `inject.natural` tells GetSun: "speak this information now, at the next natural pause." Without this:

- ❌ Data is in context but nobody knows → awkward silence, someone has to ask again
- ✅ GetSun proactively shares: "I've got those numbers" → natural flow

inject.natural makes results **delivered immediately** without waiting.

### Why both together

| Alone | Problem |
|-------|---------|
| Only context_update | Data available but not announced — participants don't know results are ready |
| Only inject.natural | Results spoken once but lost — follow-up questions fail |
| **Both** | **Immediate delivery + persistent knowledge** |

### Why asyncio.create_task (parallel execution)

Tasks run as background coroutines. The main event loop continues receiving meeting events:

- ❌ Synchronous: meeting events queue up, voice states delayed, bot feels frozen
- ✅ Async: meeting flows naturally, multiple tasks run simultaneously

If someone asks "look up revenue AND create a ticket", both execute in parallel.

### Why instant acknowledgment (capabilities in context)

GetSun's initial context describes available tools. When someone asks for a task, GetSun already knows it can do it — so it responds immediately:

- ❌ No capabilities in context: GetSun says "I don't know how to do that" (because it doesn't know it can)
- ✅ Capabilities in context: GetSun says "Sure, I'll look that up" (because the context says it can)

The capabilities context is what enables the **zero-latency acknowledgment**. The tools only execute when the agent detects the task — but the participant hears confirmation instantly.

### Why graceful failure

If a tool fails (database timeout, API error), the agent injects an error message:

- ❌ Silent failure: participant waits forever for results that never come
- ✅ Inject error: "I wasn't able to complete that lookup. Could you give me more details?"

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Agent (Python)                         │
│                                                           │
│  ┌──────────────────┐    ┌─────────────────────────────┐ │
│  │ Event Loop       │    │ Background Tasks             │ │
│  │                  │    │                               │ │
│  │ transcript.final │───>│ LLM: is this a task?         │ │
│  │   → detect task  │    │   yes → asyncio.create_task  │ │
│  │                  │    │     → execute tool            │ │
│  │ voice.state ──>  │    │     → context_update          │ │
│  │   log            │    │     → inject.natural           │ │
│  │                  │    │                               │ │
│  │ voice.text ──>   │    │ Multiple tasks run in         │ │
│  │   log            │    │ parallel simultaneously       │ │
│  └──────────────────┘    └─────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Context Manager                                      │ │
│  │ persona + capabilities (static)                      │ │
│  │ + task results (dynamic, accumulated, ≤4000 chars)   │ │
│  │ → voice.context_update on every result               │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

         ↕ WebSocket

┌──────────────────���──────────────────────────────────────┐
│ AgentCall + GetSun (collaborative voice intelligence)    │
│                                                           │
│ - Listens to meeting transcripts automatically            │
│ - Detects trigger words, waits for silence                │
│ - Answers from meeting memory + context (with results)    │
│ - Speaks inject.natural content at next pause             │
│ - Avatar shows voice states (7 states)                    │
└─────────────────────────────────────────────────────────┘
```

## Available Tools

| Tool | Description | Example |
|------|-------------|---------|
| `database_lookup` | Query company data — revenue, orders, customers | "Q3 revenue by region" |
| `document_search` | Search docs, policies, knowledge base | "vacation policy" |
| `calculate` | Calculations, comparisons, projections | "15% growth on $2.4M" |
| `create_ticket` | Create tasks/tickets in project management tools | "Create task for Bob" |

**Note:** GetSun (collaborative voice intelligence) can also search the web in realtime on its own — no tool needed for general web questions. Tools are for tasks that need specific company data, documents, or actions.

Tools are defined in `tools.py` — add your own by writing an async function and adding it to the `TOOLS` dict.

## Setup

```bash
pip install requests websockets
# Plus your LLM SDK for task detection:
pip install anthropic  # or openai, google-generativeai

export AGENTCALL_API_KEY="ak_ac_your_key"
export ANTHROPIC_API_KEY="sk-ant-..."

python assistant.py "https://meet.google.com/abc-def-ghi"
```

## Usage

```bash
# Default: Juno with database, docs, calculate, tickets
python assistant.py "https://meet.google.com/abc-def-ghi"

# Custom name and triggers
python assistant.py "https://meet.google.com/abc" --name "Aria" --triggers "aria,hey aria"

# Custom voice
python assistant.py "https://meet.google.com/abc" --voice voice.bella
```

## Example Session

```
Creating smart meeting assistant:
  Bot name: Juno
  Tools: database_lookup, document_search, calculate, create_ticket
  Mode: webpage-av (avatar) + collaborative

Bot is in the meeting with avatar visible.
Tools available: database_lookup, document_search, calculate, create_ticket

  + Alice joined
  + Bob joined
  👂 Voice state: listening
  [Alice] Let's review the quarterly numbers. Bob, what's the overview?
  [Bob] Revenue was around 2.4 million I believe.
  [Alice] Hey Juno, can you pull up the exact Q3 revenue by region?
  🎯 Voice state: actively_listening
  🎯 Task detected: database_lookup — Q3 regional revenue
  ⚙️  Executing: database_lookup("Q3 revenue by region")
  🧠 Voice state: thinking
  🗣️ Voice state: speaking
  💬 Juno said: "Sure, I'll pull up the Q3 regional breakdown right now."
  🔊 Speaking...
  🔇 Done speaking
  👂 Voice state: listening
  [Bob] While Juno looks that up, let me also mention we closed 3 new enterprise deals.
  📝 Context updated with: Q3 regional revenue
  💉 Injected results for: Q3 regional revenue
  ⏳ Voice state: waiting_to_speak
  🗣️ Voice state: speaking
  💬 Juno said: "I've got those Q3 numbers. North America led with 1.2 million..."
  🔊 Speaking...
  🔇 Done speaking
  👂 Voice state: listening
  [Alice] Thanks. Juno, how does that compare to Q2?
  🎯 Voice state: actively_listening
  🗣️ Voice state: speaking
  💬 Juno said: "I don't have Q2 data loaded yet. Want me to look that up?"
  [Alice] Yes please, and also create a task for Bob to prepare the Q4 forecast.
  🎯 Task detected: database_lookup — Q2 regional revenue
  🎯 Task detected: create_ticket — Bob to prepare Q4 forecast
  ⚙️  Executing: database_lookup("Q2 revenue by region")
  ⚙️  Executing: create_ticket("Bob to prepare Q4 forecast")
  🗣️ Voice state: speaking
  💬 Juno said: "On it — I'll pull up Q2 numbers and create that task for Bob."
  📝 Context updated with: Task for Bob
  💉 Injected results for: Task for Bob
  📝 Context updated with: Q2 regional revenue
  💉 Injected results for: Q2 regional revenue
  🗣️ Voice state: speaking
  💬 Juno said: "I've created a task for Bob to prepare the Q4 forecast.
                  And for Q2 comparison..."

Call ended: left
Meeting log saved to: smart-meeting-log-2026-04-03-1500.md
```

## Billing

| Component | Charged? | Notes |
|-----------|----------|-------|
| Meeting bot (base) | Yes | Per minute of call |
| Speech-to-text | Yes | Per minute |
| Voice intelligence | Yes | Collaborative mode |
| Text-to-speech | Yes | Per minute of generated audio |
| LLM (task detection) | Yes | Billed by your LLM provider |
| Tool execution | Varies | Depends on your APIs/databases |

## Context Size Management

GetSun's context is limited to 4000 characters. The ContextManager handles this:

- **Capabilities** (static) — always kept, never trimmed
- **Task results** (dynamic) — newest kept, oldest trimmed when over limit
- On each new result: capabilities + all results rebuilt, oldest dropped if over 4000 chars

For long meetings with many tasks, early results may be trimmed. Consider storing full results in the meeting log for reference.

## Extending

### Add a new tool

```python
# In tools.py:
async def slack_notify(query: str) -> str:
    """Send a Slack message to a channel."""
    # await slack.chat.postMessage(channel="#general", text=query)
    return f"Message sent to Slack: {query}"

TOOLS["slack_notify"] = {
    "fn": slack_notify,
    "description": "Send messages to Slack channels",
    "examples": "notify #engineering about deployment, message #sales about the deal",
}
```

The assistant automatically includes the new tool in GetSun's capabilities context.

### Real tool implementations

Replace the placeholder functions in `tools.py` with actual API calls:
- **Database**: connect to PostgreSQL, MongoDB, or a REST API
- **Documents**: use Pinecone, Elasticsearch, or Notion API for RAG
- **Calculations**: pandas, numpy, or LLM-assisted computation
- **Tickets**: Linear, Jira, Asana, or Notion API

### Add more intelligence

- **Proactive contributions**: detect when the agent has relevant data and `voice.contribute` without being asked
- **Smart context**: use an LLM to summarize old results before trimming (compress instead of drop)
- **Multi-step tasks**: chain tools (e.g., look up revenue → calculate growth → create report)
- **Memory across meetings**: persist context to a database, load relevant history on join

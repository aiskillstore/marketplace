# Collaborative Mode — Complete Guide

Collaborative mode lets your AI agent participate in group meetings naturally using voice intelligence (GetSun (collaborative voice intelligence)). The agent listens for its name, responds intelligently, handles interruptions, and maintains conversational context — all automatically.

## How It Works

```
Meeting participants talk
        │
        ▼
FirstCall (meeting infrastructure) captures audio → transcribes (STT)
        │
        ├── transcript.partial ──► GetSun (collaborative voice intelligence) (for interruption detection)
        │   (in-progress text)       Someone is still talking.
        │                            If GetSun (collaborative voice intelligence) is speaking, it detects
        │                            the interruption and stops.
        │
        └── transcript.final ──► GetSun (collaborative voice intelligence) (text.full)
            (complete sentence)      GetSun (collaborative voice intelligence) checks: did they say my name?
                                     │
                                     ├── YES → thinking → prepare response
                                     │         → wait for silence
                                     │         → speak (audio chunks)
                                     │
                                     └── NO  → stay listening
```

## Setup

```python
call = await client.create_call(
    meet_url="https://meet.google.com/abc-def-ghi",
    bot_name="June",
    mode="audio",
    voice_strategy="collaborative",
    transcription=True,
    collaborative={
        "trigger_words": ["june", "juno", "hey june"],
        "barge_in_prevention": True,
        "interruption_use_full_text": True,
        "context": "You are June, a financial analyst AI. You help with revenue data and market analysis.",
        "voice": "voice.heart"
    }
)
```

## Configuration Reference

### `trigger_words` — Alternate Names

STT engines often mishear names. List all common misheard spellings so the agent responds reliably.

```json
{
  "trigger_words": ["june", "juno", "joon", "hey june", "june bot"]
}
```

**How it works:** When GetSun (collaborative voice intelligence) receives `text.full`, it checks if the text contains the `bot_name` OR any of the `trigger_words`. If found, it begins processing a response.

### `barge_in_prevention` — Wait for Silence

When `true` (default), GetSun (collaborative voice intelligence) waits until nobody is talking before it starts speaking. This prevents the bot from talking over people.

```
barge_in_prevention: true
  → Someone says "June, what was revenue?"
  → GetSun (collaborative voice intelligence) prepares answer (state: thinking)
  → Alice is still talking... (state: waiting_to_speak)
  → Alice stops (state: speaking → audio plays)

barge_in_prevention: false
  → Someone says "June, what was revenue?"
  → GetSun (collaborative voice intelligence) starts speaking immediately (may overlap)
```

### `interruption_use_full_text` — Smart Interruption Handling

When `true` (default), GetSun (collaborative voice intelligence) uses the full transcribed text during interruptions to decide how to respond, rather than waiting for the speaker to fully stop. This makes the bot more responsive to being redirected mid-speech.

```
interruption_use_full_text: true
  → Bot is speaking about Q3 revenue
  → Alice interrupts: "Actually, what about Q2?"
  → GetSun (collaborative voice intelligence) immediately understands the redirect
  → Stops Q3 response, switches to Q2

interruption_use_full_text: false
  → Bot is speaking about Q3 revenue
  → Alice interrupts: "Actually, what about Q2?"
  → GetSun (collaborative voice intelligence) stops speaking but waits for Alice to fully finish
  → Then processes the interruption
```

### `voice` — GetSun (collaborative voice intelligence) TTS Voice

4 available voices:
- `voice.heart` — female, warm (default)
- `voice.bella` — female, professional
- `voice.echo` — male, calm
- `voice.eric` — male, energetic

### `context` — Knowledge Scratchpad

The most powerful feature. See the dedicated section below.

---

## Voice States

Your agent receives `voice.state` events as GetSun (collaborative voice intelligence) transitions through 7 states:

```
listening              → Idle. Waiting for its name.
        │
        ▼ (name detected in partial text)
actively_listening     → Recognized it's being addressed. Brief transition.
        │
        ▼ (text.full received, processing)
thinking               → Preparing response from context + conversation.
        │
        ▼ (response ready, waiting for silence)
waiting_to_speak       → Has answer but someone is talking. Holding.
        │                 (only with barge_in_prevention: true)
        ▼ (silence detected)
speaking               → Audio streaming to meeting.
        │
        ├──── interrupted → Someone started talking mid-speech.
        │                    Stops audio. Evaluates what was said.
        │                    May respond to the interruption or go to listening.
        │
        ▼ (finished speaking)
contextually_aware     → Follow-up window (20 seconds).
                          Will respond to next utterance WITHOUT
                          needing its name again.
                          After 20s → back to listening.
```

---

## Context System — In Detail

### What is Context?

Context is a **swappable knowledge layer** — facts, data, and instructions that GetSun (collaborative voice intelligence) uses when generating responses. It is NOT conversation memory.

| | Context | Conversation |
|---|---|---|
| What | Facts you feed in | Everything said in the meeting |
| Managed by | Your agent (via `voice.context_update`) | GetSun (collaborative voice intelligence) (automatic) |
| Persistence | Replaced each time you update | Never cleared, accumulates |
| Max size | 4,000 characters | Unlimited (full session) |
| Purpose | Give GetSun (collaborative voice intelligence) knowledge to answer from | GetSun (collaborative voice intelligence) tracks who said what |

**Key insight:** GetSun (collaborative voice intelligence) remembers the entire conversation automatically. Context is for external knowledge the agent brings in — database results, API responses, file contents, analysis results.

### When to Update Context

Update context whenever your agent learns something new that GetSun (collaborative voice intelligence) should know:

```python
# After fetching data from a database
await client.send_command({
    "type": "voice.context_update",
    "text": "Customer: Acme Corp. Renewal: June 2026. ARR: $450K. 3 P1 incidents last month."
})

# After completing an analysis
await client.send_command({
    "type": "voice.context_update",
    "text": "Financial analysis complete. Q3 revenue: $2.4M (+15% YoY). Enterprise: $1.6M. SMB: $0.8M. Top customer: Acme Corp ($450K). Churn: 2.1%. MRR growth: $45K/month."
})

# After looking up documentation
await client.send_command({
    "type": "voice.context_update",
    "text": "Feature X supports: batch processing (up to 10K items), real-time streaming, webhook notifications. Pricing: $0.001/item for batch, $0.01/minute for streaming. Available in all regions except ap-south-1."
})
```

### Context Examples by Use Case

**Meeting Assistant (financial data):**
```python
context = """You are June, a financial analyst AI for Pattern AI Labs.

Current data:
- Q3 Revenue: $2.4M (up 15% YoY)
- Enterprise segment: $1.6M (67% of total)
- SMB segment: $0.8M (33% of total)
- Gross margin: 72%
- Top 5 customers: Acme ($450K), Globex ($380K), Initech ($290K), Umbrella ($240K), Cyberdyne ($180K)
- Churn rate: 2.1% (down from 3.4% in Q2)
- MRR growth: $45K/month
- Cash runway: 18 months

Key metrics to highlight: Enterprise growth (+22%), churn improvement, expanding margins.
Avoid discussing: M&A plans, unreleased products, employee count."""
```

**Customer Support Agent:**
```python
context = """You are June, customer support for AgentCall.

Customer: Alice Chen (alice@acme.com)
Account: Enterprise tier, 14 months active
Current issue: TTS latency spikes during peak hours (reported 2 days ago)
Ticket: SUP-4521 (priority: high)

Resolution status: Engineering identified the root cause (GPU fleet auto-scaling delay).
Fix deployed: Yesterday at 3pm UTC. Monitoring shows latency back to normal (<200ms p95).

Customer sentiment: frustrated (3 support tickets this month)
Recommended action: Confirm fix is working, offer 1 month credit as goodwill."""
```

**Code Review Assistant:**
```python
context = """You are June, a code review assistant.

PR #847: "Add WebSocket connection pooling"
Author: Bob
Files changed: 4 (ws_pool.go, manager.go, manager_test.go, config.go)

Analysis results:
- No security issues found
- Test coverage: 87% (up from 82%)
- Performance: connection reuse reduces latency by ~40ms per reconnect
- Concern: pool max size (100) may be too low for enterprise customers
- Suggestion: make pool size configurable via POOL_MAX_SIZE env var
- Build status: passing (all 142 tests green)"""
```

---

## The Context-First Pattern

The recommended way to use collaborative mode. Your agent fetches data, updates context, then lets GetSun (collaborative voice intelligence) answer naturally.

### Basic Pattern

```python
async for event in client.connect_ws(call_id):
    if event.get("type") == "transcript.final":
        text = event["text"]
        speaker = event["speaker"]["name"]
        
        # 1. Check if it's relevant to our domain
        if needs_data_lookup(text):
            # 2. Fetch the data (async — don't block)
            data = await fetch_from_database(text)
            
            # 3. Update GetSun (collaborative voice intelligence)'s context with fresh data
            await client.send_command({
                "type": "voice.context_update",
                "text": format_context(data)
            })
            
            # 4. Tell GetSun (collaborative voice intelligence) to respond (guaranteed response)
            await client.send_command({
                "type": "trigger.speak",
                "text": text,
                "speaker": speaker
            })
```

### Why trigger.speak after context_update?

In collaborative mode, GetSun (collaborative voice intelligence) only responds when it hears its name. But what if the agent fetched data that changes the answer? The flow is:

1. Alice says: "June, what's Acme's renewal date?"
2. GetSun (collaborative voice intelligence) hears "June" → starts thinking
3. **BUT** GetSun (collaborative voice intelligence) doesn't have the CRM data yet
4. Agent fetches CRM data → updates context
5. Agent sends `trigger.speak` with the original question
6. Now GetSun (collaborative voice intelligence) answers from the enriched context: "Acme's renewal is in June 2026"

Without step 5, GetSun (collaborative voice intelligence) might answer with "I don't have that information" because the context wasn't ready when it first heard the question.

---

## Injecting Updates Into the Meeting

When your agent completes a background task, announce it with a SHORT `inject.natural`
(1 sentence). Put the full data in `context_update` so follow-up questions work instantly.

**IMPORTANT:** `inject.natural` has high reliability — if interrupted, GetSun retries until
fully spoken. Keep inject text to 1 sentence to avoid interrupt-retry loops. `trigger.speak`
is conversational — if interrupted, content is lost (like a person being cut off).

### Example: Background Task Completion

```python
# Someone asked the bot to analyze financial data
# Bot says "I'll analyze that and get back to you"
# Agent runs the analysis in the background...

async def on_analysis_complete(results):
    # 1. Update context with the results
    await client.send_command({
        "type": "voice.context_update",
        "text": f"Analysis complete. {format_results(results)}"
    })
    
    # 2. Raise hand to visually indicate we want to speak
    await client.send_command({
        "type": "meeting.raise_hand"
    })
    
    # 3. Inject a SHORT announcement (1 sentence only)
    # Full data is already in context — user can ask follow-ups
    await client.send_command({
        "type": "inject.natural",
        "text": "I've completed the financial analysis.",
        "priority": "normal"
    })
    
    # GetSun speaks: "I've finished the financial analysis."
    # User: "What were the key findings?" → GetSun answers from context instantly
```

### inject.natural vs inject.verbatim

| | inject.natural | inject.verbatim |
|---|---|---|
| What GetSun (collaborative voice intelligence) does | Rephrases into natural speech | Speaks exact text as-is |
| When to use | Data, bullet points, raw facts | Exact quotes, legal text, names |
| Example input | "revenue Q3: $2.4M, up 15%" | "The meeting will end in 5 minutes" |
| Example output | "Our Q3 revenue was 2.4 million dollars, which is up 15 percent" | "The meeting will end in 5 minutes" |

### Example: inject.natural for Different Scenarios

```python
# Scenario 1: Research task completed
await client.send_command({
    "type": "inject.natural",
    "text": "Research on competitor pricing complete. AWS charges $16/1M chars for neural TTS. Google charges $16/1M. Our AgentCall TTS-based TTS is $8/hr, approximately 40% cheaper.",
    "priority": "normal"
})
# GetSun (collaborative voice intelligence) says: "I've completed the competitor pricing research. 
# AWS and Google both charge sixteen dollars per million characters 
# for neural text-to-speech. Our AgentCall TTS-based service runs at eight 
# dollars per hour, which works out to about forty percent cheaper."

# Scenario 2: Alert from monitoring
await client.send_command({
    "type": "inject.natural",
    "text": "Alert: Production API latency spike detected. P95 latency at 450ms (normal: 120ms). Root cause: database connection pool exhaustion. Auto-scaling triggered.",
    "priority": "high"  # high priority = speaks sooner in queue
})

# Scenario 3: Meeting timer
await client.send_command({
    "type": "inject.verbatim",  # exact text, no rephrasing
    "text": "Just a heads up, we have ten minutes remaining in this meeting.",
    "priority": "normal"
})
```

### Combining Raise Hand + Inject

For important announcements, raise hand first so participants see the visual indicator:

```python
# Step 1: Raise hand (visual cue in meeting UI)
await client.send_command({"type": "meeting.raise_hand"})

# Step 2: Inject the message (GetSun (collaborative voice intelligence) waits for silence, then speaks)
await client.send_command({
    "type": "inject.natural",
    "text": "The deployment to production has completed successfully. All health checks are passing.",
    "priority": "normal"
})

# What participants see:
# 1. Bot's hand raises in meeting UI
# 2. When nobody is talking, bot speaks:
#    "Hey everyone, just wanted to let you know the production 
#     deployment has completed. All health checks are passing."
# 3. Hand automatically lowers after speaking
```

---

## Full Working Example: Meeting Assistant with Background Tasks

```python
import asyncio
from agentcall import AgentCallClient

async def main():
    client = AgentCallClient(api_key="ak_ac_your_key")
    
    call = await client.create_call(
        meet_url="https://meet.google.com/abc-def-ghi",
        bot_name="June",
        mode="audio",
        voice_strategy="collaborative",
        transcription=True,
        collaborative={
            "trigger_words": ["june", "juno", "hey june"],
            "barge_in_prevention": True,
            "interruption_use_full_text": True,
            "context": (
                "You are June, an AI assistant for Pattern AI Labs. "
                "You can analyze financial data, look up customer information, "
                "and run code analysis. When asked to do something that takes time, "
                "say you'll work on it and come back with results."
            ),
            "voice": "voice.heart"
        }
    )
    
    pending_tasks = {}
    
    async for event in client.connect_ws(call["call_id"]):
        event_type = event.get("event") or event.get("type", "")
        
        if event_type == "transcript.final":
            text = event["text"]
            speaker = event["speaker"]["name"]
            
            # Check if someone is asking for a long-running task
            if "analyze" in text.lower() and "financial" in text.lower():
                # Start background analysis
                task = asyncio.create_task(run_financial_analysis())
                pending_tasks["financial"] = task
                
                # Update context so GetSun (collaborative voice intelligence) knows it can promise to do it
                await client.send_command({
                    "type": "voice.context_update",
                    "text": (
                        "You are June. You have been asked to analyze financial data. "
                        "You have started the analysis. Tell the user you'll work on it "
                        "and come back with results shortly."
                    )
                })
                await client.send_command({
                    "type": "trigger.speak",
                    "text": text,
                    "speaker": speaker
                })
                # GetSun (collaborative voice intelligence) says: "I'll run that financial analysis now 
                # and get back to you with the results."
                
                # Wait for task completion in background
                asyncio.create_task(wait_and_announce(client, task, "financial"))
            
            elif "customer" in text.lower():
                # Quick lookup — update context and respond immediately
                customer_data = await lookup_customer(text)
                await client.send_command({
                    "type": "voice.context_update",
                    "text": f"Customer data: {customer_data}"
                })
                await client.send_command({
                    "type": "trigger.speak",
                    "text": text,
                    "speaker": speaker
                })
        
        elif event_type == "voice.state":
            print(f"[voice] {event['state']}")
        
        elif event_type == "voice.text":
            print(f"[bot speaking] {event['text']}")
        
        elif event_type == "call.ended":
            break


async def wait_and_announce(client, task, task_name):
    """Wait for a background task, then announce results to the meeting."""
    result = await task
    
    # Update context with results
    await client.send_command({
        "type": "voice.context_update",
        "text": f"Analysis complete. Results: {result}"
    })
    
    # Raise hand + inject announcement
    await client.send_command({"type": "meeting.raise_hand"})
    await client.send_command({
        "type": "inject.natural",
        "text": f"The {task_name} analysis is complete. {summarize(result)}",
        "priority": "normal"
    })


async def run_financial_analysis():
    """Simulated long-running analysis."""
    await asyncio.sleep(30)  # simulate processing
    return {
        "revenue_q3": "$2.4M",
        "growth": "+15% YoY",
        "enterprise_share": "67%",
        "churn": "2.1%",
        "top_customer": "Acme Corp ($450K)"
    }


asyncio.run(main())
```

---

## Predictive Context Updates

The agent can preemptively update GetSun's context with data relevant to the current
discussion — BEFORE anyone asks. This makes GetSun answer instantly (<1s) instead of
deferring ("let me check") and waiting for the agent to fetch data.

```python
# Agent hears participants discussing deployment...
# Preload deployment data into context before anyone asks
await client.send_command({
    "type": "voice.context_update",
    "text": context_mgr.build()  # includes deployment status
})
# Now if someone asks "Is the deployment healthy?" → GetSun answers instantly
```

When to preload:
- Conversation shifts to a topic the agent has data on
- Agent just completed a task — results may be relevant
- Agent recognizes a pattern (participants keep asking about metrics)

`context_update` is silent — GetSun absorbs it without speaking. If nobody asks,
no harm. The 4000-char limit means prioritize data relevant to current discussion.

## Command Quick Reference

| Command | What It Does | When to Use |
|---|---|---|
| `voice.context_update` | Replace GetSun's knowledge scratchpad (4000 chars) | Preload data, after fetching results |
| `trigger.speak` | Force GetSun to respond (interruptible — content lost on interrupt) | Answering direct questions conversationally |
| `voice.contribute` | GetSun contributes from context at natural pause | When bot should chime in without being asked |
| `inject.natural` | GetSun speaks at right time (high reliability — retries on interrupt) | SHORT announcements only (1 sentence) |
| `inject.verbatim` | Speaks exact text (high reliability) | Exact quotes, timers, legal text (keep short) |
| `meeting.raise_hand` | Visual indicator in meeting UI | Before inject for important updates |
| `meeting.send_chat` | Send text to meeting chat | Sharing links, data better in text |

## Configuration Quick Reference

| Config | Default | What It Does |
|---|---|---|
| `trigger_words` | `[]` | Alternate names for the bot (handles STT mishearing) |
| `barge_in_prevention` | `true` | Wait for silence before speaking |
| `interruption_use_full_text` | `true` | Use full text during interruptions for smarter responses |
| `context` | `""` | Initial knowledge scratchpad |
| `voice` | `voice.heart` | TTS voice (heart/bella/echo/eric) |

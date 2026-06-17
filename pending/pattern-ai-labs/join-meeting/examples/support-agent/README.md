# Customer Support Agent (1-on-1)

An AI support agent that joins a call, listens to the customer, looks up information from a knowledge base, and responds naturally using TTS. Designed for turn-based 1-on-1 conversations.

## What It Does

1. Joins meeting in **audio mode** with **direct** voice strategy
2. Greets the customer with a welcome message via TTS
3. Listens for `transcript.final` events (customer speaking)
4. Sends conversation history + knowledge base to an LLM
5. LLM decides: respond, escalate to human, or end the call
6. Speaks the response via `tts.speak` WebSocket command
7. Loops steps 3-6 until resolved or escalated
8. Saves conversation log to markdown after the call

## Architecture

```
Customer speaks
    ↓
AgentCall STT → transcript.final event
    ↓
Agent receives transcript via WebSocket
    ↓
Agent sends conversation + knowledge base → LLM
    ↓
LLM returns: {"response": "...", "action": "respond|escalate|end"}
    ↓
Agent sends tts.speak command → AgentCall TTS → Customer hears response
    ↓
Repeat until resolved
```

## Files

| File | Purpose |
|------|---------|
| `agent.py` | Main agent loop — listen, think, speak |
| `knowledge.json` | Mock knowledge base — products, policies, FAQs |
| `README.md` | This file |

## Setup

```bash
pip install requests websockets
# Plus your chosen LLM SDK (e.g., pip install anthropic)

export AGENTCALL_API_KEY="ak_ac_your_key"
export ANTHROPIC_API_KEY="sk-ant-..."   # or OPENAI_API_KEY, GOOGLE_API_KEY

python agent.py "https://meet.google.com/abc-def-ghi"
```

## Options

```bash
# Custom bot name
python agent.py "https://meet.google.com/abc" --name "Sarah"

# Custom TTS voice (54 voices available)
python agent.py "https://meet.google.com/abc" --voice af_bella

# Custom output file
python agent.py "https://meet.google.com/abc" --output call-log.md
```

## Available TTS Voices

| Voice ID | Name | Gender | Language |
|----------|------|--------|----------|
| af_heart | Heart | Female | en-us |
| af_bella | Bella | Female | en-us |
| af_sarah | Sarah | Female | en-us |
| am_adam | Adam | Male | en-us |
| am_michael | Michael | Male | en-us |
| bf_emma | Emma | Female | en-gb |
| bm_george | George | Male | en-gb |

Run `GET /v1/tts/voices` for the full list of 54 voices across 9 languages.

## Billing

| Component | Charged? | Notes |
|-----------|----------|-------|
| Meeting bot (base) | Yes | Per minute of call |
| Speech-to-text | Yes | Per minute (needed to hear customer) |
| Voice intelligence | **No** | Direct mode — no GetSun |
| Text-to-speech | Yes | Per minute of generated audio |
| LLM (external) | Yes | Billed by your LLM provider |

## Example Conversation

```
Bot is in the meeting.

  Agent: Hello! Thanks for calling Acme Corp support. How can I help you today?
  Customer (Alice): Hi, I ordered a Laptop Pro 15 but I received a Laptop Air 13 instead.
  [thinking...]
  Agent: I'm sorry about that mix-up. I can see we carry both the Laptop Pro 15 and Laptop Air 13.
         Let me arrange a replacement for you — it'll ship within 2 business days with free return shipping.
  Customer (Alice): That would be great, how do I return the wrong one?
  [thinking...]
  Agent: We'll email you a prepaid return label. Just pack the Laptop Air 13 in its original box
         and drop it off at any carrier location. You have 14 days to return it.
  Customer (Alice): Perfect, thank you so much.
  [thinking...]
  Agent (closing): You're welcome! Your replacement Laptop Pro 15 will ship within 2 business days.
                   Thanks for contacting Acme Corp! Have a great day.

Call ended: resolved
Call log saved to: support-log-2026-04-03-1430.md
```

## Output (Call Log)

```markdown
# Support Call Log — 2026-04-03 14:30

**Call ID:** call-550e8400...
**End reason:** resolved
**Turns:** 8

---

## Conversation

👤 **Customer:** Hi, I ordered a Laptop Pro 15 but I received a Laptop Air 13 instead.

🤖 **Agent:** I'm sorry about that mix-up. Let me arrange a replacement...

👤 **Customer:** That would be great, how do I return the wrong one?

🤖 **Agent:** We'll email you a prepaid return label...

---

## Post-Call Actions

# TODO: Create support ticket in Zendesk/Freshdesk
# TODO: Log interaction in CRM
```

## How the LLM Decides

The LLM receives:
- **System prompt** with company knowledge base (products, policies, FAQs)
- **Conversation history** (all customer + agent turns)
- **Instructions** to respond with JSON: `{"response": "...", "action": "respond|escalate|end"}`

| Action | When | What happens |
|--------|------|-------------|
| `respond` | Customer has a question/issue | Agent speaks the response, continues listening |
| `escalate` | Agent can't help (not in knowledge base) | Agent says escalation message, leaves call |
| `end` | Issue resolved, customer says goodbye | Agent says farewell, leaves call |

## Knowledge Base

`knowledge.json` is a mock data file with:
- Company name and messages (greeting, farewell, escalation)
- Product catalog (ID, name, price, specs)
- Policies (returns, replacements, refunds, warranty, shipping)
- FAQs (common questions and answers)

In production, replace this with real data sources:

```python
# Instead of loading knowledge.json, query your systems:
def get_knowledge(customer_id):
    orders = crm.get_orders(customer_id)
    account = crm.get_account(customer_id)
    products = catalog.search(relevant_to=orders)
    return format_for_prompt(orders, account, products, POLICIES)
```

## Customization Ideas

- **CRM integration** — look up customer by phone/email, pull order history
- **Real-time order lookup** — when customer gives order number, query live DB
- **Sentiment tracking** — monitor customer sentiment, escalate if frustrated
- **Multi-language** — detect language, switch TTS voice and LLM prompt language
- **Call recording** — add `audio_streaming: true` to save audio alongside transcript
- **Quality scoring** — post-call LLM analysis of agent performance
- **Auto-ticketing** — create support ticket automatically with resolution details
- **Transfer to human** — instead of leaving, keep bot as observer when human joins
- **Canned responses** — for common issues, skip LLM and use pre-written responses
- **Rate limiting** — cap maximum call duration and number of turns

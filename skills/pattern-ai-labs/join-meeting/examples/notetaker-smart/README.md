# Smart Note-Taker with LLM Summarization

Joins a meeting, records the transcript, then uses an LLM to generate a structured summary with key decisions, action items, and follow-ups.

## What It Does

1. Creates a call in **audio mode** (voice-only, cheapest)
2. Collects `transcript.final` events in real-time via WebSocket
3. When the meeting ends, fetches the full transcript from the API
4. Sends the transcript to an LLM with a structured prompt
5. Saves a summary + full transcript to a markdown file

## LLM Configuration

The script supports any LLM provider. Uncomment one option in `summarize_with_llm()` (Python) or `summarizeWithLLM()` (Node.js):

| Option | Provider | Model | Install |
|--------|----------|-------|---------|
| A | Anthropic | Claude Sonnet | `pip install anthropic` / `npm install @anthropic-ai/sdk` |
| B | OpenAI | GPT-4o | `pip install openai` / `npm install openai` |
| C | Google | Gemini 2.0 Flash | `pip install google-generativeai` / `npm install @google/generative-ai` |
| D | Any OpenAI-compatible | Ollama, Together, Groq | `pip install openai` / `npm install openai` |

If no LLM is configured, the script saves the raw transcript without a summary.

## Setup

### Python

```bash
pip install requests websockets
# Plus your chosen LLM SDK (e.g., pip install anthropic)

export AGENTCALL_API_KEY="ak_ac_your_key"
export ANTHROPIC_API_KEY="sk-ant-..."   # or OPENAI_API_KEY, GOOGLE_API_KEY

python notetaker.py "https://meet.google.com/abc-def-ghi"
```

### Node.js

```bash
npm install ws
# Plus your chosen LLM SDK (e.g., npm install @anthropic-ai/sdk)

export AGENTCALL_API_KEY="ak_ac_your_key"
export ANTHROPIC_API_KEY="sk-ant-..."

node notetaker.js "https://meet.google.com/abc-def-ghi"
```

### Options

```bash
# Custom bot name
python notetaker.py "https://meet.google.com/abc" --name "Scribe"

# Custom output file
python notetaker.py "https://meet.google.com/abc" --output weekly-standup.md
```

## Output

```markdown
# Meeting Summary — 2026-04-03 14:30

**Call ID:** call-550e8400...
**Duration:** 32 minutes
**Participants:** Alice, Bob, Carol
**End reason:** left

---

## Summary
The team discussed Q3 roadmap priorities, focusing on mobile-first strategy
and API timeline. Alice proposed launching the mobile app by end of Q3,
Bob raised concerns about backend capacity.

## Key Decisions
- Mobile app launch will be prioritized for Q3
- API v2 migration deferred to Q4

## Action Items
- [ ] Alice: Draft mobile launch timeline by Friday
- [ ] Bob: Run load tests on staging by next Tuesday
- [ ] Carol: Schedule design review for mobile mockups

## Follow-Up Needed
- Backend capacity planning for mobile launch — Bob to investigate

---

## Full Transcript

[14:30:12] **Alice**: Let's discuss the Q3 roadmap
[14:30:45] **Bob**: I think we should focus on mobile first
...
```

## The Summarization Prompt

The built-in prompt asks the LLM to produce:
- **Summary** — 2-4 sentence overview
- **Key Decisions** — what was agreed upon
- **Action Items** — who does what, with deadlines if mentioned
- **Follow-Up Needed** — unresolved questions

You can customize the `SUMMARY_PROMPT` variable to change the output format.

## Billing

Only two components are charged:
- **Meeting bot** — per minute of call
- **Speech-to-text** — per minute of call

The LLM call is billed by your LLM provider, not AgentCall.

## Customization Ideas

- **Slack/Email integration** — post the summary to a Slack channel or email it to attendees after the meeting
- **Database storage** — save transcripts and summaries to a database for search and retrieval
- **Speaker analytics** — calculate talk time per person, interruption counts, speaking pace
- **Language translation** — detect the meeting language and translate the summary
- **Sentiment analysis** — track sentiment per speaker throughout the meeting
- **CRM integration** — for sales calls, auto-log notes and action items to Salesforce/HubSpot
- **Project management** — push action items directly to Linear, Jira, Notion, or Asana
- **Multi-meeting tracking** — compare action items across meetings to track completion
- **Custom templates** — different summary formats for standups, 1:1s, client calls, etc.

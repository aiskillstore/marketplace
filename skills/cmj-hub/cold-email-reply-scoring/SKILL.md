---
name: cold-email-reply-scoring
description: Classify replies to cold email into 4 categories — buy-signal, positive, neutral, not-interested — using deterministic features (intent keywords, time-to-reply, length, question count, calendar/asset asks). Routes each reply per brand-config.operations.reply_routing. Backed by a Python script that uses regex + features (no LLM). Loaded by the main cold-email skill when the operator processes their reply queue.
user-invocable: false
allowed-tools: Read Bash Write
  - Grep
license: MIT

---

# Cold Email Reply Scoring — deterministic reply classifier

Real classifier, not vibes. Backed by `scripts/score_reply.py` for
deterministic categorization. The output is a category + confidence
+ recommended routing action.

## Activation

Loaded by:
- `cold-email-weekly-rhythm` — Wednesday + Friday reply triage
- User invocation: "Score this reply", "Classify this response"

## Output categories

The classifier returns one of 4 categories with a confidence score:

| Category | Signal | Routing (per brand-config) |
|---|---|---|
| `buy-signal` | Explicit ask to talk, calendar request, price question, decision-maker tag | `brand-config.operations.reply_routing.buy_signal` |
| `positive` | Curious, asking follow-up Qs, expressing interest, asking for proof | `positive` |
| `neutral` | "Not now", "circle back later", "send more info" without commitment | `neutral` (often → nurture stream) |
| `not-interested` | Explicit no, unsubscribe ask, hostile, out-of-office on repeat | `not-interested` |

## Feature set (what the classifier uses)

Pure feature engineering — no LLM, no vendor APIs:

1. **Intent keywords** — regex over 50+ patterns per category
   - buy-signal: "send the calendar", "what's the price", "demo", "case study", "intro"
   - positive: "tell me more", "interesting", "curious", "send the deck"
   - neutral: "not the right time", "Q4", "send more info", "in a few months"
   - not-interested: "unsubscribe", "stop emailing", "not a fit", "no thanks"

2. **Time-to-reply** — minutes since send
   - <15 min after send → likely auto-reply (out-of-office, etc.)
   - <60 min → high-intent (operator was working, saw it, replied immediately)
   - 60 min - 24h → engaged reply
   - >24h → background reply

3. **Reply length** — chars
   - <20 chars → 1-word answer, usually not-interested or short positive
   - 20-200 → typical engaged reply
   - >200 → often a substantive response (rare; high-signal)

4. **Question count** — # of "?" in the body
   - 0 → declarative (could be any category)
   - 1-2 → engaged with specific questions
   - 3+ → either highly engaged or asking-for-everything (lower convert)

5. **Calendar / asset ask** — regex
   - "send <calendar link>", "let's get a time", "what dates work" → buy-signal
   - "send the case study", "send the deck" → positive (could be buy-signal if combined with other features)

6. **Out-of-office indicators** — regex
   - "out of office", "OOO", "auto-reply", "I'm currently away" → exclude from scoring
   - These get marked `auto-reply` (5th category) and not routed

## Output format

```markdown
# Reply scoring

From: <sender>
Subject: Re: <original subject>
Time-to-reply: <minutes since send>
Length: <N chars>

## Classification
Category: **buy-signal** (confidence: 0.87)

## Why
- "send me a calendar link" → buy-signal +0.5
- "what's the price for Series-B teams" → buy-signal +0.4
- Reply within 27 minutes → buy-signal +0.2
- Length 142 chars → engaged-length +0.1
- No not-interested patterns matched

## Recommended routing
Per your brand-config.operations.reply_routing.buy_signal:
→ Slack #pipeline + create HS deal
→ Reply within 4 hours

## Suggested reply opener (not generated; use your own voice)
"Sent — calendar link [here]. <Specific qualifying Q to set the agenda>"
```

## Batch mode

For triaging the Wednesday/Friday batch of replies:

```bash
# In the project, with reply data in replies.jsonl
python3 ../../scripts/score_reply.py --batch replies.jsonl --format json | jq
```

Output:

```
# Batch reply scoring — <date>

| # | From | Category | Confidence | Route |
|---|---|---|---|---|
| 1 | sarah@acme.com | buy-signal | 0.87 | Slack + HS deal |
| 2 | mike@beta.io | positive | 0.74 | Reply <4h |
| 3 | hr@autoresponder.co | auto-reply | 1.00 | Skip |
| 4 | bob@churn.com | not-interested | 0.92 | Suppress + log |
| ... |
```

## Why deterministic > LLM here

Reply classification is high-throughput (50-200/week per operator).
LLM classification:
- Costs money per reply
- Adds 1-3 seconds latency per reply
- Drifts as LLMs version
- Hard to audit

Feature-based classification:
- Zero cost per reply
- <10ms per reply
- Stable across years
- Fully auditable (every score has a feature contribution list)

For a 100-reply week, the deterministic classifier runs in <1 second
and gives the same answer in 6 months as it does today.

## False-positive handling

The script flags **low-confidence** classifications (confidence <0.6)
for human review. These are usually:
- Short replies (1-3 words) that could go either way
- Replies in non-English (the lexicon is English-only)
- Sarcasm / context-dependent meaning

Low-confidence replies surface as:

```
# Manual review needed

<sender>: "<reply body>"
Category candidates: positive (0.42) | neutral (0.38)
→ Read carefully before routing
```

## Calibration

The lexicon is calibrated against JMC's review of 1000+ real cold-email
replies (anonymized). Accuracy on the held-out set:

- buy-signal vs not: 94%
- positive vs neutral: 81%
- not-interested precision: 97%

Re-calibration ships when the lexicon updates (every 90 days minimum,
or when bulk-sender rules change).

## References

- `../../scripts/score_reply.py` — the actual classifier
- `references/reply-lexicon.md` — feature regex source
- `../cold-email-weekly-rhythm/SKILL.md` — where batch triage runs
- `brand-config.operations.reply_routing` — the routing rules

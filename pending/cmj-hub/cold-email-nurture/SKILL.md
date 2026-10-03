---
name: cold-email-nurture
description: Design a 5-email nurture stream from a Pain Signal Profile + EVP. Each email has a subject, preheader, opener, body beats, CTA, cadence rationale, behavioral principle, and one route-to-sales trigger. Loaded by the main cold-email skill when the user asks to nurture, re-engage, or design a stream. Based on the JMC Lifecycle Nurture framework.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# Cold Email Nurture — 5-Email Stream Designer

Loaded by `cold-email` when the user wants to nurture (warm leads who
didn't reply, re-engage dormant prospects, re-activate churned
clients, post-content-download follow-ups).

## Activation triggers

- "Design a nurture sequence"
- "5-email nurture"
- "Re-engagement sequence"
- "Re-activate churned"
- "Post-download follow-up"
- "Lifecycle nurture"

## Workflow

### 1. Capture inputs

Required:

| Input | Source |
|---|---|
| `pain_signal_profile` | The PSP for this audience |
| `evp` | One-line value prop |
| `nurture_context` | Why these prospects are getting this stream (no reply / churned / downloaded / post-event) |
| `expected_cadence_days` | Default: 3 / 5 / 10 / 17 / 28 |

### 2. Generate the 5-email stream

Each email follows this shape:

```
Email N — <day> — <behavioral principle in 2 words>

Subject: <≤7 words>
Preheader: <≤90 chars>

Opener: <1 sentence — references the PSP, no "just checking in">
Body beats:
  - <Beat 1: insight / case / question>
  - <Beat 2: bridge to EVP>
CTA: <Binary, time-bound>
Cadence rationale: <Why this day>
Behavioral principle: <Reciprocity / commitment / social proof / loss aversion / curiosity>
Route-to-sales trigger: <Behavior that flags this lead is hot — open + reply + click + reply-to-CTA>
```

### 3. The default 5-email shape (no-reply nurture)

| # | Day | Principle | Job |
|---|---|---|---|
| 1 | 3 | Insight | Drop ONE specific insight tied to the PSP. No ask. |
| 2 | 8 | Case study | One peer company hit <outcome> in <timeframe>. Binary ask. |
| 3 | 13 | Reframe | Different angle on the same pain (cost-of-inaction / opportunity-cost). |
| 4 | 23 | Soft close | "Should I keep these coming?" — explicit permission ask. |
| 5 | 40 | Hard close | "I'll stop reaching out unless you want a different lens. Reply 'keep' to stay on." |

For re-engagement / churned / post-download contexts, shift the
opening principle but keep the 5-touch shape:

- **Re-engagement**: T1 = "What changed?" (curiosity) → T5 = "Last
  ping — should I close the loop?"
- **Churned**: T1 = "What broke?" (reciprocity by listening) → T5 = "If
  we shipped <X>, would you re-evaluate?"
- **Post-download**: T1 = "Most-asked Q after <download>" (insight) →
  T5 = "Want a walkthrough or close the loop?"

### 4. Route-to-sales trigger per email

Each email defines ONE behavior that signals the lead is hot and
should route to sales:

- T1: replied with any substance
- T2: clicked the case study
- T3: opened + clicked (engaged without replying)
- T4: replied to permission ask = consent + signal
- T5: replied 'keep' OR explicit interest

The trigger fires a webhook / Slack notification / SDR queue — the
mechanics live downstream of this skill. This skill just documents
the triggers.

### 5. Output format

Markdown by default. JSON if user requests it, shaped as:

```json
{
  "audience": "PSP description",
  "evp": "...",
  "context": "no-reply | re-engagement | churned | post-download",
  "emails": [
    {
      "n": 1,
      "day": 3,
      "subject": "...",
      "preheader": "...",
      "opener": "...",
      "bodyBeats": ["...", "..."],
      "cta": "...",
      "cadenceRationale": "...",
      "behavioralPrinciple": "...",
      "routeToSalesTrigger": "..."
    }
  ]
}
```

## References

- `../../cold-email/references/jmc-framework.md` — core framework
- The **Lifecycle Nurture** course in The Compounding Engine covers
  segmentation, lifecycle stages, and trigger automation:

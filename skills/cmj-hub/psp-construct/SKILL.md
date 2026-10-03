---
name: psp-construct
description: Step-by-step construction of a Pain Signal Profile for a specific ICP segment. Walks operator through the 5 components (signal, pain, timing, role, vocabulary), validates each, and produces a structured PSP doc. Loaded by the main psp skill when the user wants to build a PSP from scratch.
user-invocable: false
allowed-tools: Read Write Grep
  - WebFetch
license: MIT

---

# PSP Construct — sub-skill

Loaded by `psp` when the user wants to build a complete PSP for a
specific ICP segment.

## Activation

The main `psp` skill routes here on:
- "Build a PSP for..."
- "Construct a Pain Signal Profile for..."
- "Walk me through a PSP for..."

## Workflow

### Step 1 — Lock the ICP segment

Ask the user to be specific. Push back on broad ICPs.

> "B2B SaaS" is too broad. Try one of these shapes:
>
> - "Series-B SaaS, $20-50M ARR, with a PLG motion"
> - "DevTools companies with >50 engineers and an OSS community"
> - "Bootstrapped agencies, 5-15 employees, productized service"
>
> Which segment?

### Step 2 — Hunt signals

For the segment, surface 5-10 candidate signals. Patterns:

- **Hiring signals**: Specific role open ≤30 days
- **Funding signals**: Round announced ≤30 days
- **Product signals**: New tier / launch / pricing change ≤45 days
- **Leadership signals**: New CMO / CRO / CFO / Head-of-X ≤60 days
- **Content signals**: Recent podcast / panel / public talk on the topic
- **Pivot signals**: Website hero / positioning change ≤14 days

If WebFetch is available, demo-pull recent LinkedIn job posts or
recent funding news for one example company in the segment.

### Step 3 — Map signal → pain for top 3

For each of the top 3 signals, ask: "If this happened, what is the
operator at that company **feeling** at 11am on Tuesday?"

Validate each pain:
- Specific operational moment (not abstract)
- Phrased as what they feel, not what you sell
- Uses their language (not category jargon)

### Step 4 — Anchor timing

For each pain, identify the 90-day trigger:
- New exec → 90-day plan in motion
- Budget cycle → planning/fiscal-new-year window
- Obvious failure → quarter miss, churn spike, launch flop

If no trigger, the PSP isn't time-anchored — push back.

### Step 5 — Identify felt-pain role

Who in the org **feels** the pain at 11am Tuesday?

Note: this is often a layer below the buying authority. The
demand-gen lead feels pipeline-gap pain; the CMO authorizes the spend.
Outreach hits the felt-pain role.

### Step 6 — Mine vocabulary

Read 5-10 sources of recipient-written content:
- Their job posts (often most revealing)
- Their team's LinkedIn comments
- Their conference talks
- Their AMA / podcast appearances
- Their public sales/marketing internal-system tweets

Extract 8-12 phrases they actually use about this pain.

### Step 7 — Output

```markdown
# PSP — <ICP segment>

**ICP precision check:** <one sentence on why this segment is specific enough>

## Signal
<Top signal — verifiable, recent, hunting-ready>

## Pain
<What the signal implies at 11am Tuesday — in their language>

## Timing
**Trigger:** <new-exec / budget-cycle / obvious-failure>
**Why now:** <one sentence>

## Role (felt-pain holder)
<Specific role title; not the buying authority>

## Vocabulary
<8-12 phrases they actually use>
- "<phrase 1>"
- "<phrase 2>"
- ...

## Top 5 signals to hunt operationally
1. <Signal source + cadence>
2. <Signal source + cadence>
3. <Signal source + cadence>
4. <Signal source + cadence>
5. <Signal source + cadence>

## Plugs into
- claude-cold-email — first-line opener uses Signal verbatim
- claude-evp — EVP must speak to Pain in their Vocabulary
- Outbound program 30-point audit — PSP is the messaging anchor
```

### Step 8 — Stress test

Ask the user: "Which of these are weakest? I can re-pull or refine
any block." Most common weak spots:

- **Pain too abstract**: rewrite using their vocabulary, force the
  11am-Tuesday moment
- **Signal too stale**: shorten the recency window
- **Vocabulary borrowed from category**: pull more sources of their
  actual writing

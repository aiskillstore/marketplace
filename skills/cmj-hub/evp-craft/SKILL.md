---
name: evp-craft
description: Generate 3 EVP variants for a single Schwartz awareness tier. Each variant follows the 22-word shape and explores a different emphasis (outcome / tradeoff / ICP). Loaded by the main evp skill when the user wants to craft EVPs for a specific tier.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# EVP Craft — sub-skill

Generates 3 EVP variants for a specific awareness tier.

## Activation

Loaded by `evp` on:
- "Write an EVP for <tier>"
- "EVP for solution-aware prospects"
- "Tier 3 EVP"

## Workflow

### 1. Lock the awareness tier

Ask the user which Schwartz tier (1-5). If they don't know, walk them
through the 5-tier table from `../../evp/SKILL.md` and ask: "Which
describes your audience right now?"

Most B2B buyers are in Tiers 2-4. If the user says "Tier 5," push
back — that's product-team thinking, not buyer-where-they-are
thinking.

### 2. Capture the inputs

Required:
- `icp` — specific ICP segment
- `psp_pain` — pain in the prospect's vocabulary (from claude-psp)
- `outcome` — specific result you deliver
- `tradeoff` — obvious tradeoff you spare them
- `proof` (optional) — case study / metric backing it

If PSP is missing, suggest the user run `claude-psp` first. EVPs
without a PSP are guesses.

### 3. Generate 3 variants

Each variant uses the shape but with different emphasis:

**Variant A — outcome-led**

> "For <ICP>, in <pain>, we're the <one team> that does <SPECIFIC
> OUTCOME> without <tradeoff>."

The outcome carries the line. Use when the outcome is differentiated
and concrete (e.g., "ships 14 qualified meetings in 30 days").

**Variant B — tradeoff-led**

> "For <ICP>, in <pain>, we're the team that hits <outcome> WITHOUT
> <SPECIFIC TRADEOFF>."

The tradeoff carries the line. Use when the tradeoff is the
elephant-in-the-room reason the audience hesitates (e.g., "without
hiring 2 more SDRs" or "without sacrificing self-serve").

**Variant C — ICP-led**

> "<SPECIFIC ICP> in <pain> use us when they want <outcome> without
> <tradeoff>."

The ICP carries the line. Use when the audience is hyper-niche and
you want immediate exclusion-by-segment (signals fit fast).

### 4. Validate each variant

Run the self-check:

| Check | Pass criterion |
|---|---|
| Word count | ≤22 |
| Outcome specificity | A concrete noun + metric, not a verb like "improve" |
| Tradeoff specificity | A concrete thing they'd otherwise have to give up |
| ICP named | Segment is specific enough to exclude wrong-fit |
| Pain vocabulary | Uses their words from the PSP, not category jargon |
| Tier-appropriate | Matches the awareness tier (no Tier-5 line for a Tier-2 audience) |

### 5. Output

```markdown
# EVP — <ICP> · Tier <N>: <tier name>

**Pain anchor:** <PSP pain in their language>

## Variant A — outcome-led
"<22-word line>"

## Variant B — tradeoff-led
"<22-word line>"

## Variant C — ICP-led
"<22-word line>"

## Recommended primary
<A / B / C> — <one-sentence rationale>

## Where this fits
- Cold email line 3 (works on Tier 2-4 audiences)
- Hero copy (Tier <N> only — calibrate per page)
- Pricing-page tagline (Tier 4)
- Sales call opener (calibrate to where prospect is)

## Proof to back it
<Case study / metric / social proof aligned to this tier>
```

### 6. Surgical critique mode

If user pastes an existing EVP for critique, return:

```
Original: "<their EVP>"
Word count: <N>
Tier-fit: <which tier this actually lands on>

Issues:
  - <issue 1>
  - <issue 2>

Rewrite (same voice):
"<rewritten>"
Rationale: <one sentence>
```

## References

- `../../evp/SKILL.md` — the framework
- The **EVP** course in The Compounding Engine:

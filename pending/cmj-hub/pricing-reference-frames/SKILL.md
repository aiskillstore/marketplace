---
name: pricing-reference-frames
description: Design the reference-frame stack for pricing copy. Picks the strongest plausible anchor (inertia / opportunity cost / replacement cost / competitor) for the operator's PSP segment, generates the anchor copy block, and applies Prospect Theory loss-aversion patterns so the page reads "worth it or refund" rather than "save 40%." Loaded by the main pricing skill when the operator asks about anchoring, framing, or rewriting pricing copy.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# Pricing Reference Frames — sub-skill

The anchor design engine. Most pricing pages anchor on competitor
cost — the weakest frame in the stack. This sub-skill picks the
strongest plausible frame and writes the copy block that puts it
on the page.

## Activation

Routed here when operator says:

- "How do I anchor my pricing?"
- "What should my pricing page say above the tiers?"
- "Rewrite my pricing copy"
- "What's my reference frame?"
- "Apply loss aversion to my pricing"

## The reference-frame stack

```
1. Inertia / status quo     ← strongest, use this first
2. Opportunity cost
3. Replacement cost
4. Competitor cost           ← weakest, default of most pages
```

### Frame 1 — Inertia / status quo

What is the buyer doing TODAY to solve this problem? That's the
real reference frame. Quantify the cost of doing nothing.

Inertia anchors look like:

> "Right now, you're solving this with a contractor + spreadsheet
> + 3 Slack channels — that's ~12 hours/week of founder time at
> $200/hr loaded = $124,800/year."

Or for SaaS:

> "Your current stack: $300/mo HubSpot CRM + $200/mo Pipedrive
> for sales + 6 hours/week of manual data sync = $14,000/year + 
> 312 founder-hours/year. Our $499/mo replaces all three."

### Frame 2 — Opportunity cost

What does the buyer lose by NOT solving this? Time, market position,
pipeline.

Opportunity-cost anchors look like:

> "Every week you delay shipping pricing changes = 1 fewer customer
> onboarded at the new ACV = $30,000/year of compounding ARR you
> never get back."

### Frame 3 — Replacement cost

What does it cost to build/staff the alternative internally?

Replacement-cost anchors look like:

> "If you built this internally: 2 engineers × 6 months × $250K
> loaded = $250K to ship + $80K/year to maintain. Or you can use
> ours at $1,200/year."

### Frame 4 — Competitor cost (LAST RESORT)

Only if there's no plausible inertia / opportunity / replacement
frame, and the competitor is well-known and obviously similar.
Even then — anchor by VALUE, not price.

Competitor-frame example (acceptable):

> "Like X but with built-in PSP segmentation and quarterly review
> baked in."

Competitor-frame example (banned):

> "$X cheaper than Competitor Y." (See `pricing-banned-patterns.md`.)

## Workflow

### 1. Gather PSP + current state

From `brand-config.json`:

- `customer.psps[]` — at least one PSP
- `pricing.currentTiers` — current pricing
- Optional: `customer.competitors[]`

If multiple PSPs, ask: "Which PSP should we anchor for? Different
PSPs may need different reference frames on different page sections."

### 2. Discover the inertia anchor (always start here)

Ask the operator:

1. "Without your product, what does {PSP} do today to solve this?
   Be specific — name the tools, the headcount, the time spent."
2. "What's their loaded-cost on that today?" (Time × $/hr + tool costs)
3. "Quantify the time/quality/risk cost of staying with the status quo."

If the operator can't quantify inertia, this is a customer-development
gap — flag it.

### 3. Build the opportunity-cost anchor

Ask:

4. "What's at stake if {PSP} delays solving this for another quarter?"
5. "What does NOT solving this cost in pipeline / market position?"

If the answer is "nothing material," the buyer doesn't actually need
to buy now. Flag this — it suggests the messaging needs urgency
work, not pricing work.

### 4. Pick the dominant frame

Pick the strongest available frame for THIS PSP:

| Available frame | Use as |
|---|---|
| Inertia ≥ replacement ≥ opportunity | Above-the-fold anchor block |
| Opportunity ≥ inertia ≥ replacement | Headline statement + chart |
| Replacement (engineers, contractors) | Calculator block + ROI |
| Only competitor | Soften to "category-leading" language; do NOT lead with $X cheaper |

### 5. Apply Prospect Theory

Once the frame is chosen, layer loss-aversion language:

| Instead of (gain frame) | Use (loss frame) |
|---|---|
| "Save 40% vs. internal build" | "Stop losing 312 founder-hours/year" |
| "Get to outcome X faster" | "Stop letting opportunity-cost X compound" |
| "Money-back guarantee if not satisfied" | "If we don't ship outcome X by date Y, you pay only Z" |
| "Premium support included" | "Never debug a critical pricing error alone" |

### 6. Generate the anchor block

Output a complete above-the-tier-cards copy block:

```
Headline (1-2 lines, ≤14 words):
{Anchor on chosen frame, loss-coded if possible}

Subhead (1-2 lines, ≤22 words):
{Quantify the frame with a specific number}

Mechanism (3-line bullet list, ≤8 words each):
- {How we replace / reduce / eliminate the inertia cost}
- {What we lock-in / de-risk}
- {What outcome ships}

Guarantee (1 sentence, ≤30 words):
{Outcome-tied guarantee with bounded liability — never open-ended}
```

### 7. Self-check

- [ ] Frame chosen is highest in the stack that's plausibly true
- [ ] Anchor is quantified (specific number, not vague)
- [ ] Loss-coded language above gain-coded language
- [ ] Guarantee is outcome-tied, not satisfaction-tied
- [ ] No banned patterns (cost-plus reasoning, "we're cheaper than X")

## Output format

```
Reference-Frame Recommendation — {PSP}
─────────────────────────────────────────────────────────────────

CHOSEN FRAME: {frame name + rationale}

ANCHOR COPY BLOCK:
[headline]
[subhead]
[mechanism bullets]
[guarantee]

REJECTED FRAMES:
- {frame}: {why not for this PSP}

LOSS-AVERSION APPLICATION:
- Replaced gain-coded line {X} with loss-coded line {Y}
- Replaced open-ended guarantee with outcome-tied
```

## References

- `../../pricing/references/pricing-framework.md` — full reference-frame stack
- `../../pricing/references/pricing-banned-patterns.md` — what to avoid
- `../pricing-contrast-set/SKILL.md` — next: design the tier cards under the anchor

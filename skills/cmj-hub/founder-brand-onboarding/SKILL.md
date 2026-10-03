---
name: founder-brand-onboarding
description: First-run interactive setup for the founder-brand skill pack. Walks the operator through brand-config.json (audience, 4-pillar topic pools, cadence, drive-to URLs) and SOUL.md (voice fingerprints, phrases-I-refuse, stories reservoir, won't-write boundaries) in ~15 minutes. This is THE most important file in the pack — the whole point is sounding like the operator, not ChatGPT.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# Founder-Brand Onboarding — first-run setup

The most important setup in this pack. The point of founder-brand
content is that it sounds like YOU. Without SOUL.md, the skill
produces LinkedIn-influencer-voice slop.

## Activation

Loaded automatically by `founder-brand` on missing brand-config.json
or SOUL.md.

Also user-invocable: "Set up founder-brand onboarding", "Configure voice".

## Workflow

### Step 1 — Voice in 3 sentences

```
Describe how you actually write — in 3 sentences. Not "professional yet
approachable." Specific.

Examples of useful answers:
  "I write declarative, with one claim per sentence."
  "I lead with the receipt before the explanation."
  "I don't soften with hedges — I either claim it or cut it."

Don't generalize. Tell me what's true about YOUR writing.
```

Save to `SOUL.md` (top section).

### Step 2 — Phrases I use a lot (5-10)

```
Pull up your last 10 emails / posts / messages. What phrases show up
repeatedly? These are your voice fingerprints.

Examples (not yours — yours will differ):
  "The lever is..."
  "Specifically:"
  "Here's the receipt:"
  "What actually moved the number..."

5-10 phrases. These show up naturally in every output.
```

Save to `SOUL.md`.

### Step 3 — Phrases I refuse (5-10)

```
What phrases would you NEVER write? Be specific. These get banned in
addition to the framework's banned-patterns list.

Common refuses:
  "Synergy"
  "Leverage" (as verb)
  "Circle back"
  "Delve into"
  "Game-changing"

YOUR refuses might include things others use freely. Capture them.
```

Save to `SOUL.md`.

### Step 4 — Voice settings

```
Pick your settings:

Formality:        Casual / Professional / Direct
Sentence length:  Short (≤15w) / Medium / Mixed
Confidence:       High (outright) / Hedged / Calibrated
Humor:            Dry / Never / Often
Profanity:        Never / Sparingly / Often
First-person:     I / We / Both
Emoji:            Never / Sparingly (≤1/post) / Often
```

Save to `SOUL.md`.

### Step 5 — Stories reservoir (3-5)

```
Give me 3-5 specific receipts you can cite. Anonymized but specific.
These become the case-study reservoir every Proof-pillar post pulls from.

Examples:
  "The Series-B SaaS that hit 14 SQLs in 30 days from a PSP rewrite"
  "The bootstrapped agency that went 2% → 11% reply rate"
  "The DevTools company that closed $80k ACV in 90 days after EVP retier"

Each story needs:
- A specific (anonymized) client/company descriptor
- A specific number / metric / outcome
- A specific lever that drove it
```

Save to `SOUL.md`.

### Step 6 — Won't-write boundaries

```
Hard nos. What topics will you NOT touch?

Common:
  Political topics
  Personal life specifics
  Hot-takes-for-engagement
  Industries you don't actually serve

Capture yours.
```

Save to `SOUL.md`.

### Step 7 — Audience + 4-pillar topic pools

```
Now the brand-config side.

AUDIENCE:
1. Primary ICP (1 sentence)
2. What they already know
3. What they don't know yet

4-PILLAR TOPIC POOLS (3+ topics each):

PILLAR pool — big claims / POVs / contrarian takes
  • Topic 1
  • Topic 2
  • Topic 3

PROOF pool — specific receipts / case studies / metrics
  • <draws from your stories reservoir>

PROCESS pool — how you do the work / SOPs / frameworks
  • <Process you teach>
  • <Framework you use>

PERSON pool — human stories / stakes / why you care
  • <Your story 1>
  • <Your story 2>
```

Save to `brand-config.audience` + `brand-config.pillars`.

### Step 8 — Cadence + business outcomes

```
CADENCE:
  Posts per week (default 4 — 1 per pillar)
  Rotation order (default: pillar → proof → process → person)
  Default platform (linkedin / x / both)
  Auto-critique before post (yes/no)

BUSINESS OUTCOMES:
  Drive-to URL (the primary CTA destination)
  Lead magnet URL (the soft offer for skeptical readers)
  Call URL (booking link for hot replies)
```

Save to `brand-config.cadence` + `brand-config.business_outcomes`.

### Step 9 — Write the files + smoke test

```
✓ brand-config.json — audience + 4 pillars (×3 topics each) + cadence + outcomes
✓ SOUL.md — voice + 8 phrases used + 7 refused + 5 stories

Try a smoke test:
> Generate a Proof pillar post about <one of your stories>

The output will:
- Use your phrases-I-use list naturally
- Refuse your phrases-I-refuse list
- Cite the actual story (not invent one)
- Match your voice settings
- Be ≤200 words, 1-sentence opener, scannable body, no engagement bait
```

### Step 10 — Refresh cadence

```
Voice evolves. Re-run onboarding when:
- You catch yourself using phrases not in your fingerprint list (add them)
- The audience shifts
- Quarterly minimum

Re-run: `/founder-brand onboarding refresh`
```

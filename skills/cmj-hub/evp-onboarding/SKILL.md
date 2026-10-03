---
name: evp-onboarding
description: First-run interactive setup for the EVP skill pack. Walks the operator through brand-config.json (awareness tier, outcomes-I-will-claim, proofs reservoir, competitors) and SOUL.md (tier-by-tier voice, won't-claim list, boundaries) in ~10 minutes. Refuses to let the operator skip — generic EVP is worse than no EVP. Loaded automatically when brand-config.json or SOUL.md is missing.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# EVP Onboarding — first-run setup

10 minutes of setup that makes every downstream EVP differentiated
instead of generic.

## Activation

Loaded automatically by `evp` orchestrator when `brand-config.json`
or `SOUL.md` is missing.

Also user-invocable: "Set up EVP brand config", "EVP onboarding".

## Workflow

### Step 1 — ICP + PSP carry-forward

```
Quick check — do you already have a PSP?

If yes (claude-psp is installed and PSP doc exists): I'll pull ICP + pain + vocabulary from there.
If no: Install cmj-hub/claude-psp first. EVP without a PSP is a guess.
```

### Step 2 — Primary outreach tier

```
Where is YOUR buyer on the Schwartz tier ladder when they meet you?

Most B2B buyers live in Tiers 2-4. Pick the most common one for your outreach:

  Tier 1 (unaware)         — you have to reveal the pain first
  Tier 2 (problem-aware)   — they know the pain, no solutions evaluated
  Tier 3 (solution-aware)  — they're comparing categories (in-house / agency / tool)
  Tier 4 (product-aware)   — comparing specific vendors
  Tier 5 (most aware)      — ready to buy

If you don't know, default to Tier 3 — most outbound campaigns target
that tier.
```

Save to `brand-config.primary_outreach_tier`.

### Step 3 — Outcomes-I-will-claim list

```
What specific outcomes are you willing to claim in writing?

Each outcome needs:
1. A specific noun (not a verb — "14 SQLs", not "more pipeline")
2. A specific timeframe (in 30 days, per month, per quarter)
3. A proof point you can back it with

Examples of GOOD outcomes:
  "14+ SQLs per month"
  "Targeted-outbound CPM under $700"
  "First positive reply within 7 days"

Examples of BAD outcomes (refuse to claim):
  "Better demand-gen"
  "Improved efficiency"
  "Best-in-class outreach"

Give me 3-5 outcomes you're willing to claim. These constrain every
downstream EVP variant.
```

Save to `SOUL.md` (outcomes-I-will-claim list) + `brand-config.evp_drafts.tier_3.outcome`.

### Step 4 — Tradeoffs you name

```
For each outcome, what's the obvious tradeoff you spare them from?

The EVP shape is "<outcome> without <tradeoff>". The tradeoff carries
the line — name something they'd otherwise have to give up.

Examples:
  "without hiring 2 more SDRs"
  "without breaking the PLG self-serve motion"
  "without paying agency retainer rates"
```

Save to `brand-config.evp_drafts.tier_3.tradeoff` + `SOUL.md`.

### Step 5 — Proofs reservoir

```
Give me 3-5 concrete proofs you can cite. Each is anonymized but
specific.

Examples:
  "Series-B SaaS hit 14 SQLs in 30 days from a PSP rewrite — case study at /case-studies/X"
  "Bootstrapped agency went 2% → 11% reply rate by killing demographic targeting"

These become the proof reservoir — EVP variants pull from here, not
fabricated case studies.
```

Save to `SOUL.md`.

### Step 6 — Competitors (for Tier 4 EVPs)

```
For Tier 4 EVPs, you need to name competitors and your delta on a
specific axis.

Top 2-3 competitors + the axis you beat them on:
  1. Generic outbound agency — CPM efficiency
  2. AI SDR vendor — reply quality vs volume
  3. In-house SDR build — time-to-payback
```

Save to `brand-config.competitors`.

### Step 7 — Voice (SOUL.md)

```
Per-tier voice settings:

Tier 2 (problem-aware) — tone: ?
Tier 3 (solution-aware) — tone: ?
Tier 4 (product-aware) — tone: ?

Won't-write list:
  • <e.g. industry guarantees you don't actually back>
  • <e.g. competitor names you won't reference by full brand>
```

Save to `SOUL.md`.

### Step 8 — Write the files + smoke test

Write `brand-config.json` + `SOUL.md` at project root. Show:

```
✓ brand-config.json — Tier 3 primary + 3 outcomes + 3 competitors
✓ SOUL.md — outcomes-will-claim list + 4 proofs + tier voice

Try a smoke test:
> Generate a Tier 3 EVP for my ICP

The output will use:
- Your outcomes-will-claim list (refuses outside it)
- Your tradeoffs
- Proofs from your reservoir
```

## References

- `../../brand-config.example.json`
- `../../SOUL.md`
- `../../AGENTS.md`
- Sister skills: `evp-craft`, `evp-brief`

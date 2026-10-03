---
name: evp-brief
description: Build a structured 3-tier EVP brief — Tier 2 (problem-aware), Tier 3 (solution-aware), Tier 4 (product-aware) — side-by-side with audience, pain, EVP variants, and proof per tier. Becomes the single source of truth your hero, ads, cold email, and pricing-page pull from. Loaded by the main evp skill when the user wants a full brief.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# EVP Brief — sub-skill

Produces a structured 3-tier EVP brief covering the three tiers where
most B2B buyers live: Tier 2 (problem-aware), Tier 3 (solution-aware),
Tier 4 (product-aware).

## Activation

Loaded by `evp` on:
- "Build an EVP brief"
- "3-tier brief"
- "EVP across awareness levels"

## Workflow

### 1. Confirm the ICP scope

The brief is per-ICP. If the user has multiple ICPs, ask: "Which ICP
are we building this brief for? (Run again per segment.)"

### 2. Capture inputs once

| Input | Source |
|---|---|
| `icp` | Specific ICP segment |
| `psp` | PSP doc from claude-psp (or build inline) |
| `outcome` | The specific result you deliver |
| `tradeoff` | The obvious tradeoff you spare them |
| `competitors` (optional) | Top 2-3 competitors for Tier 4 framing |
| `proof_per_tier` (optional) | Case study / metric per tier |

### 3. Generate the brief

For each of Tier 2, Tier 3, Tier 4:

- Audience description (what they know, what they don't)
- Tier-appropriate pain framing
- 1 primary EVP (best variant) + 1 alternate
- Proof aligned to that tier (different proofs land at different tiers)
- Where to deploy this EVP (which surfaces)

### 4. Output

```markdown
# EVP Brief — <ICP>

**PSP anchor:** <pain in their vocabulary, one sentence>

---

## Tier 2 — Problem-aware

**Audience knows:** the pain exists; doesn't know solutions exist (or
doesn't think any are worth evaluating yet).

**Best framing:** Pain reveal + reframe.

### Primary EVP
"<22-word line>"

### Alternate
"<22-word line>"

### Proof for this tier
<Demonstration of the pain at scale — e.g., "62% of Series-B SaaS hit
this within 18 months of funding.">

### Deploy on
- Hero copy on landing pages
- Top-of-funnel ad creative
- Cold email line 3 (when targeting based on signal that implies awareness)
- Podcast-appearance pitch lines

---

## Tier 3 — Solution-aware

**Audience knows:** solutions exist; comparing categories of approach
(in-house vs agency vs DIY vs tool).

**Best framing:** Category split — why your category beats the
traditional one.

### Primary EVP
"<22-word line>"

### Alternate
"<22-word line>"

### Proof for this tier
<Comparison: outcome metric of your category vs traditional approach —
e.g., "Targeted outbound: $640 CPM. Generic agency: $2,800 CPM.">

### Deploy on
- Comparison pages
- Mid-funnel ads
- Cold email line 3 (when targeting based on category-discontent signal)
- Sales call opener (when prospect has tried alternatives)

---

## Tier 4 — Product-aware

**Audience knows:** specific vendors exist; comparing options head to head.

**Best framing:** Vendor delta — your specific advantage on a specific
axis vs named competitor.

### Primary EVP
"<22-word line — references competitor>"

### Alternate
"<22-word line — references competitor>"

### Proof for this tier
<Specific competitor delta — e.g., "Versus <competitor>, we ship the
<feature> in <timeframe> instead of <their timeframe>.">

### Deploy on
- Pricing page hero
- Sales-call objection handling
- Battlecards
- Bottom-funnel ads

---

## The single source of truth

This brief is the authoritative messaging document for <ICP>. When
hero copy, ad creative, cold email, or pricing-page lines need to be
written or rewritten, pull from the tier that matches the audience's
actual awareness level.

Re-run this brief every 90 days. EVPs decay as the market catches up
and competitor positioning shifts.
```

## References

- `../../evp/SKILL.md` — the framework
- Sister skill: `evp-craft` for single-tier generation
- **EVP** course in The Compounding Engine:

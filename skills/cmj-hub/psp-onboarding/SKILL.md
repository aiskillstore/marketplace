---
name: psp-onboarding
description: First-run interactive setup for the PSP skill pack. Walks the operator through brand-config.json (ICP precision, exclusion criteria, signal sources) and SOUL.md (buyer vocabulary, stories, the 11am-Tuesday moment) in ~15 minutes. Refuses to let the operator skip — generic PSP output is worse than no PSP. Loaded automatically by the main psp skill when brand-config.json or SOUL.md is missing.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# PSP Onboarding — first-run setup

Walks the operator through ~15 minutes of setup that makes every
downstream PSP 10x more useful than generic framework prose.

## Activation

Loaded automatically by the `psp` orchestrator when `brand-config.json`
or `SOUL.md` is missing from the project root.

Also user-invocable: "Set up PSP brand config", "PSP onboarding", "Configure PSP".

## Why this exists

A generic PSP that says "Series-B SaaS feels pipeline pressure" is
worse than no PSP — it produces outreach that everyone else is also
producing. The 5-component PSP framework only generates real
differentiation when paired with:

- **Your ICP precision** (segment, exclusion, motion)
- **Your buyer's actual vocabulary** (sourced from real writing, not
  invented)
- **Your stories** (signal-to-pain mappings you've seen succeed or
  fail before)
- **Your won't-chase boundaries**

## Workflow

### Step 0 — Detect prior state

Check for existing `brand-config.json` + `SOUL.md`. If both exist, ask:
"Refresh, or skip?" If one exists, fill the gap.

### Step 1 — ICP precision

```
First, ICP. Be specific — "B2B SaaS" is too broad.

Tell me in one batch:
1. The 1-sentence segment (stage / size / motion / region)
2. The size range ($M ARR)
3. The motion (PLG / sales-led / hybrid)
4. The 3-5 exclusion criteria (who you don't sell to)

If your ICP is fuzzy, that's a finding — outreach against a fuzzy ICP
will be fuzzy. We can use placeholders for now and flag them for refresh
after 100 sends.
```

Save to `brand-config.icp`.

### Step 2 — Primary PSP draft

```
Now your primary PSP. Five components:

1. SIGNAL — what's a public, recent, verifiable thing your buyer does
   that implies the pain? (job post, funding round, leadership change,
   product launch, pricing change)
2. PAIN — what's the felt operational reality at 11am Tuesday when
   that signal is present? In their language, not yours.
3. TIMING TRIGGER — which 90-day window makes the pain acute now:
   new-exec / budget-cycle / obvious-failure?
4. FELT-PAIN ROLE — who at the buyer feels it most? (Often a layer
   below the buying authority.)
5. VOCABULARY — 4-8 phrases the buyer uses in private about this. If
   you don't know yet, that's step 3.
```

Save to `brand-config.psp_drafts.primary`.

### Step 3 — Vocabulary mining

```
If you don't have 4-8 buyer phrases yet, let's mine them.

Point me at any of these sources for the buyer segment:
- 3-5 of their public LinkedIn posts
- 1-2 podcast appearances
- 2-3 of their hiring job posts (job posts reveal pain language verbatim)
- 1-2 conference talks / panel appearances
- Their public AMA responses

I'll extract candidate phrases — you confirm which ones land.
```

If WebFetch is available, the skill can pull + extract directly. If
not, instruct the operator to paste content and run extraction.

### Step 4 — Signal sources (operations)

```
Where will you hunt these signals? (Mark all that apply.)

1. LinkedIn job search (daily — manual or via Phantombuster)
2. Crunchbase / news APIs (weekly)
3. RSS feeds for specific publications
4. Podcast feeds for relevant shows
5. Manual research only

How often refresh:
- PSP refresh cadence (default: 90 days)
- Vocabulary refresh (default: 30 days)
- Signal freshness window (default: 14 days — older signals drop)
```

Save to `brand-config.signal_sources` + `brand-config.research_cadence`.

### Step 5 — Stories (SOUL.md)

```
Tell me 3-5 stories that anchor your PSP — times you saw a signal-to-pain
mapping work or fail.

Each story: 1-2 sentences, anonymized but specific. These become
calibration points for the construct skill.

Also:
- Your won't-chase boundaries (topics / segments you refuse)
- The 11am-Tuesday operational moment of your buyer (paint it specific)
```

Save to `SOUL.md`.

### Step 6 — Write the files

Write `brand-config.json` + `SOUL.md` at the project root. Show preview:

```
✓ brand-config.json — ICP + 1 PSP draft + signal sources + cadence
✓ SOUL.md — 3 stories + vocabulary + 11am-Tuesday moment

Try a quick test:
> Construct a PSP for <segment>

The output will now use:
- Your ICP precision (not generic "B2B SaaS")
- Your vocabulary (not category jargon)
- Your stories as calibration

Next step: install `cmj-hub/claude-evp` to lock the EVP that speaks
to this PSP. Then `cmj-hub/claude-cold-email` to ship outreach.
```

### Step 7 — Refresh cadence

```
PSPs decay. Re-run onboarding when:
- ICP shifts (new segment / segment cull)
- Buyer vocabulary evolves
- Quarterly minimum (90 days)

Re-run: `/psp onboarding refresh`
```

## References

- `../../brand-config.example.json` — full template
- `../../SOUL.md` — voice template
- `../../AGENTS.md` — behavior rules
- Sister skills:
  - `psp-kickoff` — adaptive router that uses these files
  - `psp-construct` — uses brand + SOUL for actual PSP build
  - `psp-signal-hunt` — runs against your signal sources

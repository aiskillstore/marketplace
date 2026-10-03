---
name: psp-kickoff
description: Adaptive router for the PSP skill pack. Detects state (brand-config? SOUL.md? primary PSP drafted? secondary PSPs? vocabulary refreshed?) and picks the next-best step. Loaded by the main psp skill on bare invocation. Inspired by the coldoutboundskills kickoff pattern.
user-invocable: false
allowed-tools: Read Grep
  - Bash
license: MIT

---

# PSP Kickoff — adaptive router

State-aware router for PSP work. Operators don't ship outreach on
day 1 — they walk a sequence: ICP precision → primary PSP → vocabulary
mining → secondary PSPs → operationalize signal hunting → refresh.

## Activation

Loaded by `psp` on bare invocation, or:
- "Where do I start with PSPs"
- "What's next for my PSP work"
- "I'm new to PSPs"

## State detection

```python
state = {
    "has_brand_config":    file_exists("brand-config.json"),
    "has_soul":            file_exists("SOUL.md"),
    "has_primary_psp":     brand_config.psp_drafts.primary and brand_config.psp_drafts.primary.pain != "",
    "has_secondary_psp":   brand_config.psp_drafts.secondary is not None,
    "vocabulary_ok":       len(brand_config.psp_drafts.primary.vocabulary or []) >= 4,
    "signals_sourced":     any value true in brand_config.signal_sources,
    "psp_age_days":        days_since(brand_config.psp_drafts.primary.refreshed_at),
}
```

| State | Route to |
|---|---|
| `!has_brand_config OR !has_soul` | `psp-onboarding` |
| `has_config AND !has_primary_psp` | `psp-construct` (build primary PSP) |
| `has_primary_psp AND !vocabulary_ok` | "Vocabulary list <4 phrases — let's mine more. Need help?" |
| `vocabulary_ok AND !signals_sourced` | "Pick signal sources. Run `psp signal-hunt`." |
| `signals_sourced AND psp_age_days > 90` | "PSP last refreshed >90 days ago — re-run onboarding refresh" |
| `signals_sourced AND psp_age_days < 90` | "PSP is fresh + operational. Want to build a secondary PSP? Or push downstream into claude-evp + claude-cold-email?" |

## Welcome flow

```
> /psp

Welcome. Let's figure out where you are.

[Detected: brand-config.json missing]

You're at step 1 of 6:

1. ⬜ Onboarding — capture ICP + 1 primary PSP draft (15 min)   ← YOU ARE HERE
2. ⬜ Mine 8+ vocabulary phrases from real buyer writing
3. ⬜ Pick signal sources + cadence
4. ⬜ Run first signal hunt → 5-10 candidates
5. ⬜ Build secondary PSP for the next-priority segment
6. ⬜ Plug into claude-evp + claude-cold-email downstream

Step 1 takes ~15 minutes. Ready? (y/n)
```

## Status check mode

`/psp status`:

```
# PSP program status

Brand config:        ✓ brand-config.json
SOUL:                ✓ SOUL.md (3 stories)
Primary PSP:         ✓ "Series-B SaaS pipeline-gap" (refreshed 12 days ago)
Vocabulary:          ✓ 8 phrases mined
Signal sources:      ✓ LinkedIn + Crunchbase + 2 RSS feeds
Secondary PSP:       ⬜ Not yet built

Recommended next step:
→ Build secondary PSP for your next-priority segment, OR
→ Push primary PSP into claude-evp (lock the EVP) + claude-cold-email (ship outreach)
```

## References

- `../psp-onboarding/SKILL.md`
- `../psp-construct/SKILL.md`
- `../psp-signal-hunt/SKILL.md`

---
name: evp-kickoff
description: Adaptive router for the EVP skill pack. Detects state (brand-config? SOUL? primary EVP locked per tier? competitors named? proofs reservoir?) and picks the next-best step. Loaded by the main evp skill on bare invocation.
user-invocable: false
allowed-tools: Read
  - Grep
license: MIT

---

# EVP Kickoff — adaptive router

State-aware router for EVP work.

## Activation

Loaded by `evp` on bare invocation, or:
- "Where do I start with EVPs"
- "What's next for our positioning"

## State detection

```python
state = {
    "has_brand_config":   file_exists("brand-config.json"),
    "has_soul":           file_exists("SOUL.md"),
    "has_psp":            file_exists("brand-config.json") and brand_config.psp.primary_pain != "",
    "primary_tier_set":   brand_config.primary_outreach_tier in [1,2,3,4,5],
    "tier_2_locked":      brand_config.evp_drafts.tier_2_problem_aware.primary != "",
    "tier_3_locked":      brand_config.evp_drafts.tier_3_solution_aware.primary != "",
    "tier_4_locked":      brand_config.evp_drafts.tier_4_product_aware.primary != "",
    "has_proofs":         len(soul.proofs_reservoir) >= 3,
    "has_competitors":    len(brand_config.competitors) > 0,
}
```

| State | Route to |
|---|---|
| `!has_brand_config OR !has_soul` | `evp-onboarding` |
| `!has_psp` | "Install cmj-hub/claude-psp first — EVPs without a PSP are guesses" |
| `has_psp AND !primary_tier_set` | "Pick your primary outreach tier (most common is Tier 3)" |
| `primary_tier_set AND !tier_3_locked` (assuming T3 primary) | `evp-craft` (lock primary tier) |
| `tier_3_locked AND !has_proofs` | "Mine 3 proofs into SOUL.md before publishing the EVP" |
| `tier_3_locked AND has_proofs AND !tier_2_locked` | `evp-craft` for Tier 2 (problem-reveal variant) |
| `tiers 2/3/4 locked AND has_competitors` | `evp-brief` (build the 3-tier brief) |
| `brief_built` | "EVPs operational. Re-run every 90 days. Plug into claude-cold-email next." |

## Welcome flow

```
> /evp

Welcome.

[Detected: brand-config.json missing]

You're at step 1 of 5:
1. ⬜ Onboarding — capture tier + outcomes + tradeoffs + proofs   ← YOU ARE HERE
2. ⬜ Lock primary-tier EVP (3 variants generated, pick 1)
3. ⬜ Lock Tier 2 + Tier 4 EVPs for full coverage
4. ⬜ Build 3-tier brief (the canonical messaging doc)
5. ⬜ Re-evaluate every 90 days

Step 1 takes ~10 minutes. Ready? (y/n)
```

## References

- `../evp-onboarding/SKILL.md`
- `../evp-craft/SKILL.md`
- `../evp-brief/SKILL.md`

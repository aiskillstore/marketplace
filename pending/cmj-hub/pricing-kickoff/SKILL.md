---
name: pricing-kickoff
description: Adaptive router for the pricing skill pack. Detects the operator's current state (brand-config present? SOUL.md present? current tiers documented? WTP discovery done? PSP defined? value-metric chosen? reference anchor set? pocket-price waterfall built? quarterly review scheduled?) and picks the next-best step. Loaded by the main pricing skill on bare invocation ("/pricing") or when the operator asks "where do I start" / "what's next" / "first time using this."
user-invocable: false
allowed-tools: Read Glob
  - Bash
license: MIT

---

# Pricing Kickoff — sub-skill

The adaptive entry point. The operator runs `/pricing` and this
sub-skill detects state, surfaces a state checklist, and routes to
the next step. Goal: never make the operator guess where to start.

## Activation

The main `pricing` skill routes here when:

- User invokes `/pricing` with no arguments
- User asks "where do I start", "what's next", "first time using this"
- User asks "what should I do this quarter on pricing"

## The 9-step state machine

| # | Step | Detection | Next sub-skill |
|---|---|---|---|
| 1 | brand-config + SOUL set up | `brand-config.json` + `SOUL.md` exist | `pricing-onboarding` if either missing |
| 2 | Current tiers documented | `brand-config.json` has `pricing.currentTiers[]` populated | `pricing-onboarding` (tier section) if missing |
| 3 | PSP defined | `brand-config.json` has `customer.psps[]` populated | `claude-psp` companion pack if missing |
| 4 | WTP discovery done | `brand-config.json` has `pricing.wtpResearch.lastConducted` < 12 months ago | `pricing-diagnostic` if missing/stale |
| 5 | Value-metric chosen | `brand-config.json` has `pricing.valueMetric.unit` populated | `pricing-value-metric` if missing |
| 6 | Reference anchor set | `brand-config.json` has `pricing.referenceAnchor.frame` populated | `pricing-reference-frames` if missing |
| 7 | Pocket-price waterfall built | `brand-config.json` has `pricing.pocketWaterfall.steps[]` populated | `pricing-pocket-waterfall` if missing |
| 8 | Three-tier contrast set designed | `brand-config.json` has `pricing.tiers.architecture` = "three-tier-decoy" | `pricing-contrast-set` if missing |
| 9 | Quarterly review scheduled | `brand-config.json` has `pricing.review.nextScheduled` populated | `pricing-quarterly-review` if missing |

Steps 1-3 are blocking (everything depends on them). Steps 4-7 are
the diagnostic foundation. Steps 8-9 are the operating practice.

## Workflow

### 1. Detect state

Read `brand-config.json` and `SOUL.md` if present:

```bash
# Pseudo
[ -f brand-config.json ] && jq -r '.pricing // {}' brand-config.json
[ -f SOUL.md ] && grep -q "^## My stance on pricing" SOUL.md
```

For each of the 9 steps, mark ⬜ (not done), 🔶 (partial), or ✅ (done).

### 2. Surface state checklist

Output a readable state report:

```
Pricing setup — state check
─────────────────────────────────────────────────────────────────

1. ✅ brand-config + SOUL set up
2. ✅ Current tiers documented ($99 / $299 / $999 monthly)
3. ⬜ Pain Signal Profile defined          ← START HERE
4. ⬜ Willingness-to-pay discovery done
5. ⬜ Value-metric chosen
6. ⬜ Reference anchor set
7. ⬜ Pocket-price waterfall built
8. ⬜ Three-tier contrast set designed
9. ⬜ Quarterly pricing review scheduled

Recommended next step: Step 3 — define your Pain Signal Profile(s).
Pricing decisions without a PSP anchor produce one-size-fits-none
tiers. The companion claude-psp skill pack handles this in ~30 min.

Want to install claude-psp and run the PSP workflow now? (y/n)
```

### 3. Route based on state

| State | Action |
|---|---|
| Step 1 missing | Route to `pricing-onboarding` for full setup |
| Steps 2-3 missing | Route to `pricing-onboarding` (tier section) + suggest claude-psp |
| Steps 4-7 partial | Route to the lowest-numbered missing diagnostic step |
| Steps 8-9 missing | Route to `pricing-contrast-set` or `pricing-quarterly-review` |
| Everything done | Offer the "quarterly review" workflow + "what changed" diff |

### 4. Don't generate without state

If state isn't loaded and the operator says "just write me a pricing
page" — refuse, route to onboarding. Generic pricing is worse than
no pricing.

The operator can override with `--no-config` flag for sandbox runs;
warn that the output will be generic.

## Output format

Always include:

- The 9-step state checklist
- Which step is YOU ARE HERE
- One specific next action (with time estimate)
- A binary y/n to start that step now

Never list all 9 sub-skills as options ("pick one"). Always lead
with the recommended next step. The operator can override.

## Self-check

Before delivering the kickoff:

- [ ] Read `brand-config.json` and `SOUL.md` (or noted they're missing)
- [ ] All 9 steps checked
- [ ] Identified YOU ARE HERE
- [ ] Recommended ONE next action, not a menu
- [ ] Time estimate provided

## Reference

- `../../pricing/SKILL.md` — the orchestrator
- `../../pricing/references/pricing-framework.md` — full framework
- `../pricing-onboarding/SKILL.md` — what runs if state is empty

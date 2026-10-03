---
name: founder-brand-kickoff
description: Adaptive router for the founder-brand skill pack. Detects state (brand-config? SOUL? pillars filled? cadence set? recent posts logged?) and picks the next-best step. Loaded by the main founder-brand skill on bare invocation.
user-invocable: false
allowed-tools: Read
  - Grep
license: MIT

---

# Founder-Brand Kickoff — adaptive router

## Activation

Loaded by `founder-brand` on bare invocation, or:
- "Where do I start"
- "What's next for my content"

## State detection

```python
state = {
    "has_brand_config":  file_exists("brand-config.json"),
    "has_soul":          file_exists("SOUL.md"),
    "pillars_filled":    all 4 pillars have >=3 topics,
    "voice_fingerprints": len(soul.phrases_used) >= 5,
    "stories_reservoir": len(soul.stories) >= 3,
    "cadence_set":       brand_config.cadence.posts_per_week > 0,
    "this_week_done":    posts_logged_this_week >= cadence.posts_per_week,
}
```

| State | Route to |
|---|---|
| `!has_brand_config OR !has_soul` | `founder-brand-onboarding` |
| `!pillars_filled` | "Fill pillar topic pools (need ≥3 per pillar). Re-run onboarding to add." |
| `!voice_fingerprints` | "Mine phrases-I-use list — need ≥5. Read your last 10 posts/emails." |
| `!stories_reservoir` | "Capture ≥3 stories. Anonymized but specific." |
| `!cadence_set` | "Pick weekly cadence — default 4 posts/week, 1 per pillar" |
| `this_week_done` | "This week's queue done. Re-run on Monday for next rotation." |
| else | "Generate this week's post for the next pillar in rotation. Topic suggestion from your pool." |
```

## Welcome flow

```
> /founder-brand

Welcome.

[Detected: brand-config.json missing]

You're at step 1 of 5:
1. ⬜ Onboarding — voice + 4-pillar pools + cadence (15 min)   ← YOU ARE HERE
2. ⬜ Mine ≥5 voice fingerprints from your existing writing
3. ⬜ Capture ≥3 stories for the Proof reservoir
4. ⬜ Generate first week's posts (1 per pillar in rotation)
5. ⬜ Iterate weekly — auto-critique → ship → score

Step 1 takes ~15 minutes. Ready? (y/n)
```

## Weekly mode

When `cadence_set` and `this_week_done == false`:

```
# This week's queue

You're on the <PILLAR> rotation slot. Topic suggestion from your pool:

  "<Topic from brand-config.pillars.<pillar>.topic_pool>"

Want me to draft it? (y/n)

Other pool options for this slot:
  "<Topic 2>"
  "<Topic 3>"
```

## Status mode

`/founder-brand status`:

```
# Founder-brand program status

Brand config:        ✓ brand-config.json
SOUL:                ✓ SOUL.md (8 phrases, 7 refused, 5 stories)
Pillar pools:        ✓ All 4 pillars have ≥3 topics
Cadence:             ✓ 4 posts/week, Pillar→Proof→Process→Person
This week (Mon-Sun): 2 of 4 posts logged

Next: Wednesday — Process pillar slot. Suggestion: "<topic>"
```

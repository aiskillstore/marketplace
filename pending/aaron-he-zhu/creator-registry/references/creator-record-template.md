# Creator Record Template

Scaffold for canonical creator records at `memory/creators/<handle-slug>.md` — one file per creator, slug = canonical primary-platform handle in kebab-case (`sarah-ig`, `techtom-yt`). `creator-registry` is the sole writer; all other skills submit updates via `memory/creators/candidates.md` (line format at the bottom).

Records are roster state, not dated run artifacts: no `YYYY-MM-DD` filename, exempt from the 90-day WARM demotion (see [State Model](../../../references/state-model.md)). Archive only when the user drops the creator from the roster, executed by `memory-management`.

## Record frontmatter (modeled on the entity-optimizer profile contract)

```yaml
---
name: sarah-ig                          # slug matches filename; canonical primary handle
display_name: "Sarah Lee (@sarah_ig)"
type: entity                            # State Model frontmatter vocabulary
description: "Canonical roster record — beauty niche, IG-primary, 2 closed campaigns"
last_updated: 2026-07-02
primary_platform: instagram
handles:                                # cross-platform identity map
  - platform: instagram
    handle: "@sarah_ig"
    status: confirmed                   # confirmed | unconfirmed
    evidence: "bio link to linktr.ee matches TikTok bio"
  - platform: tiktok
    handle: "@sarahtok"
    status: unconfirmed                 # never merged on similarity alone
    evidence: null
contact:
  path: "email via media kit"          # confirmed contact path
  value: "sarah@example.com"
  waterfall_step: 2                    # which creator-dossier waterfall step produced it
  confirmed: 2026-05-14
roster_status: active                   # active | paused | dropped
exclusivity:
  status: exclusive-category            # none | exclusive-category | exclusive-full
  category: "skincare"
  expires: 2026-08-30                   # promote to hot-cache if within 60 days
contract_status: "signed 2026-05-20; usage rights 6mo, whitelisting excluded"
gdpr_basis: "legitimate interest, confirmed by user 2026-05-14"
---
```

## Record body sections

```markdown
## Audience Stats
| Metric | Value | As-of | Provenance |
|--------|-------|-------|------------|
| IG followers | 84,200 | 2026-06-28 | Measured (public profile) |
| IG avg engagement | 3.1% | 2026-06-28 | Estimated (last 12 posts) |
| Audience 18-24 share | 41% | 2026-05-10 | User-provided (creator media kit) |

## Rate Card & Negotiation History
| Date | Deliverable | Quoted | Agreed | Notes |
|------|-------------|--------|--------|-------|
| 2026-05-18 | 1 reel + 3 stories | $2,400 | $1,900 | countered once; bundle discount |

## Past-Campaign Baselines
| Campaign | Closed | Deliverables | Results (source) |
|----------|--------|--------------|------------------|
| spring-launch | 2026-06-15 | 1 reel + 3 stories | 92k views, 61 tracked orders (performance-analyzer 2026-06-20) |

## Compliance Events (append-only; dated; cite verdict IDs — never a roll-up label)
| Date | Event | Source |
|------|-------|--------|
| 2026-06-02 | #ad disclosure present and conspicuous | content-reviewer verdict ART-2026-06-02-sarah-ig-01 |
| 2026-04-11 | missing paid-partnership label on story 2, fixed same day | user-reported (no verdict ID) |

## Response History (facts only — no reputation rating)
- 2026-05-12: replied in 2 days to cold pitch; 2026-05-16: confirmed after 1 follow-up.

## Change Log
- 2026-07-02: merged 3 candidate updates (rate, exclusivity expiry, ART verdict); source: outreach-manager close-out + memory/audits/influencer/.
```

## candidates.md line format

Other skills append one line per update to `memory/creators/candidates.md`:

```markdown
- [2026-07-01] @sarah_ig | field: agreed_rate | value: $1,900 (1 reel + 3 stories) | source: outreach-manager close-out | provenance: User-provided
```

When 3+ lines accumulate for one creator, recommend `creator-registry` to reconcile.

## Merge precedence

1. Newer as-of date wins.
2. Same date: Measured > User-provided > Estimated; log the losing value in the change log.
3. Identity links: only bio cross-links, matching confirmed contact paths, or user confirmation upgrade `unconfirmed` → `confirmed`. Conflicts go to `memory/open-loops.md`, never silently merged.
4. Compliance events are append-only; nothing overwrites or summarizes them.

# Promotion and Demotion Rules

Promotion is an **explicit decision** (the user/skill pins an item), optionally cued by **observable
data signals**. No hook counts how often something is "referenced" or "requested", so never gate on
reference frequency — use the signals below or an explicit "promote X".

## Promotion Logic — Promote to hot cache when:

**Keyword signals**: significant rank movement (5+ positions); targeted in a new active campaign; a measured traffic spike.
**Competitor signals**: observed aggressive SEO activity; launching competing content; entered the tracked top-5 set.
**Metric signals**: anomalous value in the latest pull; tied to an active priority the user named.

**Promotion action:**
1. Add item to the relevant section in `memory/hot-cache.md`
2. Add note: "Promoted [date] - [reason]" and set `last_updated: [date]`
3. Keep detailed data in its WARM file / cold storage
4. The `last_updated` date is what the staleness scan reads — there is no separate reminder mechanism

## Demotion Logic — Demote to cold storage when:

**Keyword triggers**: `last_updated` 30+ days ago; target rank achieved and stable 60+ days; no longer in active strategy; replaced by higher-priority target.
**Competitor triggers**: no recorded activity in 60+ days (by `last_updated`); fell out of the tracked top-5; no longer targeting the same keywords.
**Campaign triggers**: completed 30+ days ago; cancelled or postponed indefinitely.

**Demotion action:**
1. Remove from memory/hot-cache.md
2. Archive full data in memory/[category]/archive/
3. Add line: "Last reviewed [category]: [date]"
4. Keep 1-line summary if historically significant

# Authoring examples

End-to-end recipes for adding, editing, and removing entries in the context repo. All examples assume you're authenticated (`cargo-ai whoami` works) and that the workspace already has a context repository configured.

> **Lead with frontmatter.** Every `.md`/`.mdx` write below starts with a YAML block carrying `title` and `description`. This is a strong convention, **not enforced** — a file with missing or malformed frontmatter is still committed, it just indexes poorly (the graph falls back to the filename for `title` and the first paragraph for the summary). To cite a source file so it shows up as a **graph edge**, list it in frontmatter `references:` (or use a markdown link / wikilink) — a bare path in prose creates no edge. See `../conventions.md` for the full linking rules.

## Discover before writing

```bash
# 1. What domains exist?
cargo-ai context runtime browse

# 2. What's already in the target domain? (avoid duplicates)
cargo-ai context runtime browse --path persona

# 3. What's the shape of an entry in this domain?
cargo-ai context runtime read --path persona/_template.md
```

## Add a persona

```bash
cargo-ai context runtime write \
  --path persona/head-of-revops.md \
  --content "$(cat <<'EOF'
---
title: Head of RevOps
description: Owns the GTM tech stack, data quality, and pipeline reporting at a 200–2,000-person B2B SaaS.
---

## Role

- Title: Head of RevOps / Director of RevOps
- Seniority: Director / VP
- Function: Revenue Operations
- Reports to: CRO or COO

## KPIs

- Pipeline velocity, forecast accuracy, data freshness, CRM hygiene, lead-to-opp conversion

## Pains

- Stale enrichment, broken CRM workflows, slow rep ramp because the data model is brittle
- Stitching together 6 point tools that don't talk to each other
- Manual segment refreshes for plays

## Motivations

- One source of truth across SDR, AE, CS
- Replace fragile Zapier chains with durable workflows
- Get out of the way of the frontline

## Day-to-day

Ops standup, reviewing failed syncs, building a new segment for an outbound play, fielding rep requests, and weekly forecast prep with the CRO.

## Preferred channels

_Cross-ref `medium/...`._

- medium/peer-community-slack
- medium/founder-led-linkedin

## Common objections

_Cross-ref `objection/...`._

- objection/we-already-have-clay
- objection/we-built-this-in-house

## How we land

Lead with the stack-replacement angle: "one durable workflow runtime that replaces enrichment + scoring + sync." Show, don't tell — run a workflow live against their domain on the demo call.
EOF
)" \
  --commit-message "Add Head of RevOps persona"
```

## Add a play with cross-refs

```bash
cargo-ai context runtime write \
  --path play/funding-triggered-outbound.md \
  --content "$(cat <<'EOF'
---
title: Funding-triggered outbound
description: Reach out to companies within 14 days of a Series A–C raise with a hiring-and-stack angle.
---

## Hypothesis

Companies hit a stack-and-headcount inflection right after a raise. If we land in the first two weeks with a stack-replacement angle, we beat the procurement freeze that sets in by week 4.

## Trigger

_Cross-ref `signal/...`._

- signal/series-a-funding-announcement
- signal/series-b-funding-announcement

## Audience

_Cross-ref `icp/...` or `persona/...`._

- icp/post-series-a-b2b-saas
- persona/head-of-revops

## Channel

_Cross-ref `medium/...`._

- medium/founder-led-linkedin
- medium/cold-email-personalized

## Sequence

1. Day 0: LinkedIn connect + congratulations note (no pitch).
2. Day 3: Personalized email referencing the raise + a single relevant stack-replacement angle.
3. Day 7: Follow-up with one proof point (cross-ref `proof/customer-x-replaced-three-tools`).
4. Day 14: Break-up message.

## Proof

_Cross-ref `proof/...`._

- proof/customer-x-replaced-three-tools
- proof/14-day-time-to-first-workflow

## Success metric

Reply rate ≥ 12% on Day 3 email; meetings booked / 100 contacted ≥ 4.

## Owner

Outbound AE pod lead.

## Variants

- Same play, swap LinkedIn for warm intro when one exists (cross-ref `medium/exec-warm-intro`).
EOF
)" \
  --commit-message "Add funding-triggered outbound play"
```

## Add a proof point

Keep `proof/` atomic — one metric or quote per file:

```bash
cargo-ai context runtime write \
  --path proof/14-day-time-to-first-workflow.md \
  --content "$(cat <<'EOF'
---
title: 14-day time to first workflow
description: New customers ship their first production workflow within 14 days of signing.
---

## Type

metric

## Content

Across the last 24 customers (Q1–Q3), median time from contract signature to first production workflow run was 14 days; P90 was 27 days.

## Source

Internal customer success tracker, pulled 2025-10-15.

## Client

_Aggregate across customers — no single cross-ref._

## Context

Used to counter the "another tool we'll never deploy" objection. Pairs well with `objection/we-already-have-clay`.

## Use cases

- objection/we-already-have-clay
- play/funding-triggered-outbound
- Sales decks, slide 9 ("Time to value")
EOF
)" \
  --commit-message "Add 14-day time-to-first-workflow proof point"
```

## Cite a source in an insight / learning doc

When an entry is derived from a specific source file in the repo (a sales-note, a call summary, a research output), cite it in frontmatter `references:` so the citation registers as a **graph edge** with a `frontmatter` origin. Prefer root-relative paths, and confirm the target exists first (`cargo-ai context runtime browse --path outputs/sales-notes`).

```bash
cargo-ai context runtime write \
  --path insight/agorapulse-expansion-readiness.md \
  --content "$(cat <<'EOF'
---
title: AgoraPulse expansion readiness
description: Why the AgoraPulse account is ready for a multi-thread expansion play.
references:
  - outputs/sales-notes/2026-06-05-agorapulse-build-session-1-outcomes.md
---

## Summary

AgoraPulse surfaced three net-new buying centers in the last build session — strong signal for a multi-thread expansion.

## Evidence

Drawn from the [[outputs/sales-notes/2026-06-05-agorapulse-build-session-1-outcomes|June 5 build-session outcomes]]: the champion named two adjacent teams already evaluating workflow tooling.
EOF
)" \
  --commit-message "Add AgoraPulse expansion readiness insight"
```

Both the frontmatter `references:` entry and the body wikilink (the `|` sets the display text) resolve to the same node — a bare `Source: outputs/sales-notes/...` line in prose would not. A standard Markdown link to the same file works too.

## Edit a single line

```bash
cargo-ai context runtime edit \
  --path global/positioning.md \
  --old-string "We help RevOps automate workflows." \
  --new-string "We help RevOps run AI-native GTM motions." \
  --commit-message "Refresh positioning one-liner"
```

## Delete a line from a file

```bash
# Read first to copy the exact line (whitespace must match!)
cargo-ai context runtime read --path persona/head-of-revops.md --start-line 18 --end-line 22

cargo-ai context runtime edit \
  --path persona/head-of-revops.md \
  --old-string "- Stitching together 6 point tools that don't talk to each other\n" \
  --new-string "" \
  --commit-message "Drop outdated pain point on Head of RevOps"
```

## Rename / move an entry

There's no `rename` command. Use `write` at the new path, then delete the old file with `execute` + push by overwriting it with `write` after removing — easier path: write the new file, then leave the old one in place until you're ready to remove it (a follow-up `write` with empty content is not supported; deletes happen via the GitHub UI or via `execute` followed by a manual commit step in the Cargo app).

For most renames, the cleanest sequence is:

1. `write` the new file at the new path.
2. Update every file that cross-refs the old slug — find them with `execute` + `grep`:
   ```bash
   cargo-ai context runtime execute --command grep --args '["-r","-l","persona/old-slug","."]'
   ```
3. For each match, `edit` the cross-ref `persona/old-slug` → `persona/new-slug`.
4. Delete the stale file via the GitHub UI (file the rename in a single PR if your context repo uses PR review).

## Verify your work

```bash
# Confirm the file is in place
cargo-ai context runtime read --path persona/head-of-revops.md

# Confirm it lights up in the graph and its cross-refs resolve
cargo-ai context graph get | jq '.nodes[] | select(.slug == "persona/head-of-revops")'
```

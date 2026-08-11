# Understanding the Project (rich or sparse input)

The quality of the OS depends on how well you understand the project before scaffolding. Always
produce an **Understanding Brief** first.

## Step 1 — Ingest everything
- Read every supplied file/transcript fully (don't skim). Note entities, processes, vocabulary,
  stages, recurring questions, and what the user clearly cares about.
- If the input is a single prompt, treat the prompt as the seed and move to inference.

## Step 2 — Identify the spine
Answer these explicitly:
- **Domain archetype** (consulting, product, label, research, agency, personal, other).
- **Core unit of work** — the thing that recurs and moves through stages (a deal, a feature, a
  release, a study, an account).
- **Lifecycle stages** of that unit, start to finish.
- **Key entities** that own records (clients, artists, teams, products).
- **Compounding assets** the domain reuses (templates, checklists, brand kits, datasets, scripts).
- **Recurring tasks** → these become skills.
- **Metrics** that should be tracked over time.
- **External tools / systems of record** likely in play (CRM, tracker, DAW, repo, drive).

## Step 3 — Handle sparse input with best-judgment prediction
When you only have a thin prompt, do NOT build a minimal stub and wait — predict the full system, but
express that prediction inside a **lean root**, not as a wide row of empty top-level folders.
- Pick the closest archetype from `blueprint.md` and adopt its mappings as a starting point.
- Enumerate the entities/stages/assets/routines/metrics a competent operator in that domain would
  need within 90 days.
- Scaffold that depth as **subfolders, stubs, and templates inside the core top-level folders**
  (predicted stages under `{pipeline}/`, starter templates in `library/`, FAQ/decision stubs under
  `knowledge/`) — not by adding more top-level directories.
- Keep the root to the core set; add an optional top-level folder (`reference/`, `proof/`, `content/`,
  `business/`) only when there's real material for it. When unsure, leave it out — it's one `mkdir`
  to add later.
- Seed starter templates and, when you have canon to seed, a `reference/principles.md` of domain best
  practices — each marked **"draft — confirm"** so the user can correct. A stub with a one-line README
  teaches where things go; an empty top-level folder just clutters the root.

## Step 4 — Write the brief
A compact brief, e.g.:
```
Domain: record label (independent)
Core unit: release (single/EP/album)
Stages: demo -> A&R -> signed -> production -> release -> promo -> catalog
Entities: artists/, releases/
Compounding: split sheets, release checklist, promo templates, press kit, contract clauses
Recurring tasks (skills): ingest-demo, build-release-plan, splits-tracker, promo-rollout, royalty-check, janitor, learn
Metrics: releases/quarter, streams, save rate, revenue/release, roster size
External SoR: distributor dashboard, DAW project store, accounting
Confidence: medium (from 1 transcript + roster list)
```
Confirm only material ambiguities; otherwise proceed to scaffold.

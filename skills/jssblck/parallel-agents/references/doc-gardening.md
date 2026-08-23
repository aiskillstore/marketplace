# Doc gardening

In agent-managed repos, docs are the top merge-conflict hotspot: measured over
real history, AGENTS.md and README beat every source file, because every
change routes an edit through them. Most of that routed content should never
have been written. The rule is to write less, deleting more, and
putting what remains where only the relevant changes touch it.

## What each layer is for

**AGENTS.md / CLAUDE.md hold scars and invariants. Nothing else.**

- Scars: hard-won, non-obvious constraints from development. The bug class
  that recurred, the design question that gets re-litigated every session,
  the footgun an agent will hit unless warned, the approach that looks right
  and fails. If learning it cost a session, write it down.
- Invariants: the rules that must hold. "Gates fail closed." "Never bump the
  crate version." "These two directories stay byte-identical."
- Not working state: no status sections, no progress logs, no TODO lists, no
  "currently implementing X". State belongs in issues, branches, or code.
- Not indexes or restatements: no subcommand lists, no command help output,
  no file inventories, no directory trees, no dependency lists. An agent
  discovers all of these with a glob or a `--help` in seconds, and the
  written copy only goes stale.

**User docs (README, guides) tell humans and agents how to use the product.**
Task-oriented: concepts, workflows, the decisions the user must make. The
same restraint applies: do not restate what the tool already reports (flag
inventories, subcommand lists, default values `--help` prints).

## The discoverability test

Before writing a fact into any doc: could a fresh agent learn this with one
grep, one glob, or one `--help`, in under a minute? If yes, do not write it,
and delete it if it is already there. Write down only what cannot be
discovered: intent, constraints, and why the obvious approach fails.

## Pruning

- Every edit to an instruction file should look for something to delete. A
  stale entry is worse than a missing one, because a missing fact gets looked
  up while a stale one gets trusted.
- Working state rots fastest. PROGRESS.md-style files, "implemented so far"
  sections, and checklists become disinformation the week the state changes.
  Delete them on sight, converting any durable lesson into a scar first.
- When a scar's underlying constraint disappears (the API changed, the
  footgun was fixed), remove the scar in the same change that removes the
  constraint.

## Sharding

- The root AGENTS.md or CLAUDE.md holds the invariants, the scars, and at
  most one line per module pointing at that module's own doc. Per-module
  detail lives in per-module docs (a developer-guide file per area, or a doc
  next to the module).
- A feature change updates its module's doc. The root changes only when a
  module appears or disappears, or an invariant changes. That is what takes
  the root file out of every commit's blast radius.
- Symptom to fix on sight: the root doc carries a paragraph-length
  architecture entry per module that duplicates the module docs. Shrink each
  entry to a line and a link, moving anything unique into the module doc.

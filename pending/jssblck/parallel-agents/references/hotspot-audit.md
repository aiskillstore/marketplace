# Hotspot audit

Conflicts concentrate where churn concentrates. This file covers finding the files
that attract every feature's edits and splits them so future work lands in
separate files. It is the retroactive companion to `one-feature-one-file.md`,
which prevents new hotspots from forming.

## Measure

Rank files by how many commits touched them over a recent window:

```sh
git log --since="3 months ago" --name-only --pretty=format: | grep -v '^$' | sort | uniq -c | sort -rn | head -25
```

Cross that against `wc -l`. The files to act on score high on both: churn
times size is a good single ranking. A small script beats eyeballing when the
repo is large.

## Diagnose before splitting

Not every hot file is a problem. Sort each candidate into one of three bins:

- **Hub**: touched by unrelated features. Read the last ten commits that
  touched it; if they share nothing except the file, it is a hub. Split it.
- **Hot concern**: touched often because that area is under active
  development. The churn is real work, not structure. Leave it alone.
- **Generated or lock file**: high churn is inherent. Splitting does not
  apply; handle these with `mergeable-edits.md` (regenerate, never
  hand-resolve).

Docs (AGENTS.md, README, design docs) are usually the top hotspots of all and
get their own treatment in `doc-gardening.md`.

## Split

- One file per concern. If the repo already has a split-by-concern directory
  (a module directory with `plan`, `runner`, `teardown` style siblings), copy
  that shape; consistency matters more than any particular layout.
- The split is a pure move: no behavior change, no symbol renames, no drive-by
  cleanup. The diff should be reviewable as "code moved, nothing else". Run
  the formatter and the full test suite; behavior must be identical.
- Update anything that points at the old layout: docs, architecture maps,
  paths in scripts and CI.

## Timing

A large move commit conflicts with every branch currently in flight, so a
split is a one-time conflict spike bought in exchange for a permanently lower
rate. Land it when the fleet is idle, or immediately rebase in-flight branches
after it lands. Do not interleave a split with feature work on the same files.

Note that plain `git log` on the new files starts at the move; `git log
--follow` recovers the prior history.

## Cadence

Re-run the measurement after a few weeks of fleet work. New hotspots form
wherever the structure still funnels unrelated growth into one file.

---
name: parallel-agents
description: "Use when parallel agents share a codebase: adding new behavior, editing or resolving conflicts in shared files (dispatchers, registries, lockfiles), finding and splitting churn hotspots, or writing AGENTS.md, CLAUDE.md, or README."
---

# Parallel agents

Merge conflicts among parallel agents concentrate in hub files: the files every
feature must touch regardless of what the feature is (the subcommand
dispatcher, the router, the single test main, the root AGENTS.md). Four rules
reduce them, in the order you usually need them:

1. **New behavior gets its own file.** The shared file it plugs into grows by
   exactly one line: a `mod` declaration, a route registration, a delegating
   match arm, a table entry.
2. **Shape edits to shared files so git merges them alone.** One item per
   line, stable insertion order, no drive-by rewrites of lines you did not
   need to change, and never hand-resolve a generated file or lockfile;
   regenerate it.
3. **Find and split existing hubs.** Rank files by churn times size, keep only
   the ones touched by unrelated features, and split them along concern seams
   as pure-move commits.
4. **Docs hold scars and invariants, nothing else.** Delete anything an agent
   can discover with one grep or `--help`, and shard per-module detail out of
   the root doc.

## References

Read the file that matches the task. Each stands alone.

- `references/one-feature-one-file.md`: where new behavior lives, how to
  recognize a hub, patterns by project shape (CLI, HTTP service, web UI,
  tests).
- `references/mergeable-edits.md`: list and registry discipline, formatter
  scope, ownership rules, generated files, resolving a conflict in a hub.
- `references/hotspot-audit.md`: the churn measurement command, hub vs hot
  concern vs generated triage, pure-move splits, timing and cadence.
- `references/doc-gardening.md`: what AGENTS.md/CLAUDE.md and user docs are
  for, the discoverability test, pruning, sharding the root doc.

# Generation contract

## Purpose

This contract keeps the portable skill complete, testable, and traceable to its native source without putting integration-specific commands in the canonical skill body.

## Required structure

The package must keep one canonical `SKILL.md` plus `references/`, `scripts/`, `scripts/tests/`, `assets/`, `examples/`, `evals/`, `mise.toml`, and `.github/workflows/ci.yml`. Files may sit only at the skill root or one subdirectory below it, except for the required workflow and test paths.

The canonical body must define the trigger, `help` and `refresh` grammar, ordered acquisition steps, script commands for shell and PowerShell, anchor fields, timezone order, daily header, per-turn prefix, relative-date rules, resume behavior, failure behavior, gotchas, limitations, examples, disclosure rules, and completion proof.

## Lossless source packet

The repository keeps byte-exact native source files under `evidence/ports/always-current-datetime/`. `manifest.json` binds every packet file by relative source path, byte count, and SHA-256. Formatting tools must ignore that packet so they cannot change its bytes.

`evals/source-lineage.json` binds the native manifest, native version, public version, source file hashes, source case IDs, and each public file to its source paths. `evals/source-mapping.json` records one hundred percent semantic coverage and forbids a `drop` action.

The portable body may replace integration-specific loader names, configuration commands, and environment names with capability-neutral equivalents only when the source packet remains exact and the same trigger, order, precedence, failure, visible output, and duplicate-suppression behavior stays testable.

## Script and test contract

`scripts/current_anchor.py` must accept flags, avoid prompts, emit one parseable JSON object on success, emit no stdout on invalid timezone input, and use exit `0` for success and exit `2` for input or runtime failure. It must acquire the current time exactly once per process.

Write or update `scripts/tests/` before changing script behavior. `mise run ci` is the single local and hosted entry point. It must run unit tests, structure validation, writing checks, code checks, and eval checks.

## Example contract

Each command in the grammar needs a complete example. Keep at least one failure example with the command, exit code, stdout state, stderr shape, blocked reply, and recovery. Any shown command output must come from a real run.

## Eval contract

Keep all eleven native source case IDs in `evals/cases.json`, `evals/evals.json`, `evals/manifest.json`, and `evals/source-lineage.json`. Trigger cases must cover ordinary direct messages, date questions, unrelated requests, second turns, resume, tool results, background events, and assistant commentary. Behavioral criteria must test freshness, prefix placement, daily-header suppression, temporal math, stale-anchor blocking, relative script execution, and hook equivalence.

## Completion proof

A structural PASS alone is insufficient. Completion requires byte-exact source packet hashes, complete source mapping, passing script tests, passing skill-local CI, passing repository validation, passing package checks, passing Agent Skills validation, and passing root `mise run ci`.

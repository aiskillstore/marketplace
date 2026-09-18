---
name: scan-new-specs
description: DEPRECATED and retired as of 2026-08-20. Do not invoke, and do not schedule. This skill scanned for merged PRODUCT.md specs and auto-drafted docs PRs, which produced documentation for features that had not shipped. Docs for newly shipped features are now triggered by the weekly release and gated on documentation-worthiness by the missing_docs skill in warpdotdev/docs. If you were about to run this skill to find docs gaps, run missing_docs in drift-watch mode instead.
---

# scan-new-specs (deprecated)

**Retired 2026-08-20. Do not invoke this skill and do not schedule it.**

Its scheduled agent (`0ITuF9vNJ1RiO00Szlm1fW`) is paused and stays paused.

## Why it was retired

The skill fired on **spec merge**, which happens before a feature ships. Two failures followed from that single design choice:

- **It drafted docs for unreleased and sometimes abandoned work.** A merged spec is not a shipped feature. The agent had no evidence of what users had actually received, so pages were written for behavior that had not landed, or had landed differently, or never landed at all.
- **It treated every spec as a docs task.** Nothing asked whether a change warranted documentation. Pure UI changes, small intuitive additions, and behind-the-scenes work all became draft PRs, and the docs repo accumulated unvetted content debt faster than anyone could review it.

## What replaces it

The `missing_docs` skill in `warpdotdev/docs`, running in drift-watch mode. It differs in the two ways that matter:

- **Release-triggered.** `scripts/check_new_release.py` gates each run on a new stable release, so the pipeline sees what actually shipped rather than what was planned. A daily schedule does per-release work.
- **Gated on worthiness.** Every candidate is evaluated against `.agents/references/docs-worthiness-criteria.md` before anything is drafted, with a default of no docs and a requirement to name concrete evidence. Verdicts, including rejections, are recorded in `references/changelog_decisions.md` so nothing is re-litigated.

Anything genuinely worth documenting re-surfaces there once it ships.

## If you were about to run this

- **Looking for docs gaps?** Run `missing_docs` in drift-watch mode from the `warpdotdev/docs` repo.
- **You are an engineer who wants docs for your feature?** Invoke `write-feature-docs` directly and interactively. It still works, and it still walks you through spec research and outline confirmation. It no longer runs headlessly.
- **Setting up a scheduled docs agent?** Use `missing_docs`, not this. Scheduling this skill reintroduces exactly the flooding it was retired for.

## Related skills

- `missing_docs` (in `warpdotdev/docs`) — the release-triggered, worthiness-gated replacement
- `write-feature-docs` — still supported for direct, interactive use by an engineer

---
name: w-lint
description: Run project linters, apply the smallest fixes, and re-run until the suite is clean.
disable-model-invocation: true
---

Run the repository lint scripts and apply the smallest idiomatic fixes. This is not a merge gate and does not commit.

1. Run the documented lint command with autofix when the repo provides one. Capture remaining errors.
2. Fix remaining issues with minimal diffs. Change suppressions or config only with evidence they belong.
3. Re-run lint. Spot-check the diff. Do not stage or commit.
4. Docs: `/w-docs` if behavior or commands changed.

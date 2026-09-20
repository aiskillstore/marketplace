---
name: w-fix-push
description: Fix reported issues, validate, then commit and push.
disable-model-invocation: true
---

Invocation requests fix → smallest matching check → commit → push for the named issues. This is not `/w-ship` (no PR, not the full pre-push suite) and not a merge or deploy. Follow [git publish](references/git-publish.md).

1. Address the reported errors, warnings, or feedback (lint, types, tests, reviews).
2. Run the smallest existing check that matches the failure. Never the full pre-push suite.
3. Commit intended paths only, then push the inspected upstream. Do not open a PR unless the user asked `/w-pr` or `/w-ship`.

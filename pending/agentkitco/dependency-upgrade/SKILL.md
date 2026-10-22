---
name: dependency-upgrade
description: Upgrade one dependency at a time by reading its changelog, planning for breaking changes, updating code and proving the project still builds and passes. Use when asked to bump, update or migrate a package or framework.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Upgrade a dependency safely

Goal: move one dependency (or one tightly coupled group) to a newer version with the breakage understood in advance, not discovered afterwards.

## Plan

1. **Pin down the current state.** Find the installed version (lockfile, not just the manifest) and the target version. If the user said "latest", look it up with the package manager (`npm view <pkg> version`, `pip index versions <pkg>`, `cargo search`, etc.) and state the number.
2. **Record a baseline** on a clean working tree: install, build, tests, lint, type check. Note any pre-existing failures so you do not blame the upgrade for them.
3. **Read the real release notes.** Open the changelog, release notes or migration guide for every version between current and target. Extract: breaking changes, removed or renamed APIs, new minimum runtime versions, changed defaults, deprecations. Quote the source link for each item. If you cannot find release notes, say so and treat the upgrade as higher risk.
4. **Map the impact.** `rg` the codebase for each removed, renamed or changed API. List affected files before editing.

## Execute

- Upgrade only this dependency (and required peers). Do not run a blanket "update all".
- Update the manifest and lockfile with the project's package manager, not by hand.
- Make the code changes the notes require, smallest first. Replace deprecated usages when the new form is equivalent.
- Run install, build, tests, lint and type check again. Compare with the baseline.
- For major versions, also run the app or the main example path if feasible, and check bundle size, startup warnings and deprecation warnings.
- If the upgrade needs a minimum runtime or peer version bump, stop and ask before changing it.

## Report

```
Upgrade: <pkg> <from> -> <to>
Sources: <changelog links>
Breaking changes that applied: <list with file refs>
Changes made: <summary>
Verification: <commands, baseline vs after>
Warnings or follow-ups: <deprecations, skipped items, risks>
Rollback: revert <files>, or `git revert <commit>`
```

## Rules

- Never upgrade and refactor in the same change.
- Never skip a failing test or loosen a version range to hide a problem.
- Security fixes: say which advisory the upgrade addresses only if you saw it in an official advisory or the release notes.
- If a transitive dependency forces a conflict, show the conflict output and propose options rather than overriding blindly.

# npm-release Checklist Contract

## Diagnosis

Release failures come from publishing on stale auth/version assumptions or letting package, changelog, tag, and registry truth drift.

## Checklist Mode

- Mode: do-confirm
- Evidence sink: package files, release commit/tag, npm registry state, and final release report
- Failure route: publish, blocked, rollback, or stop before irreversible release action

## Pause Points

1. Before version commit: prove clean main, version decision, changelog, and registry identity.
2. Before real publish: dry-run and tag/commit parity must pass.
3. After publish: verify npm view, tarball, and install/help smoke.

## Required Checks

- [ ] working tree is clean on `main` and unpushed commits are understood
- [ ] `npm whoami` succeeds against the target registry before real publish
- [ ] package.json, package-lock.json, CHANGELOG, commit, and tag versions match
- [ ] `npm publish --dry-run --access public` succeeds before real publish
- [ ] post-publish `npm view` and install/help smoke prove registry parity

## Exit Rule

Do not exit this skill with a success claim until every required check is satisfied, explicitly skipped with a reason, or routed to the failure route above. The checklist is not a new artifact to fill out; it is the execution gate that must be reflected in the skill's normal evidence sink.

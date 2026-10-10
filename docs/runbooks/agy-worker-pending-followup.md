# agy-worker pending follow-up — Issue 3703

Scope: [Issue #3703](https://github.com/aiskillstore/marketplace/issues/3703). Preserve the published v0.22.0 artifact and let a newly audited submission supersede pending v0.24.0. Do not publish v0.24.0 merely to empty the queue. The independent listing-copy [PR #3699](https://github.com/aiskillstore/marketplace/pull/3699) is not a package upgrade.

## Observed state (2026-10-09)

- Main at investigation: `d4b8cec1b1913d420d55c31bafc3cc07b5fe47c1`.
- Published `skills/cagdasyurekli/agy-worker`: v0.22.0, source `6916f8859768c50929cc45ac8bc45e4d74784844`.
- Pending `pending/cagdasyurekli/agy-worker`: v0.24.0, source `228924b2522f3708046cfd874015c5f0a8dad21c`, merged [PR #3697](https://github.com/aiskillstore/marketplace/pull/3697).
- PR3697 merge statuses were empty and recent publication receivers were completed at readback; this is not a permanent reservation or permission to delete. Recheck active work before operations.
- GitHub resolves both repository spellings `cagdasyurekli/codex-agy-worker` and `cagdasyurekli/agy-worker` to the latter repository. Existing published/pending reports retain the former source identity. Their provenance must not be rewritten casually.
- Exact v0.24.2 commit `1ec3c6199c79c61b7ee23253a196d860c2ac3a6c` was resolved through the old repository URL by GitHub's commits API.

## Root cause and narrow fix

`classify-submission-targets.mjs` previously rejected any pending target when the same Skill already had a published target. The existing aggregation workflow already supports both published-update snapshots and pending-replacement snapshots, but the classifier never emitted both for this state.

The fix admits this coexistence only after both targets independently pass their existing source/repository/slug/author/tree validations, both match the requested exact source path, and incoming/published/pending source refs are immutable hashes. It freezes both targets: the published package remains untouched; only freshly processed/audited results may replace pending through the existing exact tree/report/Git-tree/source guard. A matching pending revision remains a no-op. A replay of the published revision while a different pending revision exists is rejected. Unrelated repositories, ambiguous paths, mutable refs, alternate namespaces and unsafe filesystem paths remain rejected.

The workflow's existing published-snapshot check remains mandatory before it commits/pushes the replacement. No workflow identity gate, auto-merge criteria, audit fields, provider state or production credentials change in this fix.

## Verification

```sh
CI=true node --test scripts/tests/submission-existing-targets.test.mjs scripts/tests/replace-pending-submission.test.mjs scripts/tests/submission-runtime-workflow.test.mjs
node --check scripts/classify-submission-targets.mjs
git diff --check
```

Observed local tests: two new reproduction cases fail on the old implementation; the three affected suites pass 53/53 after the minimal change. A fixture runs classification and the real pending replacement function together and compares published SKILL.md/report bytes before/after. Existing replacement tests reject report/tree/source/Git-tree races.

Read-only classification against the real checkout accepts v0.24.2 with the original `cagdasyurekli/codex-agy-worker` identity, emitting both snapshots. Using the new repository spelling still rejects an identity mismatch intentionally; this fix is not a generic repository-rename migration.

## Rollout and requestor retry

1. Obtain independent review and exact-head CI; normal merge the code fix without bypassing provenance protections.
2. Recheck publication receivers and both frozen targets. Coordinate with the existing provider recovery task: do not resume a batch that would publish superseded v0.24.0 before its pending payload is safely replaced.
3. Ask the submitter to use the exact original-identity URL for a normal fresh submission: `https://github.com/cagdasyurekli/codex-agy-worker/tree/1ec3c6199c79c61b7ee23253a196d860c2ac3a6c/skills/agy-worker`. Re-verify that GitHub still resolves it to the expected repository/commit first. Do not create an account-linked submission ID on their behalf or reuse the old audit.
4. Observe new audit completion and a trusted App replacement PR. Independently review/merge via normal gates; confirm pending v0.24.0 is replaced and the published v0.22.0 artifact was not changed during submission processing.
5. Publication/provider/cache/callback evidence remains separate. Close Issue3703 only after the supported retry path actually succeeds or the requestor confirms resolution, not merely when this code PR merges.

No production submission, deletion, scan, callback, provider replay or catalog sync was performed while preparing this fix. Reverting the code change restores strict collision behavior without changing any Skill artifacts. A live supersession must preserve its original Git/audit history; never resurrect an old pending payload automatically.

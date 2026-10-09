# Issue3703: exact-report publication hold (proposed code, not deployed)

This PR prepares a narrow safety guard before the separate provider recovery can unblock automatic continuation. It does not recover provider stages, alter GitHub statuses, merge submissions, replace pending content, or authorize deployment.

## Source evidence

- [Issue #3703](https://github.com/aiskillstore/marketplace/issues/3703): preserve published v0.22.0; do not publish obsolete pending v0.24.0 simply to empty the queue. A new reviewed submission must safely supersede it.
- Main read at 2026-10-09T17:22Z: `755bc353599695fcfc6bbf0c0c9a76fd3e6a4897`.
- Exact pending report: `pending/cagdasyurekli/agy-worker/skill-report.json`, version 0.24.0, Git blob `9db4ee7c8a2fe82d3dd189dfb36198d10ffd583f`.
- Trusted merged owner [PR #3697](https://github.com/aiskillstore/marketplace/pull/3697) has the identical file path/blob. Head `b3abb28a220e59e65bd5a5225d7f84a483cb12aa`, merge `561c1742ac3fb557a3b96169586dad1dd14454c6`.
- [Continuation run 37958995644](https://github.com/aiskillstore/marketplace/actions/runs/37958995644), 2026-10-09T16:25Z: actual enumeration was pending=8, candidates=[3695,3696,3697,3698,3700,3702,3704,3705], unmatched=[]. It then failed at the previous provider sync gate. Enumeration is NOT final selection, dispatch or publication evidence.

## Minimal shared guard

`assertPublicationReportNotHeld(reportPath, blobSha)` lives inside the existing `resolve-approved-submission.mjs` validator, whose source hash already determines the preflight validator revision. No new dependency, credential, service, policy file or configurable bypass.

1. Continuation checks the CURRENT pending inventory before ownership scanning, provider gates or dispatch. The exact path/blob pair throws `PublicationValidationError`. This intentionally holds the entire automatic queue; it does not skip the owner and thereby jump over unknown historical reservations/effects.
2. The shared publication resolver checks the same pair using a Git-compatible SHA1 computed from raw report bytes, after filesystem/path/symlink validation and before parsing/resolving a skill publication plan. Both the single receiver and batch receiver already use this resolver. A manual dispatch is therefore not a bypass once the receiver uses this code revision.
3. Other paths and blobs are not held by this incident-specific guard, but still undergo all existing provenance, exact-tree, frozen-source, receiver reservation, provider and audit validation. A different report blob is NOT approval and does not by itself prove a safe replacement.

The guard is byte-specific, not an indefinite ban on this slug/version. Do not edit whitespace, source identity, audits or report content to evade it. Keep the old bytes and audit history intact until a normally reviewed replacement is available. Submission/classifier code is unchanged; replacing pending through the trusted submission path is distinct from publishing it.

## TDD and bounded verification

- New `scripts/tests/publication-hold.test.mjs`: six tests; initial expected result 5 failures/1 pass, then 6/6 pass.
- The decisive counterexample injects a fake GET-only inventory and clear downstream gates into continuation **with --apply**; before the fix it records a mocked dispatch of the held owner, after the fix it throws before further reads or any mocked write. No live API is called by these tests.
- A second case verifies the non-apply path is held too. Negative controls leave unrelated paths/blob values on ordinary gates, not an unconditional release path.
- Raw report hash vectors cover ASCII and UTF-8 byte length; source-wiring assertions cover both receivers sharing the check.
- Full affected test slice: `CI=true node --test scripts/tests/publication-hold.test.mjs scripts/tests/publication-continuation.test.mjs scripts/tests/resolve-approved-submission.test.mjs scripts/tests/publish-approved-batch.test.mjs scripts/tests/publication-receiver-workflow.test.mjs` — 60/60 PASS, zero skips.
- Additional local read-only test against the actual fixed pending tree (39 files) confirms the resolver rejects blob `9db4ee7c...`, then rereads it unchanged. No provider calls, GitHub writes or source changes.

## Production sequence and limitations

This PR is review-only until separately approved and merged. Local tests/CI do not prove production enforcement. The safe order is:

1. Independently review this hold or an alternative safe replacement plan. Do NOT clear the provider gate first.
2. If separately authorized to deploy the hold, verify exact merged code in all continuation/single/batch entry points, and inspect any queued/in-flight receiver code revisions/reservations. A historical run may still carry older loaded code; this patch cannot retroactively rewrite it. Do not rerun it to test the hold.
3. Verify the old pending cannot publish before any action that can unlock continuation. No scheduler pause or workflow dispatch is performed by this PR.
4. Obtain a new immutable-source submission with a fresh audit and trusted review; replace old pending through the normal exact-snapshot mechanism. Retain published v0.22.0 until the replacement completes its own required publication checks.
5. Recheck current report blob, owning trusted PR, source tree and absence of incompatible active effects. Only then consider separately authorized provider-stage recovery and gate reconciliation. The provider's partial artifact/current/observation GET evidence does not prove catalog/audit/callback/score/cache success and cannot stand in for a successful complete manual run.

Trade-off: the minimal guard intentionally keeps other automatic publications waiting while the exact old report is present. Isolating unrelated candidates without weakening oldest-first/unknown-effect safety would be a separate design, not a hidden change here. Reverting the guard while the old blob remains restores the original risk; rollback is not permission to publish it.

No implementation of S2/S3 copy editing, production authentication, pending replacement, provider repair, status backfill or batch release is included. S1 remains independently accepted and unchanged.

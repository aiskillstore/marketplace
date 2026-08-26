# Standing autonomy

Use a durable autonomy grant only after an explicit candidate instruction such as “apply autonomously.” Store no prompt text in the grant.

```text
node scripts/job-application.mjs autonomy grant --stdin
node scripts/job-application.mjs autonomy status
node scripts/job-application.mjs autonomy preview
node scripts/job-application.mjs autonomy revoke
```

Grant input:

```json
{ "mode": "routine-auto" }
```

An active grant covers discovery, assessment, verified form filling, canonical résumé upload, routine submission, verified recruiting email, ledger/outcome recording, completed-tab cleanup, and opening a sanitized improvement PR. Do not ask for another skill-level upload or submission approval while both the profile and grant use `routine-auto`.

Always stop for authentication, MFA, CAPTCHA, legal attestations, demographic responses, government identifiers, unverifiable claims, and ambiguous work authorization or compensation. Obey every browser, host, and tool permission prompt; the grant never bypasses an access control.

`autonomy revoke` blocks new routine transmissions without deleting applications, outcomes, rounds, or queued attention items.

## Improvement boundary

Record friction while the application round continues. Open a public-agent PR only when the issue is reproducible, general-purpose, sanitized, and covered by a regression test. Validate the full suite, privacy audit, package smoke test, and secret scan before marking the PR ready.

Never automatically merge, tag, release, or publish. Never alter telemetry privacy boundaries, candidate facts, résumé claims, targeting thresholds, or answer guidance from an improvement PR. Keep live application work on the latest released package; do not hot-swap unmerged code.

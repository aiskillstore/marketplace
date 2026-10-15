# Example review-bot protocol

The parser is an integration example, not a bundled review service. Fixtures were constructed for testing and contain no real conversations. Configure your own trusted sender and adapt this parser if your bot's documented output differs. Never normalize arbitrary messages into a clean result.

A start message contains a unique job ID and the exact PR URL set:

```text
AI Review job `sample-job`
Requested by Example User · mode: cross · 1 PR
https://bitbucket.org/example-workspace/service/pull-requests/205
```

A zero-finding completion for that same job has explicit counters:

```text
AI Review job `sample-job` reached state: completed.

Automatic publication: 0 published and verified, 0 duplicate(s) skipped, 0 unverified.

Summary:
Cross review complete. Shared sources (also adjudicated): 0; Codex-confirmed candidates: 0; final gap-scan additions: 0; rejected: 0; explicitly merged duplicates: 0; uncertain summary-only: 0.
```

Published findings, existing duplicate findings, unverified publication, shared/confirmed findings, additional findings, unresolved duplicates or uncertain decisions block announcement. Rejected candidates alone do not. Retained advisory or context decisions require inspection. Failed/running jobs remain waiting within the bounded run. A newer job invalidates an older clean result. A bot may edit its status message in place, so inspect its current text rather than assuming a late completion timestamp.

Thread parent identity and exact PR URLs, trusted sender, job identity, explicit zero-outstanding counters, and unchanged live source/destination commits are separate checks. Preserve all when adapting the protocol.

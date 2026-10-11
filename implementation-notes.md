# Implementation notes

## 2026-10-11 — Publication dependency outcomes

- Repeated wakeups behind one failed provider write report `blocked` with its original run link, not a new execution error. Waiting, blocked, idle and dispatch outcomes are written to job outputs and the run summary; none imply production acceptance.
- Check active/failed dependencies before fetching all approval files. Reconciliation completion now wakes continuation directly. Exact recovery proof, no-replay, publication holds and source validation remain required; API/integrity failures and stalled runs still fail.

## 2026-10-11 — Submission author identity

- CLI reports preserve the upstream YAML author as a display name; it is not required to equal the GitHub owner login. Existing-target classification now uses the owner-scoped path, report slug and canonical source repository/ref as authority, while requiring a nonempty display author.
- This applies to both published and pending updates without rewriting old reports. Snapshot hashing, source mismatch rejection, symlink rejection and approval provenance stay unchanged.

## 2026-10-11 — General Actions recovery

- Recovery uses a failed run ID to derive immutable scope. No skill names, incident IDs or source-specific exceptions enter the implementation.
- The artifact must already be current and exact. Recovery finishes ancillary stages with CLI 2.17.0; failed evidence stays immutable and a separate verified reconciliation releases continuation.
- GitHub PR files are capped at 3,000 by the provider. Read the declared count completely or fail; do not silently truncate a large approval.
- Use the existing locked YAML parser for discovery, with lifecycle scripts disabled and bounded alias expansion; valid flow mappings must not be rejected by a scalar regex.
- Invalid upstream frontmatter is a rejected input, not a processing success. Unknown/system errors and nonempty unsafe source-monitor changes still fail.
- Existing no-replay and publication provenance gates remain active. The original reconciliation verifier's single-publication limitation remains; batch recovery requires complete multi-owner proof before it can be enabled.

# Implementation notes

## 2026-10-17 — Reviewed Skill distribution

- Publishing checks the site's authenticated source authority (live immutable GitHub repository ID plus upstream path) and committed distribution markers, including after rebase. Withdrawal/erasure survives source repository rename or transfer; report-supplied IDs are not trusted.
- The existing cache secret authenticates a five-minute scheduled worker. It advances at most five stages, fails visibly on incomplete processing, and never publishes applicant identity or reviewer evidence. Merge after the site endpoint and database migration are deployed.
- Reimport is blocked by tombstones; restoration requires the site's reviewed lifecycle. Git history and external installed copies remain outside current-tree deletion. No historic Git rewrite.

## 2026-10-11 — Publication dependency outcomes

- Repeated wakeups behind one failed provider write report `blocked` with its original run link, not a new execution error. Waiting, blocked, idle and dispatch outcomes are written to job outputs and the run summary; none imply production acceptance.
- Check active/failed dependencies before fetching all approval files. Reconciliation completion now wakes continuation directly. Exact recovery proof, no-replay, publication holds and source validation remain required; API/integrity failures and stalled runs still fail.

## 2026-10-11 — Submission author identity

- CLI reports preserve the upstream YAML author as a display name; it is not required to equal the GitHub owner login. Existing-target classification now uses the owner-scoped path, report slug and canonical source repository/ref as authority, while requiring a nonempty display author.
- This applies to both published and pending updates without rewriting old reports. Snapshot hashing, source mismatch rejection, symlink rejection and approval provenance stay unchanged.


## Historical Notes Summary

- 2026-10-11 — General Actions recovery — Preserve existing publication checks and recovery boundaries; full decisions remain in Git history.

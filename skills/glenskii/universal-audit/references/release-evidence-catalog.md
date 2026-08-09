# Release Evidence Catalog

Use this catalog to select evidence that can support a release decision. A completed command alone is not sufficient. Capture the target, result, date, and any material limitation.

## Build and change identity

- Commit hash, release tag, or immutable build identifier.
- Dependency lockfile and build output tied to the same revision.
- Deployment identifier when the review covers a running environment.

## Verification evidence

- Test results with the command, environment, and executed scope.
- Manual test notes for critical user journeys, accessibility, and error handling.
- Security review findings with affected components and confirmed remediation status.
- Infrastructure checks for configuration, access, and recovery controls when they are in scope.

## Gate evidence

- A complete list of failed, unverified, and accepted-risk items.
- Named ownership and a due date for every accepted risk.
- A clear release verdict: BLOCKED, REVIEW REQUIRED, or PASS.

Do not turn unavailable evidence into a pass. Record the limitation and use REVIEW REQUIRED or BLOCKED when the missing evidence prevents a reliable release decision.

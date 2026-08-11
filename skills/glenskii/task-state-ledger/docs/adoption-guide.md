# Task State Ledger adoption guide

Task State Ledger keeps long technical work legible after a pause, handoff, or change in scope. It gives the next person or compatible tool a short record of what happened, what was proved, and what must happen next.

Its deliberately constrained, progressive-disclosure structure preserves decision rationale, evidentiary boundaries, and retrieval discipline across complicated multi-stage technical work.

The ledger supports reliable continuation without pretending that file records are automatic memory or a substitute for authorization, retention, and privacy decisions.

Use it when fragmented transcripts, repetitive diagnostics, and uncertain ownership would otherwise obscure the evidence required for a responsible next action.

This controlled recordkeeping approach improves operational accountability when several contributors, tools, or sessions must interpret the same technical history.

## Use cases

### Debug a difficult release

Record the release target, failed checks, evidence node IDs, current owner, and next test. Keep raw logs in reviewed evidence nodes instead of pasting them into every follow-up.

### Hand off work safely

Record the task boundary, completed changes, validation result, known limits, and the one next action. A handoff should state what remains unverified, not only what was completed.

### Resume a multi-file change

Record affected files, decisions that constrained the work, and the evidence needed to make the next change. Read the state record before reopening a large build log or a long diff.

## Best practices

1. Update the ledger after a material decision, failure, or verified milestone.
2. Keep the state record short enough to read in one pass.
3. Link to reviewed evidence by stable node ID and relative path.

## Anti-patterns

1. Do not use the ledger as a dump for complete logs or copied conversation history.
2. Do not save credentials, customer data, cookies, or unreviewed configuration files.
3. Do not call a task complete when the ledger says important evidence is missing.

## Prompt templates

### Start a ledger

```text
Use $task-state-ledger to create a ledger for this project. State the task boundary, current objective, and evidence limits before recording anything.
```

### Record a verified milestone

```text
Use $task-state-ledger to record this completed milestone. Save only the reviewed evidence needed to support the result and state what remains unverified.
```

### Prepare a handoff

```text
Use $task-state-ledger to prepare a handoff. Record completed work, open blockers, evidence paths, safety limits, and one next action.
```

### Resume focused work

```text
Use $task-state-ledger to resume this task. Read the current state first, then retrieve only the evidence needed for the next decision.
```

## Output examples

### Release-check state

```text
Objective: Verify the release candidate before deployment.
Completed: Build and static checks passed.
Evidence: evidence/build-01.md, evidence/static-02.md.
Limit: Browser testing is still unverified.
Next action: Run the browser check against the staging address.
```

### Handoff state

```text
Objective: Correct the form submission failure.
Completed: Reproduced the error and isolated the request handler.
Evidence: evidence/request-01.md.
Blocker: Test credentials are not available.
Next action: Obtain approved test access before active verification.
```

## Frequently asked questions

### Does this replace normal project documentation?

No. It records the live working state. Keep design documents, runbooks, and user guides in their normal locations.

### Does this save every conversation automatically?

No. It records selected state and selected evidence only after an explicit action.

### Does this guarantee lower cost or faster work?

No. It can reduce unnecessary retrieval when used well, but it cannot guarantee a fixed result.

### Where should evidence live?

Keep it in `.task-state/evidence/` unless the project has an approved equivalent. Exclude the directory from version control unless a reviewed record is safe to publish.

### Can a team share one ledger?

Yes, when the team agrees on access and retention rules. Keep secrets and private material out of the shared ledger.

### When should an evidence record be deleted?

Follow the project retention rule. Delete only after confirming that it is no longer needed and that the deletion is authorized.

## Capabilities and limits

The ledger can record concise task state, write sanitized evidence through its helper, and guide selective retrieval. It cannot recover omitted details, alter a host application's history, or guarantee privacy after unsafe material has been saved. Read the [privacy and retention guidance](../references/privacy-and-retention.md) before recording logs, browser output, or configuration details.

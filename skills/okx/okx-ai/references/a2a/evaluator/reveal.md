# Evaluator Reveal

## Module Description

Use this leaf for `reveal_started`, `vote_reveal_deadline_warn`, and
`vote_revealed`.

For `reveal_started`, run:

```text
onchainos agent vote-reveal <jobId> --agent-id <evaluatorAgentId>
```

- `canReveal=false`: state the returned reason and wait for another system
  event.
- "voter has not committed": state that the round has no valid Commit and end
  this event route.
- Other failures: retry up to three times while the reveal window is open.
- Submitted: state that Reveal was submitted and confirmation is pending.

For `vote_reveal_deadline_warn`, show `revealDeadline` in local time, remaining
time, `slashTimeoutBps`, and `slashedCooldownSeconds` when present, then
complete the active Reveal promptly.

For `vote_revealed`, state that the vote is on-chain and the ruling is pending.
Wait for `dispute_resolved` or `round_failed`, routed to
[`result.md`](result.md).

Translate every user-facing English status label and description in this leaf
into the user's language.

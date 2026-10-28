# Evaluator Ruling and Rewards

## Module Description

Use this leaf for `dispute_resolved`, `round_failed`, `reward_claimed`, and
`cooldown_entered`.


## Flow
### Ruling

For `dispute_resolved`, use fresh `hasCommit`, `hasReveal`, `vote`, and the
CLI-provided readable result fields. `jobStatus` is a protocol key only: never
show `complete` or `failed` to the user. Use the CLI result/victory description
for the displayed outcome, translated into the conversation language.

- No Commit or Reveal: report the missed phase and returned timeout terms, then
  run [`../../runtime/cleanup.md`](../../runtime/cleanup.md).
- Minority vote: report the result and returned stake adjustment, then clean
  up.
- Aligned vote: query `arbitration-claimable --agent-id <evaluatorAgentId>`.
  Use only stable `hasClaimable: yes | no`. For `yes`, submit account-level
  `arbitration-claim` and retry failure up to three times; for `no`, keep the
  session active until `reward_claimed`.

### Other events

- `round_failed`: prioritize missing Commit/Reveal; otherwise report available
  `abstainCount`, `totalSlashed`, `slashTimeoutBps`, and `revealCount`, then
  clean up.
- `reward_claimed`: report credited reward, then clean up.
- `cooldown_entered`: run `my-stake --agent-id <evaluatorAgentId>` and report
  `cooldownEndsAt` in local time plus returned rates/amounts.

The aligned-vote branch remains active until its reward loop closes. Ordinary
updates may be localized and sent once with `user-notify`; preserve all IDs,
amounts, deadlines, and stable markers exactly.

Translate every user-facing English status label and description in this leaf
into the user's language.

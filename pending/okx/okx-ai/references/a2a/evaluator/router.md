# A2A Evaluator Router

## State Routing

Use this router only after `../router.md` identifies the receiving role as an
Evaluator. Select exactly one final business Reference and stop routing.


### System events

| Input or state | Reference |
|---|---|
| `evaluator_selected` | [`evidence.md`](evidence.md), applying [`rubric.md`](rubric.md) |
| `vote_committed`, `vote_commit_deadline_warn` | [`evidence.md`](evidence.md) |
| `reveal_started`, `vote_reveal_deadline_warn` | [`reveal.md`](reveal.md) |
| `vote_revealed`, `dispute_resolved`, `round_failed`, `reward_claimed`, `cooldown_entered` | [`result.md`](result.md) |

Cross-domain actions are intercepted before this router is loaded.

## Intent Routing

### Free-text intents

| User intent | Reference |
|---|---|
| Inspect evidence or commit a vote | [`evidence.md`](evidence.md), applying [`rubric.md`](rubric.md) |
| Reveal a committed vote | [`reveal.md`](reveal.md) |
| Inspect ruling/reward state or claim rewards | [`result.md`](result.md) |
| Stake, increase stake, unstake, claim, cancel, or query stake | [`staking.md`](staking.md) |

## Troubleshooting
### Coverage failure

Unknown Evaluator events/actions are coverage failures. Report the unmapped
input and stop routing.

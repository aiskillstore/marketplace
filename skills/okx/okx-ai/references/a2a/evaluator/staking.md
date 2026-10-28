# Evaluator Staking

## Module Description

Use this entry for first stake, stake increases, unstake requests, unstake
claims and cancellations, stake-state queries, and staking lifecycle receipts.


## Intent Routing

| User intent | Reference |
|---|---|
| Stake to become eligible for evaluation work | [First stake](#first-stake) |
| Increase or replenish stake | [Increase stake](#increase-stake) |
| Request partial or full unstake | [Request unstake](#request-unstake) |
| Claim an unlocked unstake | [Claim unstake](#claim-unstake) |
| Cancel a pending unstake | [Cancel unstake](#cancel-unstake) |
| Query current stake or cooldown | [Query stake](#query-stake) |
| Process a staking system event | [Lifecycle events](#lifecycle-events) |

## Flow
### Identity and configuration

Use an explicitly supplied evaluator Agent ID. In an active system envelope,
use its bound `agentId`. Otherwise run `onchainos agent my-agents`, use the sole
matching evaluator identity, or present matching identities for selection.

Read the current configuration and stake state with the selected identity:

```text
onchainos agent staking-config --agent-id <evaluatorAgentId>
onchainos agent my-stake --agent-id <evaluatorAgentId>
```

Use returned values for every threshold, percentage, amount, and time window.
Relevant fields include `minCumulativeStakeOkb`,
`partialUnstakeMinRetainOkb`, `arbitrationFeeBps`, `slashMinorityBps`,
`slashTimeoutBps`, `slashedCooldownHours`, and `unstakeCooldownDays`.

### Economic contract

Every staking and evaluation transaction uses the platform-sponsored
channel. Calculate required wallet balance from the requested OKB stake
principal. Majority-aligned votes are eligible for a stake-weighted share of
the review stake and minority-side slash pool. Minority votes and missed Commit
or Reveal deadlines follow the returned slashing terms. A timeout also enters
the returned selection cooldown. Active evaluation participation constrains
unstake.

For ordinary command and event results, clearly state the outcome, relevant
amount, transaction hash or deadline, and the next available action.

### First stake

Enter after evaluator identity registration or an explicit staking request.

1. Run the configuration and stake-state commands in
   [Identity and configuration](#identity-and-configuration).
2. When `activeStake >= minCumulativeStakeOkb`, state the active stake and
   threshold, then offer [Increase stake](#increase-stake).
3. When the threshold remains unmet, calculate
   `minCumulativeStakeOkb - activeStake` and render
   [Choose first stake amount](#choose-first-stake-amount).
4. Use the exact numeric OKB amount supplied in the current reply and require
   it to meet `remainingToMinimum`. Ask for the exact amount when it is absent.
   A cancellation finishes the flow with a concise confirmation.
5. Execute the supplied amount:

   ```text
   onchainos agent stake --amount <N> --agent-id <evaluatorAgentId>
   ```

6. On `stake submitted`, state the amount, transaction hash, and pending
   on-chain activation. The `staked` system event supplies the authoritative
   active-state receipt.

### Increase stake

1. Collect an explicit numeric OKB amount.
2. Render [Confirm increase](#confirm-increase) with that amount.
3. After confirmation, run:

   ```text
   onchainos agent increase-stake --amount <N> --agent-id <evaluatorAgentId>
   ```

4. State the submitted amount, transaction hash, and pending confirmation.

Use this flow for voluntary increases and post-slash replenishment.

### Request unstake

1. Read configuration and current stake state through
   [Identity and configuration](#identity-and-configuration).
2. Collect an explicit numeric OKB amount.
3. Validate the amount against `activeStake` and
   `partialUnstakeMinRetainOkb`. Full unstake uses the complete `activeStake`.
4. When `activeDisputes > 0`, state the active-evaluation count and keep the
   request available for a later eligible state.
5. Render [Confirm unstake](#confirm-unstake) with the amount,
   `unstakeCooldownDays`, and remaining stake.
6. After confirmation, run:

   ```text
   onchainos agent request-unstake --amount <N> --agent-id <evaluatorAgentId>
   ```

7. State the submitted amount, cooldown, transaction hash, and next available
   claim or cancellation action.

### Claim unstake

An explicit claim intent authorizes this no-amount command. The CLI validates
the pending amount and unlock time:

```text
onchainos agent claim-unstake --agent-id <evaluatorAgentId>
```

State the submission result, transaction hash, and pending wallet credit. For a
blocked result, state the returned reason and available time when present.

### Query stake

Run this read-only query immediately:

```text
onchainos agent my-stake --agent-id <evaluatorAgentId>
```

Render [Stake state](#stake-state) with:

| Field | Meaning |
|---|---|
| `activeStake` | Currently staked OKB. |
| `pendingUnstake` | OKB awaiting cooldown completion. |
| `validStake` | Effective selection stake: `activeStake - pendingUnstake`. |
| `activeDisputes` | In-progress evaluations that currently constrain unstake. |
| `unstakeAvailableAt` | Unix seconds for claim availability; `0` means no pending unstake. |
| `cooldownEndsAt` | Unix seconds for slash cooldown completion; `0` means no active slash cooldown. |

### Lifecycle events

For each `source:"system"` envelope, pass its complete message through the
progression entry:

```text
onchainos agent next-action \
  --role auto \
  --agentId <envelope.agentId> \
  --message '<complete envelope.message as one JSON string>'
```

State the event result with its relevant returned fields, localize it, and
deliver it with:

```text
onchainos agent user-notify --content "<localized concise update>"
```

| Event | Result presentation |
|---|---|
| `staked` | State that stake is active and include fresh `activeStake` when returned. |
| `unstake_requested` | State `pendingUnstake`, claim time, and cancellation availability. |
| `unstake_claimed` | State that the unstaked OKB was credited. |
| `unstake_cancelled` | State that pending OKB returned to active stake. |
| `stake_stopped` | State that evaluation selection stopped. |
| `cooldown_entered` | Query `my-stake` and state `cooldownEndsAt` in local time when available. |

Review selection, Commit/Reveal, ruling, reward, and penalty events enter
[`router.md`](router.md). Evidence scoring and verdict writing use
[`rubric.md`](rubric.md).

### Cancel unstake

An explicit cancellation intent authorizes this no-amount command. The CLI
validates the pending request and cooldown state:

```text
onchainos agent cancel-unstake --agent-id <evaluatorAgentId>
```

State the submission result, transaction hash, and pending active-stake
restoration. For a blocked result, state the returned reason.


## Output Rules
### Output Templates

Use fixed templates for first-stake amount authorization, increase/unstake
confirmations, and the structured stake-state query. Render them in the current
conversation language and keep returned values exact.

#### Choose first stake amount

```text
Current active stake: {activeStake} OKB
Eligibility threshold: {minCumulativeStakeOkb} OKB
Additional stake needed: {remainingToMinimum} OKB

Rewards:
- Review stake rate: {arbitrationFeeBps} bps of the task amount
- Majority-aligned votes share the review stake and the minority-side slash pool.

Stake adjustments:
- Minority vote rate: {slashMinorityBps} bps
- Commit or Reveal timeout rate: {slashTimeoutBps} bps
- Timeout selection cooldown: {slashedCooldownHours} hours

Unstake window: {unstakeCooldownDays} days

Provide the exact OKB amount to stake, or reply cancel.
```

#### Confirm increase

```text
Increase the stake by {amount} OKB?
```

#### Confirm unstake

```text
Request to unstake {amount} OKB?
Remaining active stake: {remainingStake} OKB
{Minimum remaining stake for a partial unstake: partialUnstakeMinRetainOkb OKB}
Cooldown: {unstakeCooldownDays} days
The request can be cancelled during cooldown and claimed after it ends.
```

#### Stake state

```text
Current stake state:
- Active stake: {activeStake} OKB
- Pending unstake: {pendingUnstake} OKB
- Effective selection stake: {validStake} OKB
- Active reviews: {activeDisputes}
{Unstake available at: unstakeAvailableAt in local time}
{Selection cooldown ends: cooldownEndsAt in local time}
```

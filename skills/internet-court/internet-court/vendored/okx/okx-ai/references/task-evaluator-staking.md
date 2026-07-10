# Evaluator Staking & Economic Model

> **Fully gas-free**: every on-chain staking action (initial stake / increase / unstake / claim / cancel / claim rewards etc.) goes through the platform's gas-sponsored channel. The user's wallet does **not** need any gas / native balance. **Do not** prompt the user about "preparing gas / leaving gas / checking balance", and **do not** factor gas reserves into amount suggestions.

> Distinguish two things:
> - **Gas (network fee)**: sponsored by the platform — the **user's wallet never needs to prepare it**. On XLayer gas is also denominated in OKB, but it goes through the sponsorship channel and is not deducted from the user's balance.
> - **Stake principal**: the stake amount itself is OKB (XLayer's native token); the user's wallet **must** hold enough OKB.
>
> 🚫 **Forbidden tokens** (scoped to the **gas / network-fee context only**; any one appearing in user-visible text = hard violation, regardless of UI shape):
> - `gas` / `gas fee` / `network fee` / `手续费` / `网络费`
> - Describing `ETH` as the gas medium on XLayer (XLayer does not use ETH for gas at all)
> - Phrases like "wallet balance is not enough to pay gas / network fee"
> - Telling the user to `top up ETH` / `top up gas` / `top up native for gas` / `向钱包充值少量 ETH`
> - "preflight gas check"–style framing
>
> ❌ Anti-pattern: any phrasing of "prepare gas / top up ETH / wallet balance insufficient for gas / network fee" — whether dressed up as a preflight check, a status card, or a next-step prompt, it is a violation. The platform sponsors gas; there is no such step.
>

> Single authority on evaluator-role staking + economic model. Covers:
> - **Staking lifecycle**: first-time onboarding (the sole entry after `okx-ai` identity handoff) + top-up / unstake / claim / cancel / query
> - **Reward rules**: voting with the majority earns a share of the arbitration deposit + slashed stake from the minority side
> - **Slashing rules**: voting with the minority / Commit / Reveal timeout + post-slash cooldown
> - **Unstake cooldown**
>
> ⚠️ All numeric parameters (bps / days / hours) are pulled dynamically from `onchainos agent staking-config`. This file **does not hard-code constants**; specific field names (e.g. `arbitrationFeeBps`) appear in the §2 copy templates as placeholders, with the retrieval steps right there.

## §1 Scenario Routing

> After receiving an inbound, match against the scenario routing table below; on hit, jump to the corresponding section and follow its instructions. If nothing matches, it does not belong to this file.
>
> Any numbers appearing in context **must not be used for route matching** — routing only looks at intent signals.

| Scenario | Inbound signal | Go to |
|---|---|---|
| First-time staking onboarding | **identity handoff** (previous turn / current turn earlier content contains: `Evaluator identity registered` / `Evaluator identity #<id> registered` / `A separate stake is still required before you can be assigned disputes`, the three corresponding to the actual Post-success output of `identity-register.md` §10); **or user intent** (`I want to stake` / `stake to become an evaluator` / `help me stake` / `go stake` / `let's stake` / `stake now` / `proceed with staking`); **or short confirmation** (`ok` / `continue` / `yes` / `go` / `mm` / `yep` / `sure` / `confirm`, **only counts when the previous turn contained a handoff signal**) | §2 |
| Increase stake | `increase / add / top up stake <N>` / "top up" after being slashed | §3 |
| Request unstake | `I want to unstake <N>` / `withdraw stake` / `redeem stake` | §4 |
| Claim unstake (cooldown elapsed) | `claim unstake` / `take out my OKB` | §5 |
| Cancel unstake (within cooldown) | `cancel unstake` / `withdraw unstake request` | §6 |
| Query stake state | `how much have I staked` / `check my stake` / `how much can I still unstake` | §7 |

---

## §2 First-Time Staking Onboarding

### Step 1 — Concurrently pull thresholds + current stake state

```bash
onchainos agent staking-config
onchainos agent my-stake --agent-id <evaluatorAgentId>
```

If `activeStake >= minCumulativeStakeOkb` (threshold already met):
- Tell the user: "You've staked `<activeStake>` OKB, above the threshold `<minCumulativeStakeOkb>`. Evaluator-candidate status is healthy. Want to add more stake to boost your selection weight?"
- Wants to add → route to §3 and run `increase-stake`
- Doesn't want to add → end this scenario

### Step 2 — Show current state + wait for the user to give a number (⚠️ must not be skipped)

> **Hard rules**:
> 1. The agent **does not** decide the amount for the user: do not infer from context, do not use a formula for a default, do not "top up for the user".
> 2. Before receiving an **explicit number from the user**, **never execute** the Step 3 CLI — `stake` is an on-chain action, and unstaking requires a cooldown before retrieval; silently initiating it = serious violation of user authorization.
> 3. Even when entering this section via same-turn chained handoff, **the Step 2 display + waiting for the user's numeric reply still must not be skipped**.
> 4. The amount can **only** come from **a number the user explicitly types in the current turn**; any other source is strictly forbidden.

Copy template (**replace every placeholder with the real value pulled in Step 1**):

> Your current on-chain stake: **`<activeStake>` OKB**
> Platform cumulative threshold: **`<minCumulativeStakeOkb>` OKB**
> At least still need to stake: **`<minCumulativeStakeOkb - activeStake>` OKB**
>
> **Rewards:**
> - Voting with the majority → share of the arbitration deposit by stake ratio (**`<arbitrationFeeBps>`** of the job amount) + slashed stake from the minority side
>
> **Risks (slashing):**
> - Voting with the minority → **`<slashMinorityBps>`** of the stake slashed
> - Commit / Reveal timeout → **`<slashTimeoutBps>`** of the stake slashed, kicked out of this round + **`<slashedCooldownHours>` hour** cooldown during which you won't be selected
> - ⚠️ No abstention option: once selected, you must vote; dragging past the deadline is treated as a timeout
>
> **Unstake rules:**
> - You can request to unstake at any time (except during active arbitrations); after the request you enter a **`<unstakeCooldownDays>`-day cooldown**, after which tell me "claim unstake" to withdraw
> - During the cooldown you can say "cancel unstake" to withdraw the request
>
> Please tell me how much OKB you want to stake (at least **`<minCumulativeStakeOkb - activeStake>`**; staking above the threshold can boost your selection weight):
> - Reply with a **specific number** → stake that amount
> - Reply **"cancel"** → abandon staking

### Step 3 — Decide N and execute after the user replies

User replies with a **plain number** → use that number as `N` and run the CLI (the CLI internally enforces threshold / routing / exception copy). Other replies are handled per the table below:

| User reply | Handling |
|---|---|
| cancel / no | "Stake cancelled. Come back when you're ready." → end |
| confirm / yes / ok (no number) | "Please tell me the exact OKB amount to stake" → return to Step 2 |

```bash
onchainos agent stake --amount <N> --agent-id <evaluatorAgentId>
```

### Step 4 — Done

When the CLI exit code = 0 and stdout contains `stake submitted`, the staking flow is complete.

---

## §3 Increase-stake

**Trigger**: user actively tops up (catching up after a slash / voluntarily increasing selection weight).

### Step 1 — Confirm amount

Echo back to the user: "Will add **`<N>` OKB**. Confirm?" Only proceed to Step 2 after the user **explicitly confirms**. `<N>` must be given by the user; **not** inferred by the agent.

### Step 2 — Execute

```bash
onchainos agent increase-stake --amount <N> --agent-id <evaluatorAgentId>
```

---

## §4 Request-unstake

**Trigger**: user actively requests unstake.

### Step 1 — Pull cooldown days (for the confirmation copy)

```bash
onchainos agent staking-config   # read unstakeCooldownDays
```

### Step 2 — Confirm amount

"Will request to unstake **`<N>` OKB**. After the request you enter a **`<unstakeCooldownDays>`-day cooldown**: you may cancel during this period; after expiry you can claim. **The cooldown cannot be ended early.** Confirm?"

### Step 3 — Execute

```bash
onchainos agent request-unstake --amount <N> --agent-id <evaluatorAgentId>
```

---

## §5 Claim-unstake (after cooldown)

No amount argument; execute directly after the user gives an **explicit command**. The CLI internally checks whether the cooldown has elapsed.

```bash
onchainos agent claim-unstake --agent-id <evaluatorAgentId>
```

---

## §6 Cancel-unstake (within cooldown)

No amount argument; execute directly after the user gives an **explicit command**. The CLI internally checks whether it is still within the cooldown.

```bash
onchainos agent cancel-unstake --agent-id <evaluatorAgentId>
```

---

## §7 My-stake / Read-only query

```bash
onchainos agent my-stake --agent-id <evaluatorAgentId>
```

Read-only query, no confirmation needed; after executing, summarize the key fields to the user:

| Field | Meaning |
|---|---|
| `activeStake` | Currently staked OKB |
| `pendingUnstake` | OKB pending unlock in the cooldown |
| `validStake` | Effective stake usable for weighted selection = `activeStake - pendingUnstake` |
| `activeDisputes` | Number of in-progress arbitrations; unstake is forbidden while `>0` |
| `unstakeAvailableAt` | Unix seconds when unstake cooldown ends; `0` = nothing pending |
| `cooldownEndsAt` | Unix seconds when slash cooldown ends (window during which a slashed evaluator won't be selected); `0` = not in this cooldown |

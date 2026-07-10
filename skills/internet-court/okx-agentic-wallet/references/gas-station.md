# Gas Station (Solana)

Gas Station lets the user pay gas with a stablecoin (USDT / USDC / USDG) when they lack native SOL. On Solana the Relayer is the fee payer; the stablecoin fee is collected via an SPL Token Transfer inside the same transaction — **no account upgrade, no per-chain setup, no 7702**. Solana only.

**Supported scenarios**: all SPL token transfers and contract interactions (swaps, DeFi supply / borrow / redeem / claim, bridge initiation, any SPL / program interaction). Native SOL transfers do NOT trigger Gas Station. State (enable flag, default token) is scoped to `(account, Solana)`.

Edge cases, FAQ answers, and failure diagnosis live in [gas-station-troubleshooting.md](gas-station-troubleshooting.md).

## Critical Rules

**Backend dispatches; Agent reacts.** Do NOT check SOL balance or decide whether to use Gas Station yourself. Call `wallet send` / `wallet contract-call` as normal, read the CLI's **`scene`** discriminator (and `gasStationUsed`), and dispatch via the Outcome → render map below — do not re-derive the scene from raw backend fields. On a Confirming, show the matching scene's verbatim copy and ask the user to pick a token.

Always surface Gas Station when native SOL is insufficient but a supported stablecoin has enough balance — for both a fresh attempt and a "why did my transfer fail?" follow-up. When a GS transfer is blocked because the default token is insufficient and the account holds another stablecoin, propose switching the gas token (Scene C, zero-cost) before "reduce amount" or "top up default token".

- **NEVER pass `--gas-token-address` / `--relayer-id` / `--enable-gas-station` on the FIRST call.** They are second-phase values, used only after the user picks a token from a Confirming response.
- **NEVER fabricate token addresses or relayer IDs** — use the exact values from the Confirming response's `next` field.
- **NEVER proactively push Gas Station** when the user is browsing or asking unrelated questions.
- **NEVER call Gas Station "free"** — there is a service charge in the selected stablecoin. Display `serviceCharge` + `serviceChargeSymbol` when present.
- **NEVER combine Gas Station with Jito Bundler** — hard block (troubleshooting Edge Case 2).

### Output discipline (applies to every template here and in troubleshooting)

All user-facing copy is product copy: render the template body verbatim, substituting only bracketed slots. When the user's language is not English, translate at output time while preserving structure and every fact — keep every clause (e.g. "now set as the default Gas token"), never substitute a chain noun (render "Solana" as-is), no leading setup line, no trailing notes beyond the template.

**Output vocabulary**: refer to the feature only as "Gas Station" and the choice as "which stablecoin to pay gas". Never surface internal field names (`gasStationFirstTimePrompt`, `gasStationUsed`, `autoSelectedToken`, `hasPendingTx`, `insufficientAll`, `signType`, `multiSignerTx`, `Phase 1/2`, `DB flag`), numeric error codes, or debug/log paths.

## Flow

Gas Station is not a separate command — the backend decides per-request whether to dispatch it inside the `wallet send` / `wallet contract-call` response. First-time / token-switch cases use the Confirming Response pattern (exit code 2, Scene A / C); when a default token is pinned it runs silently (Scene B / D). **Token priority** (list ordering + auto-select): balance descending; ties USDT > USDC > USDG.

### Outcome → render map

Map the CLI `scene` directly to the fixed copy below; do NOT re-derive it, do NOT author copy yourself. On a Confirming, `next` carries the exact re-run command.

| CLI `scene` | Render | Then |
|---|---|---|
| `gs_first_time` | Scene A | Get consent + token pick → follow `next` (re-run with `--enable-gas-station --gas-token-address <pick> --relayer-id <pick>`). On success → Scene A two-step. |
| `gs_reenable` | Scene A (re-enable variant) | Same as `gs_first_time`; backend overwrites the previous default. |
| `gs_token_switch` | Scene C | Get choice 1 / 2 / 3 → follow `next`. On success → Scene C post-success echo. |
| `gs_insufficient_all` | Scene E | Bail. Do NOT re-run. |
| `gs_pending_tx` | Edge Case 4 (troubleshooting) | Bail. Do NOT auto-retry. |
| success + `gasStationUsed=true` (no `scene`) | Universal Success Reply | — |

Jito hard-block, tx-cap, async-hash, native-SOL are Agent-detected — see troubleshooting Edge Cases.

## Scene A — Not enabled, SOL insufficient, has sufficient stablecoin

Backend returns `gasStationFirstTimePrompt=true` + `gasStationTokenList` (≥1 `sufficient=true`; if none → Scene E).

```
Your SOL balance is not enough to pay Gas. Two ways to proceed:

1. Top up SOL and pay with the native token.
2. Enable "Gas Station" and pay Gas directly with a stablecoin.

About Gas Station: Gas Station aggregates third-party services, automatically compares rates and picks the cheapest one to cover Gas on your behalf. It accepts USDT, USDC, or USDG — you do not need to hold Solana. Learn more: https://web3.okx.com/learn/wallet-gas-station

- Once enabled, whenever the native token is insufficient, the system will automatically pay Gas with the stablecoin — no manual confirmation needed.
- By default the token with the highest balance is used; you can also pin a specific token as the default for every transaction. Tokens supported on this chain: USDT, USDC, USDG.

Confirm enabling Gas Station and paying this transaction's Gas with stablecoin?
```

Never modify the body, drop the academy link, drop the two bullets, drop the "Tokens supported on this chain" line, or reduce to a bare yes/no.

**Consent**: on a pick → follow `next` (re-run with that token's `--gas-token-address` + `--relayer-id`; if the user confirmed without naming one, use the highest-balance sufficient token). On decline → do NOT re-run; tell them to top up SOL at `{fromAddr}`. Ambiguous / token not in list → re-prompt once, never guess.

**Post-success (MANDATORY two-step, on every Scene A trigger):**

Step 1 — pin the used token as default. Resolve `{chosen_token_address}` from `serviceChargeFeeTokenAddress` (or the `--gas-token-address` passed in phase 2), then call once, silently (treat non-zero exit as soft failure, continue):
```
onchainos wallet gas-station update-default-token --chain solana --gas-token-address {chosen_token_address}
```
Step 2 — echo verbatim (keep every sentence):
```
Gas Station enabled. This transaction will pay Gas with {chosen_token}, and {chosen_token} is now set as the default Gas token. Whenever the native token is insufficient from now on, {chosen_token} will be used automatically — no further confirmation needed. You can change the default Gas token at any time.
```
`{chosen_token}` = the stablecoin symbol actually used. Then append the Universal Success Reply.

## Scene B / D — Silent auto-path

Backend returns `gasStationUsed=true` + `autoSelectedToken=true` + non-empty `hash`; CLI silently signs + broadcasts. **B**: a default token is set and sufficient. **D**: no default set, exactly one stablecoin sufficient — backend auto-selects (do not prompt). Reply: no GS prompt, just the Universal Success Reply. For Scene D, add a one-line note that the auto-selected token was used.

## Scene C — Enabled, default token insufficient

Backend returns `gasStationUsed=true` + `hash` empty + `gasStationFirstTimePrompt=false` + `insufficientAll=false`, default token `sufficient=false`, ≥1 alternative `sufficient=true`. CLI returns Confirming.

```
The default Gas token {prev_token} has insufficient balance (need ${serviceChargeUsd}, current balance ${prev_balance_usd}).
The following stablecoins in your account have enough balance to pay this transaction's Gas:

- {alt_token_1} (balance ${alt_balance_1_usd})
- {alt_token_2} (balance ${alt_balance_2_usd})

How would you like to proceed?
1. Change the default Gas token to {alt_token_X} and use it for this transaction (this chain will default to {alt_token_X} going forward).
2. Use {alt_token_X} for this transaction only; keep the default as {prev_token}.
3. Top up {prev_token} and continue using it.
```

Slots: `{prev_token}` = token at `defaultGasTokenAddress`; `{serviceChargeUsd}` / `{prev_balance_usd}` from the response; `{alt_token_N}` = each `sufficient=true` entry other than the default, in token-priority order; `{alt_token_X}` = the single alternative's symbol if only one, else `<your-pick>`. Always include all three choices and the top-up fallback; no leading/trailing lines.

**Response parsing:**

| User choice | CLI action |
|---|---|
| **1** — alt token + make it default | Re-run original command with `--gas-token-address <alt_addr> --relayer-id <alt_relayer_id>`. After broadcast succeeds, silently `wallet gas-station update-default-token --chain solana --gas-token-address <alt_addr>`. Use "replace default" echo. |
| **2** — alt token this tx only | Re-run with `--gas-token-address <alt_addr> --relayer-id <alt_relayer_id>` only (no `--enable-gas-station`, no `update-default-token`). Use "keep default" echo. |
| **3** — top up default / cancel | Do NOT re-run. Tell user to top up at `{fromAddr}` and retry. |
| Ambiguous / token not in list / didn't say whether to change default | Re-prompt once: ask explicitly whether to change the default (yes → 1, no → 2). Never guess. |

Post-success echo (then append Universal Success Reply):
- keep default: `Done — this transaction will pay Gas with {chosen_token}. The default token remains {prev_token}, unchanged.`
- replace default: `Done — this transaction will pay Gas with {chosen_token}, and the default Gas token is now {chosen_token}.`

## Scene E — All stablecoins insufficient

Backend returns `insufficientAll=true` + all entries `sufficient=false` + `fromAddr`. CLI bails.

```
You don't have enough balance to pay Gas. Please top up first:
  Top-up address: {fromAddr}
  Accepted tokens: SOL, USDT, USDC
```

Do NOT proceed; do NOT propose Gas Station.

## Universal Gas Station Success Reply (all commands)

Whenever any transaction is paid via Gas Station (`wallet send`, `contract-call`, `swap`, `bridge`, any DeFi plugin — detect via `gasStationUsed=true` or a non-empty `serviceCharge` + `serviceChargeSymbol`), the reply MUST contain all four:

1. **Acknowledgment** — state plainly this tx's gas was paid via Gas Station with a stablecoin, not SOL. Never imply "free".
2. **Service charge** — show raw amount + symbol (`{serviceCharge} {serviceChargeSymbol}`) and USD equivalent. E.g. `Network fee: 0.8 USDC (≈ $0.80, paid via Gas Station)`.
3. **orderId** — copy verbatim; never omit or truncate.
4. **Follow-up prompt** — `You can tell me: **check order {orderId}** to check the status.` Translate but keep the literal `check order {orderId}` idiom.

**`networkFeeLabel` rule** (every GS render): when the CLI output carries `networkFeeLabel` (`Network fee` or `Network fee and Rent fee`), that string IS the label — render exactly ONE fee row using it (translate the label). Do not render it as a separate row, do not add a default `Gas fee` title alongside it. Absent → default label `Network fee`.

**When `txHash` is empty** (Relayer returns it asynchronously — usual on first response): also state the tx was submitted and the on-chain hash will come back asynchronously; ask the user to check again shortly. Never fabricate a `txHash`. Never show raw CLI commands to the user.

Example:
```
Sent 100 USDC to CYXWm...

- Network fee: 0.8 USDC (≈ $0.80, paid via Gas Station)
- orderId: ord_ghi789rst
- txHash: submitted, on-chain hash will be returned asynchronously by the Relayer — check again shortly.

You can tell me: **check order ord_ghi789rst** to check the status.
```

Checking later: when the user says any equivalent of "check order {orderId}" (any language), run `wallet history --chain solana --order-id <orderId>` internally (not shown) and relay per troubleshooting Edge Case 5.

## Management Commands

Syntax below; all `--chain solana`. User-facing reply wording follows.

```bash
onchainos wallet gas-station update-default-token --chain solana --gas-token-address <spl_mint>
onchainos wallet gas-station enable  --chain solana
onchainos wallet gas-station disable --chain solana
onchainos wallet gas-station status  --chain solana [--from <solana_address>]
onchainos wallet gas-station setup   --chain solana --gas-token-address <spl_mint> --relayer-id <id> [--from <solana_address>]
```

- `status` — read-only readiness probe (never broadcasts; safe to call repeatedly). Returns `recommendation`: `READY` (proceed) · `ENABLE_GAS_STATION` (render Scene A) · `INSUFFICIENT_ALL` (render Scene E) · `HAS_PENDING_TX` (tell user to wait). Also `gasStationEnabled`, `gasStationDefaultToken`, `tokenList[]` (`symbol`, `feeTokenAddress`, `relayerId`, `balance`, `serviceCharge`, `sufficient`). Used by third-party plugin pre-flight ([plugin-preflight.md](wallet-plugin-preflight.md)).
- `setup` — standalone first-time activation (idempotent; re-calling with the same default returns `alreadyActivated=true`). Only proceeds when the probe state is first-time-eligible.
- Enable / disable / update-default-token are backend DB-flag operations — no on-chain action.

**User-facing reply templates** (translate at output time, semantics must not drift):

Before `disable` (confirmation prompt):
> "Once disabled, transactions on Solana will pay Gas with SOL again. You can re-enable any time. If you only want to switch the Gas-payment token, use 'change default Gas token' instead of disabling. Confirm disabling?"

After any management command succeeds (`enable` / `disable` / `update-default-token`): render `data.message` verbatim (the CLI fills the copy).

## User Intent Recognition

| User intent | Action |
|---|---|
| Wants to send but lacks SOL (any wording/language) | Proceed with `wallet send` — Gas Station activates automatically. |
| Asks whether stablecoins can pay Gas | Explain briefly from troubleshooting FAQ verbatim, then proceed if a tx is given. |
| Any GS FAQ (what / how / fees / supported tokens / non-trigger scenarios / why a small SOL was received) | Answer from troubleshooting FAQ — verbatim (matching Q). |
| Change the default Gas token | `wallet gas-station update-default-token --chain solana --gas-token-address <addr>`. |
| Enable Gas Station | `wallet gas-station enable --chain solana` (use confirmation + success templates). |
| Disable Gas Station / stop paying with stablecoin | `wallet gas-station disable --chain solana`. If they only want to switch token, suggest `update-default-token`. |
| Jito Bundle + stablecoin Gas | Conflicting (hard block) → troubleshooting Edge Case 2. |
| Which tx types are supported | Answer from troubleshooting FAQ (transfers + swaps) — verbatim. |
| Tx blocked: type not supported | Troubleshooting Edge Case 8. Bail — do NOT re-run via GS. |
| Why didn't GS kick in | Check: pending tx? > 100,000 U? Jito Bundle? native SOL? unsupported type? → matching verbatim template. |
| Asks for a not-yet-returned tx hash / why hash is slow | Troubleshooting Edge Case 3. |

## Plugin Bail Recovery

Third-party plugins (`kamino-plugin`, `raydium-plugin`, …) invoke `wallet contract-call` as a subprocess; on a Confirming (exit code 2, `"confirming": true` in stdout) for Scene A / C, the wrapper bails on the non-zero exit. Markers: exit code **2** + stdout JSON with `"confirming": true`.

Recovery: read `scene` from the stdout JSON, dispatch via the Outcome → render map (render copy, get consent where required, run any management command it calls for — e.g. `update-default-token` on a Scene C replace-default pick), then re-invoke the **same plugin command verbatim** (the plugin rebuilds calldata and hits the auto path). `gs_insufficient_all` / `gs_pending_tx` → do NOT retry.

- Always parse the Confirming JSON before deciding it's recoverable; real failures differ.
- Always get user consent for Scene A and Scene C token selection.
- Re-invoke the same plugin command verbatim; the bail is pre-broadcast, so re-running is idempotent — do not hand-rebuild the plugin's calldata.

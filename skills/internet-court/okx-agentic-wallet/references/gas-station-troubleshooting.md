# Gas Station — Troubleshooting (Solana)

Edge cases, FAQ answers, and failure diagnosis for Gas Station. Render every user-facing template per the output-discipline rule in [gas-station.md](gas-station.md) (verbatim, translate at output time, no extras). Never expose internal mechanism terms or error codes.

## Edge Cases

Handle these explicitly — do not fall through to generic error handling.

### 1 — Relayer single-tx cap exceeded (100,000 U)
Backend detects single-tx value > 100,000 USD, silently falls back to normal flow (`gasStationUsed=false`); no GS Confirming. Do NOT proactively mention Gas Station. **Only** when the user directly asks whether stablecoins can pay gas for this tx:
```
This transaction exceeds the Gas Station per-transaction cap (100,000 U), so Gas cannot be paid with a stablecoin. Top up the native token and retry the full transfer, or split it into smaller transactions.
```

### 2 — Jito Bundler HARD BLOCK
Trigger: `--jito-unsigned-tx` supplied, or the user states intent to use Jito Bundle. Gas Station does NOT support Jito Bundler. Even if SOL is insufficient and stablecoin is available, offer the two alternatives — never silently route to Gas Station:
```
Sorry, Gas Station does not support Jito Bundler transactions.

You can continue either way:

- Use Jito Bundle: switch the network fee to the native token (SOL); the Bundle transaction can be sent normally.
- Use stablecoin Gas: switch to a normal transaction (no Jito Bundle).
```

### 3 — txHash before Relayer returns it
Trigger: user asks for the hash but the latest GS broadcast's `txHash` is still empty (`orderId` known).
```
The transaction is being submitted on-chain. Please check again shortly.
```
If they ask why other txs return a hash immediately:
```
This one is paid via Gas Station, so the hash comes back slightly later than for normal transactions.
```
Do NOT fabricate a `txHash` or show raw CLI commands.

### 4 — Pending Gas Station tx blocking
Trigger: `hasPendingTx=true` (CLI `scene: "gs_pending_tx"`).
```
A previous Gas Station transaction is still processing — you can't start a new one yet. Wait for the previous one to finish and retry, or top up SOL and use the native token instead.
(To check the previous one, tell me: **check order {prev_orderId}**)
```
Do NOT auto-retry.

### 5 — Order status query ("check order xxx")
Trigger: user says any equivalent of "check order {orderId}" / "is that last transaction done?" (any language). Run `wallet history --chain solana --order-id {orderId}` internally (not shown), then render one:

**A — completed:**
```
✅ Order {orderId} completed.

- txHash: {txHash}
- Status: success
- Chain: Solana
- {networkFeeLabel}: {network_fee_line}
```
`{networkFeeLabel}` is provided by the CLI (`Network fee` or `Network fee and Rent fee`) — render verbatim (translate the label); do not add a separate rent row. `{network_fee_line}` (first that fits):
1. `serviceChargeSymbol` present: `{serviceCharge_readable} {serviceChargeSymbol} (≈ ${serviceChargeUsd}, paid via Gas Station)` where `{serviceCharge_readable}` = `serviceCharge` ÷ `10^serviceChargeDecimal` (never print the raw integer or field names).
2. only `serviceChargeUsd`: `≈ ${serviceChargeUsd} (paid via Gas Station)`.
3. even that empty: `paid via Gas Station (amount not returned)`.

**B — still processing:**
```
Order {orderId} is still being processed by the Relayer. Please check again shortly — tell me **check order {orderId}** and I'll fetch the latest status.
```

**C — failed / timed out (10-min Relayer TTL):**
```
⚠️ Order {orderId} did not complete.

The transaction was broadcast via Gas Station, but the Relayer did not finalize it on-chain within 10 minutes; it has been marked as failed.

Your funds are untouched — the stablecoin Gas fee was NOT deducted, and the {amount} {tokenSymbol} you tried to send is still in your account.

You can retry now, or top up SOL and pay Gas with the native token instead.
```
Never fabricate `txHash`; never show `wallet history` as a command to the user.

### 6 — Native SOL transfer
Backend returns `gasStationUsed=false` regardless of balance. If asked why: "Gas Station only applies to SPL token transfers and contract interactions. Native SOL transfers do not go through Gas Station."

### 7 — History display rules
When listing/detailing a GS tx in `wallet history`: show the user's intended transfer (not the Relayer's fee-payer address); show the network fee in the stablecoin actually used (not SOL); show the user's `from` address (not the Relayer's).

### 8 — Transaction type not supported
Trigger: `wallet send` / `contract-call` bails with a message containing "Gas Station does not support this transaction type" (deposit / staking, etc.). Only transfers and swaps are eligible; the fee must be paid in SOL. Do NOT retry via GS. Do NOT assert the SOL balance is insufficient — the top-up line is conditional:
```
This transaction type isn't eligible for Gas Station — the network fee must be paid in native SOL.

Gas Station currently supports only transfers and swaps. Other types such as deposits and staking can't pay gas with a stablecoin yet — they must be paid with SOL.

If your SOL balance isn't enough to cover the network fee, top up first, then retry:
  Top-up address: {fromAddr}
```
`{fromAddr}` = the user's Solana address (read from the bail message's "Top up SOL at: ..." or the user's known Solana address).

## FAQ

Output the matching template alone — nothing before or after, only translation. Do NOT layer the "never call Gas Station free" rule onto FAQ answers (that governs successful-broadcast replies).

**What is Gas Station?**
```
Gas Station aggregates third-party services,
  automatically comparing rates and picking the cheapest one to pay Gas for you.
  You can pay with USDT, USDC, or USDG —
  no need to hold SOL or any other native token.
  ──────────────────────────────
  Supported network and tokens: Solana (USDT, USDC, USDG)
  ──────────────────────────────
```

**How does it work under the hood?**
```
[Solana] Gas Station needs no account upgrade or setup.
A third-party service pays the network fee on your behalf,
and the fee is automatically deducted from the stablecoin you choose.
```

**Are there extra fees for enabling it?**
```
[Solana] No. Gas Station on Solana requires no account upgrade;
you can pay Gas with a stablecoin on the very first use.
```

**Does each network need to be upgraded before use?**
```
No. Solana has no setup step;
once Gas Station is enabled it can be used directly.
```

**Which tokens can pay Gas?**
```
USDC, USDT, USDG. By default the token with the highest balance is used;
when balances tie, the order is USDT > USDC > USDG.
You can also pin a specific token as the default Gas token.
```

**Which networks are supported?**
```
Solana only, for now.
```

**Which transaction types are supported?**
```
Gas Station currently lets you pay gas with a stablecoin for two transaction types:
- Transfers
- Swaps
Other types (e.g. deposits, staking) are not supported yet and must pay gas with SOL.
```

**Which scenarios do NOT trigger Gas Station?**
```
- Native SOL transfers (Gas Station only covers SPL token transfers and contract interactions).
- Transaction types other than transfers and swaps (e.g. deposits, staking).
- Transactions sent via Jito Bundle.
- A single transaction value above 100,000 U.
- A previous Gas Station transaction is still being processed.
```

**Why did I receive a small amount of SOL from this transaction?**
Render gate — scoped to Gas Station rent-settlement txs only. Do NOT render on the keyword alone. First: (1) resolve the candidate tx (use the given txHash, else `wallet history --chain solana` and pick the recent SOL-inflow record); (2) fetch detail `wallet history --chain solana --tx-hash <hash>` (or `--order-id <id>`); (3) require BOTH markers: `serviceChargeSymbol` ∈ {USDT, USDC, USDG} AND `networkFeeLabel == "Network fee and Rent fee"`.

Markers present → render verbatim:
```
[Solana] This transaction was settled via Gas Station and involves an account rent (rent):
- Within the same transaction, the Relayer first sends a small amount of SOL to cover the account rent for this transaction.
- Within the same transaction, you repay the Relayer in the stablecoin you selected (covering both the rent and the network fee).
- The small amount of SOL you ended up receiving is the leftover after the rent was paid.
```
Markers absent → do NOT render. Explain from actual tx data: a real swap (e.g. `USDC → SOL` in the asset change) → describe as a normal swap; dusting (1 lamport from unknown address, `txHash` often null) → Solana network noise, ignorable. Do not invent a Gas Station explanation when markers don't match.

## Failure & Backend-Bug Handling

Diagnosis content (not user-facing). Read the CLI `scene` and dispatch via the gas-station.md Outcome → render map; do not re-derive from raw booleans.

**Phase 2 failures (after token pick):**

| Failure | Detect | Response |
|---|---|---|
| Backend rejects token selection | non-2xx, or `gasStationUsed=false` with error | Tell user it failed; ask to retry. Re-run phase 1 to refresh `gasStationTokenList` (balance changed, `relayerId` expired, token unsupported). |
| Invalid `gasTokenAddress` | backend error | Do NOT fabricate. Re-run phase 1; use values from the Confirming `next` field. |
| Simulation failure (`executeResult=false`) | CLI bails `transaction simulation failed: <msg>` | Show `<msg>`; do NOT broadcast. |
| Balance changed between phases | phase 2 returns `insufficientAll` or simulation fails | Re-run phase 1 to refresh the list. |
| `hash` empty on phase 2 | backend bug | Surface backend error; do NOT sign. |
| `signType` ≠ `multiSignerTx` | backend bug | Fatal — CLI can't build the multi-signer tx. Surface error. |

**Broadcast & history bugs (should-not-happen):** network fee shown in SOL instead of the stablecoin used, or `from`/history shows the Relayer address → report as backend bug; do NOT manually convert.

**Management command failures** (`update-default-token` / `enable` / `disable`): show the error message; do NOT retry automatically. Common causes: invalid token address, chain not supported, not logged in.

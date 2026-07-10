# Cross-Chain Bridge — Troubleshooting

Load on a failure, edge case, no-route fallback, or a conceptual "how does it work" question. Never show raw error codes or CLI output to the user — translate every failure into plain language; codes stay in the diagnostic summary only.

## FAQ

| Question | Answer |
|---|---|
| Which bridges / chains are supported? | Decided at runtime — run `cross-chain bridges --from-chain <X> --to-chain <Y>`. No static list. Seen so far: Stargate/LayerZero, Across V3, Relay, Gas.zip, Mayan, ButterSwap. |
| What fees are there? | `crossChainFee` (bridge fee, source token) + source-chain gas; some bridges add `otherNativeFee`. |
| What is a "transit token" / why offered one? | No direct route exists, so the backend routes source→transit→target via an intermediate token (see No-Route Fallback below). |
| Why a receive address sometimes? | Heterogeneous pairs (EVM↔non-EVM) can't infer the destination from the sender. |
| Atomic / refundable? | No atomicity guarantee; `status` exposes no refund/failure sub-state. For stuck transfers, verify on the destination chain / bridge scan page first. |

## No-Route Fallback (empty `routerList` / `action=fallback`)

Normal branches, not errors: the backend auto-probes transit assets and hands you the result — you do NOT run any discovery loop. Both commands surface the same `fallback` object (`quote`: `data[0]` = `{routerList:[], fallback:{...}}`; `execute`: `data` = `{action:"fallback", routerList:[], fallback:{...}}`). Branch on `fallback.outcome`:

**`transit_available`** — `fallback.transitOptions[]` lists bridgeable transit tokens; amounts already account for the source→transit swap and the bridge leg — display directly (format `toTokenAmount` / `minimumReceived` / `crossChainFee` with `toTokenDecimals` like the main table):
```
{fromToken} cannot be bridged directly from {fromChain} to {toChain}. These transit tokens work:

| # | Transit Token  | Est. Receive    | Fee             | Est. Time      |
|---|----------------|-----------------|-----------------|----------------|
| 1 | {transitToken} | {toTokenAmount} | {crossChainFee} | {estimateTime} |

Pick a transit token. Steps:
1. Swap {fromToken} → {transitToken} on {fromChain} (use the swap flow)
2. Bridge {transitToken} from {fromChain} to {toChain}
3. Swap {transitToken} → {targetToken} on {toChain} (use the swap flow) — only when target ≠ transit
```
Let the user pick, then run each leg. The bridge leg is a normal same-token bridge (`--from {transitToken} --to {transitToken}`).

**`no_path`** — no indirect path either. Relay `fallback.message` translated. Optionally suggest a manual two-hop via a common chain (Ethereum / Arbitrum).

**`env_unavailable`** — bridge adapter offline on this environment (empty backend `msg` across all transit probes). Tell the user the route is temporarily unavailable here and to retry later — don't imply the pair is permanently unsupported.

## Error Codes

| Code | Meaning → action |
|---|---|
| 50014 | Required param `{0}` missing → surface which. |
| 50125 | Region restriction / no API access → "Service is not available in your region." |
| 51000 | Param error `{0}` → surface the offending param. |
| 81362 | Backend flagged the broadcast (potential honeypot) → WARN, ask to confirm; only on explicit confirm, retry with `--force`. |
| 82000 | No liquidity / route. Backend `msg` carries the reason; may be empty when adapter offline → surface translated `msg`. quote/execute auto-wrap no-route into `fallback`; empty `msg` across all transits → `env_unavailable`. |
| 82104 | Token not supported → transit-token fallback OR tell user unsupported. |
| 82105 | Chain not supported → "This chain pair isn't currently supported by any bridge." |
| 82106 | Bridge id not supported / wrong → re-run `quote` without `--bridge-id`. |
| 82200 | Address blacklisted → BLOCK; do NOT retry. |
| 82201 | Wallet address format invalid → check; convert EVM to lowercase if mixed-case. |
| 82202 | Receive address invalid (family mismatch) → ask for correct format. |
| 82500 | Calldata build failed (bridge server-side) → retry once; if persistent, escalate. |
| 5000 | System error → retry once; if persistent, surface. |

## Failure Diagnostics

Generate before reporting:
```
Diagnostic Summary:
  fromTxHash:    <source hash or "not yet broadcast">
  approveTxHash: <approve hash or "not needed / not run">
  fromChain:     <chain name (chainIndex)>
  toChain:       <chain name (chainIndex)>
  errorCode:     <API or on-chain error code>
  errorMessage:  <human-readable error>
  tokenPair:     <fromToken symbol> -> <toToken symbol>
  amount:        <amount in UI units>
  bridgeId:      <selected bridge id>
  bridgeName:    <bridge protocol name>
  mevProtection: <on|off>
  walletAddress: <address>
  receiveAddress:<address (if different from wallet)>
  timestamp:     <ISO 8601>
  cliVersion:    <onchainos --version>
```

## Edge Cases

- **Chain pair returns no bridges**: localize with two single-flag queries — `cross-chain bridges --from-chain <X>` (source supported?) then `--to-chain <Y>` (destination reachable?). Suggest a supported chain or two-hop.
- **Approval failed inside `execute`**: the approval/revoke tx didn't confirm — nothing bridged. Check source-chain gas, re-run the same `execute` (re-quotes + re-approves). USDT-pattern tokens auto revoke→approve when `needCancelApprove=true`.
- **Approval wait timed out inside `execute`**: CLI polls per-chain and bails; tx may still be pending. Check `wallet history --tx-hash <approveTxHash>` (or `--order-id <approveOrderId>`; pre-prod often returns empty `approveTxHash`). For EVM stuck txs, submit a 0-value tx with the same nonce to cancel.
- **Execute reverts at swap step after approving**: TEE pre-execution failed (allowance not yet reflected, or price moved). Do NOT add `--force` (it's for 81362, not a TEE revert). Wait 1–3 min for backend allowance state to settle, re-run the same `execute` (re-quotes; the re-run's quote returns `needApprove=false`). If repeated, check on-chain allowance and re-run `quote --check-approve`.
- **fromTxHash not visible on public chain**: possibly the agentic wallet's tx wasn't broadcast. Suggest checking the source explorer; if it genuinely never happened, escalate to OKX support with `fromTxHash` + bridge name + amount.
- **`status` NOT_FOUND**: first 30s expected (not yet indexed); 30s–5min → check source explorer; >5min → likely bridge-side delay, suggest the bridge's scan page, wait up to `estimateTime × 5`; >4h → escalate with `fromTxHash` + `bridgeName`.
- **`status` stuck at PENDING**: `status` reflects the backend's fill-event listener (lags). In flight (normal) → wait up to `estimateTime × 10`, check the bridge scan page. Already filled, listener lagging (abnormal, mainly ACROSS V3) → destination balance already rose by ~`minimumReceived` (`wallet balance --chain <toChain>` or explorer); funds arrived, tell the user with that evidence and stop waiting. No refund/failure sub-state; echoed `bridgeId` can be wrong — trust your own record. Long PENDING with no on-chain fill → escalate.
- **Network error**: retry once; if still failing, generate the diagnostic summary and prompt.

## Status Polling

Interactive chat: do NOT auto-loop — run `status` once per request, report, and if not `SUCCESS` tell the user when to ask again (route's `estimateTime`). If the user explicitly asks for a polling script: exponential backoff (10→20→40→60→60s), stop after `SUCCESS` or `estimateTime × 5`. Two traps: (1) every `status` call needs the full triple `(--tx-hash | --order-id) + --bridge-id + --from-chain` or it returns 50014; (2) in zsh do NOT name the loop variable `status` (read-only) — use `st`.

## Bridge Explorer References

For long-stuck cases, point users to the bridge's own scan page (map `bridgeId` → name → URL via `cross-chain bridges`):
- Stargate / LayerZero: https://layerzeroscan.com/
- ACROSS V3: https://across.to/transactions
- Relay: https://relay.link/transactions
- Gas.zip: https://www.gas.zip/scan

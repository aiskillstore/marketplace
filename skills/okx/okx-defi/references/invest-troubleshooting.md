# Capability: Invest — Troubleshooting

Error codes and failure handling for deposit / withdraw / claim flows. Load the operational flow and parameter schemas separately through the top-level Intent Routing table.

## Error Codes

| Code | Scenario | Handling |
|------|----------|----------|
| 84400 | Parameter null | Check required params — partial exit needs `--amount` or `--ratio` |
| 84021 | Asset syncing | "Position data is syncing, please retry shortly" |
| 84023 | Invalid expectOutputList | CLI auto-constructs from position-detail; retry or pass `--platform-id` |
| 84014 | Balance check failed | Insufficient balance — check with `okx-agentic-wallet` |
| 84018 | Balancing failed | V3 balancing failed — adjust price range or increase slippage |
| 84010 | Token not supported | Check supported tokens via `defi detail` |
| 84001 | Platform not supported | DeFi platform not supported |
| 84016 | Contract execution failed | Check parameters and retry |
| 84019 | Address format mismatch | Address format invalid for this chain |
| 50011 | Rate limit | Wait and retry |

## Common Failure Patterns

- **CLI-generated payload rejected before submission**: if `wallet contract-call` returns `-32602 Invalid params` or a calldata/payload validation error without a txHash, stop and discard the unexecuted `dataList`. Never inspect, edit, re-encode, or resubmit the old `serializedData`. Rerun the documented DeFi preparation flow that produced `dataList` and use only the newly returned transaction fields. If a txHash was returned, this recovery rule does not apply; use the wallet transaction-status flow instead.
- **Calldata generated but broadcast fails on-chain**: the position changed between `position-detail` and the write call (another withdraw/claim landed first). Re-run `defi position-detail` and regenerate — never reuse stale calldata.
- **Solana calldata expired**: base58 VersionedTransaction blockhash expires in ~60 s. If signing took too long, regenerate the calldata; do not retry the expired payload.
- **`--amount` rejected**: amount must be an integer in minimal units (userAmount × 10^tokenPrecision). A decimal or UI-unit value triggers parameter errors (84400).
- **Rate limit (50011)**: wait 1–2 s and retry once; if it persists, tell the user the service is rate-limiting.

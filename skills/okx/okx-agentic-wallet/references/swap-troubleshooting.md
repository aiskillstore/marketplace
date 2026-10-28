# DEX Swap — Troubleshooting

## Recovery

### Error Retry (after `swap execute` returns an error)

**Chain not support (`81104`) — evaluate FIRST, before every rule below.** On code `81104`: display the fixed reminder "⚠️ This chain does not currently support swap. Please try a different chain." and stop.

Otherwise, the error may be caused by a preceding approval tx not yet confirmed on-chain:

1. **Wait** by chain block time before retrying: Ethereum ~15s · BSC ~5s · Arbitrum / Base ~3s · XLayer ~3s · other EVM ~10s.
2. **Inform the user**, e.g. "Swap failed, possibly due to a pending approval — waiting for on-chain confirmation before retrying."
3. **Non-recoverable (82000, 51006)**: token is dead / rugged / no liquidity — retrying may not help. Do NOT retry after 5 consecutive errors for the same `(wallet, fromToken, toToken)`. Run `token advanced-info`; warn if `devRugPullTokenCount > 0` or `tokenTags` contains `lowLiquidity`.
4. **Risk warning (81362)**: backend flagged the broadcast as potentially dangerous (possible honeypot / poisoned contract). Do NOT auto-retry. Explicitly warn the user that forcing execution may cause fund loss; only if they confirm, re-run the **same** `swap execute` with `--force` (passes `skipWarning: true`). Never add `--force` without explicit confirmation.
5. **All other errors**: retry once; if it fails again, surface the error.

## Failure Diagnostics

When a swap fails (broadcast error, on-chain revert, or timeout), produce a diagnostic summary before reporting:

```
Diagnostic Summary:
  txHash:        <hash or "simulation failed">
  chain:         <chain name (chainIndex)>
  errorCode:     <API or on-chain error code>
  errorMessage:  <human-readable error>
  tokenPair:     <fromToken symbol> → <toToken symbol>
  amount:        <amount in UI units>
  slippage:      <value used, or "auto">
  mevProtection: <on|off>
  walletAddress: <address>
  timestamp:     <ISO 8601>
  cliVersion:    <onchainos --version>
```

### Edge Cases

- **Insufficient balance**: route the insufficient-balance intent to [funding.md](funding.md).
- **Network error**: retry once, then produce the diagnostic summary and prompt the user.
- **Region restriction (error code 50125 or 80001)**: do NOT show the raw code. Display: "⚠️ Service is not available in your region. Please switch to a supported region and try again."

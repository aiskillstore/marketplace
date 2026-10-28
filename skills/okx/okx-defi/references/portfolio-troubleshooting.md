# Capability: Portfolio — Troubleshooting

Error handling and edge cases for position viewing. Load the operational flow and parameter schemas separately through the top-level Intent Routing table.

## Common Errors

| Code | Scenario | Handling |
|------|----------|----------|
| 84019 | Address format mismatch | The `--address` and chain params are incompatible (EVM `0x…` vs Solana base58 vs Sui/Tron/TON) — apply the top-level Address-Chain Compatibility rule and split EVM and Solana into two separate calls |
| 84021 | Asset syncing | "Position data is syncing, please retry shortly" |
| 50011 | Rate limit | Wait 1–2 s and retry once |

## Edge Cases

- **`--chains` vs `--chain` confusion**: `defi positions` takes `--chains` (plural, comma-separated); `defi position-detail` takes `--chain` (singular). Passing the wrong one is a parameter error, not an empty result.
- **Empty positions but the user insists they have holdings**: check the address/chain pairing first (84019 class of mistake), then whether the protocol is supported (`defi support-platforms`). Positions on unsupported platforms will not appear.
- **`position-detail` output shape**: `data` is an **array** — iterate it; calling `.get()` on it directly is a client-side bug, not an API error.
- **Missing `--platform-id`**: `position-detail` requires `analysisPlatformId` from a prior `defi positions` call — run that first.

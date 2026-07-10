# Wallet — Troubleshooting

Load on a wallet operation failure or edge case.

## Send
- **Insufficient balance**: check balance first; warn if too low (include gas estimate for EVM).
- **Wrong chain for token**: `--contract-token` must exist on the specified chain.

## History
- **No transactions**: display "No transactions found" — not an error.
- **Detail mode without chain**: `--chain` is required with `--tx-hash` / `--order-id` / `--uop-hash`. Ask which chain.
- **Empty cursor**: no more pages.

## Contract Call
- **Neither `--input-data` nor `--unsigned-tx`**: exactly one is required; the command fails otherwise.
- **Invalid calldata**: malformed hex causes an API error — help re-encode.
- **Simulation failure**: show `executeErrorMsg`, do NOT broadcast.
- **Insufficient gas**: suggest a higher `--gas-limit`.

## Common
- **Region restriction (error code 50125 or 80001)**: do NOT show the raw code. Display: "Service is not available in your region. Please switch to a supported region and try again."
- **Not logged in** (`not logged in`): session expired or store missing. Tell the user to run `wallet login` + `wallet verify`.
- **Confirming response (exit code 2, error code 81362)**: not an error — the backend needs confirmation. Handle via SKILL.md → Confirming Response.

# Preflight

Run `spunk preflight` at the start of a session and again whenever `baw` returns a policy / risk / blocked
error. It never spends gas.

```bash
spunk preflight --json
```

It checks, via `baw` and an on-chain read:

- wallet connected (`baw wallet status`)
- Developer Mode on (`baw wallet settings`) — needed for any contract call
- a `.ai` Agent ID is held on BNB Chain — needed to mint
- how many punks the wallet already holds (0–5)

Expected ready state: `status: READY`, `issues: []`.

```json
{
  "success": true,
  "status": "READY",
  "address": "0x…",
  "isAgent": true,
  "devMode": true,
  "owned": 1,
  "slotsLeft": 4,
  "issues": []
}
```

Relay each `issues[].fix` to the user verbatim. The two that commonly block are **Developer Mode**
(enable in the Binance App) and a missing **Agent ID** (claim it from the Agent ID banner in Binance Wallet).

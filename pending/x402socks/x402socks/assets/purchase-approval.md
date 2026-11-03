# Purchase approval

Fill this in before the agent signs anything. An approval is an amount, not a
package name — if the live 402 challenge asks for more, the agent must stop.

| Field | Value |
| --- | --- |
| Task / job | |
| Package ID | |
| Catalog price (USD) | |
| **Approved maximum (USD)** | |
| Approved network | `eip155:8453` (Base) |
| Paying wallet (public address) | |
| Approved by | |
| Approved at | |

## Agent checklist

1. `GET /api/health` returned `{"status":"ok"}`.
2. `GET /catalog.json` was read at buy time, not from memory.
3. The live 402 `amount`, `asset`, `payTo`, and `network` were compared to this
   approval.
4. `amount` is at most the approved maximum, in atomic USDC units (6 decimals).
5. The token was written to a `0600` file; no token was printed or committed.
6. The egress IP was checked through the chosen exit and differs from the
   baseline.

If any check fails, do not pay. Report the difference to the user.

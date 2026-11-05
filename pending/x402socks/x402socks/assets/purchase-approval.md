# Purchase approval

Fill this in before the agent signs anything. An approval is the full set of
payment terms, not just an amount and not a package name — if the live 402
challenge differs from any field below, the agent must stop.

| Field | Value |
| --- | --- |
| Task / job | |
| Package ID | |
| Catalog price (USD) | |
| **Approved maximum (USD)** | |
| Approved maximum (atomic USDC, 6 decimals) | |
| Approved scheme | `exact` |
| Approved network | `eip155:8453` (Base) |
| Approved asset contract | |
| Approved recipient (`payTo`) | |
| Approved asset domain (`extra.name`, `extra.version`) | |
| Paying wallet (public address) | |
| Approved by | |
| Approved at | |

Run `scripts/x402socks.sh quote <package_id>` and copy `network`, `asset`,
`pay_to`, `asset_name`, `asset_version`, and `amount_atomic` from its output.
Those values come from the live challenge before any signer exists; the purchase
must then prove the challenge it is about to sign still matches them.

## Agent checklist

1. `GET /api/health` returned `{"status":"ok"}`.
2. `GET /catalog.json` was read at buy time, not from memory.
3. `quote` was run and its terms were recorded above.
4. **Every** entry in the live 402 `accepts[]` was compared to this approval:
   `scheme`, `network`, `asset`, `payTo`, `extra.name`, `extra.version`, and
   `amount`. Any mismatch — or more than one distinct option — stops the
   purchase.
5. The signer is bound to the single validated requirement, not to a wildcard
   network such as `eip155:*`.
6. `amount` is at most the approved maximum, in atomic USDC units (6 decimals).
7. The token was written to a `0600` file; no token was printed or committed.
8. The egress IP was checked through the chosen exit and differs from the
   baseline.

If any check fails, do not pay. Report the difference to the user.

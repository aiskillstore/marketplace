# Purchase approval

Fill this in before the agent signs anything. An approval is the full set of
payment terms, not just an amount and not a package name. If the live 402
challenge differs from any field below, the agent must stop.

| Field | Value |
| --- | --- |
| Task / job | |
| Package ID | |
| Catalog price (USD) | |
| **Approved exact amount (USD)** | |
| Approved exact amount (atomic USDC, 6 decimals) | |
| Approved scheme | `exact` |
| Approved network | `eip155:8453` (Base) |
| Approved asset contract | |
| Approved recipient (`payTo`) | |
| Approved asset domain (`extra.name`, `extra.version`) | |
| Paying wallet (public address) | |
| Signer (keystore / hardware wallet; never a pasted key) | |
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
4. The live 402 `accepts[]` had **exactly one** entry, and it matched this
   approval field for field: `scheme`, `network`, `asset`, `payTo`,
   `extra.name`, `extra.version`, and `amount`. Any mismatch, a different
   amount, or more than one option stops the purchase.
5. The signer is bound to the single validated requirement, not to a wildcard
   network such as `eip155:*`.
6. `amount` equals the approved exact amount, in atomic USDC units (6 decimals).
7. The token was written to a `0600` file; no token was printed or committed.
8. The signer was a keystore or hardware wallet; no private key appeared in argv,
   a log, or a transcript.
9. The egress IP was checked through the chosen exit and differs from the
   baseline.

If any check fails, do not pay. Report the difference to the user.

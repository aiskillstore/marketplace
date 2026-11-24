# Purchase approval

Fill this in before the agent signs anything. An approval binds one job to one
package, one request URL, one signer, and one exact live term set. It is not just
an amount and not a reusable budget. If the live 402 challenge differs from any
field below, the agent must stop and ask again.

| Field | Value |
| --- | --- |
| Task / job | |
| Authorized target hosts (`X402SOCKS_ALLOWED_HOSTS`) | |
| Exact request URL | |
| Package ID | |
| Expected `resource.url` | |
| Expected `resource.description` (entitlements) | |
| Expected `resource.serviceName` | |
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
Copy `resource.url`, `resource.description`, and `serviceName` from the live 402
challenge. Those values come from the challenge before any signer exists; the
purchase must then prove the challenge it is about to sign still matches them.
Never fill this template from a previous purchase.

## Agent checklist

1. `GET /api/health` returned `{"status":"ok"}`.
2. `GET /catalog.json` was read at buy time, not from memory.
3. `quote` returned HTTP 402 with exactly one option, and its terms were
   recorded above.
4. The live 402 request URL, `resource.url`, `resource.description`, and
   `serviceName` match this approval exactly.
5. The live 402 `accepts[]` had **exactly one** entry, and it matched this
   approval field for field: `scheme`, `network`, `asset`, `payTo`,
   `extra.name`, `extra.version`, and `amount`. Any mismatch, a different
   amount, or more than one option stops the purchase.
6. The signer is bound to the single validated requirement and public address,
   not to a wildcard network such as `eip155:*`.
7. `amount` equals the approved exact amount, in atomic USDC units (6 decimals).
8. The token was written to a `0600` file; no token or raw provider response was
   printed or committed.
9. The signer was a keystore or hardware wallet; no private key appeared in argv,
   a log, or a transcript.
10. The egress IP was checked through the chosen exit and differs from the
    baseline.

## Reconciliation, single use, and retries

This approval covers **one** signed authorization. It must be reconciled and
consumed, not merely matched.

1. **Reconcile before claiming.** Run `scripts/x402socks.sh status` (or
   `validate`) and check for a saved settlement tx hash. If a valid token already
   exists, the job is paid: reuse it and do not claim this approval.
2. **Consume before signing.** Create `<approval-file>.consumed` with exclusive
   creation and mode `0600` (`open(path, "wx", 0o600)` in Node, or
   `os.open(path, O_WRONLY | O_CREAT | O_EXCL, 0o600)` in Python). If the marker
   already exists, the approval was used: ask for a fresh decision.
3. **Retire the record.** After the purchase, rename or delete the approval file
   so it cannot be presented again. Keep the settlement tx hash for recovery.

The x402 protocol retry that sends that authorization to the same request URL is
part of the same purchase. A later 402, a 502, an unknown settlement state, a
token recovery, or a request for a second package all require a new explicit
approval decision and a fresh approval record. Reconcile the first authorization
and record its outcome before asking. Never re-sign from a stale or consumed
approval. An approval that was consumed but did not complete is burned: reconcile
the chain and account, then ask for a new explicit approval.

# x402 `period` subscription (a.k.a. `permit2_subscription`) — buyer side

> Loaded from `../SKILL.md` **only when** a 402 `accepts[]` entry has `scheme == "period"`, or the user asks to manage an existing subscription (access / change / cancel). Skip on one-shot `exact` / `aggr_deferred` / `upto` offers.

The `period` scheme is recurring (subscription) billing. The buyer **subscribes once** — signing a Permit2 `PermitSingle` (delegating a bounded allowance to the subscription contract) plus a `SubscriptionTerms` EIP-712 authorization — and thereafter serves the protected resource by attaching a lightweight `APP-Access` proof header **without re-paying**. The buyer self-manages the lifecycle: upgrade/downgrade (`change`), teardown (`cancel`), revoke a scheduled downgrade (`cancel-pending`), and inspect state (`my-subscriptions`, `allowance-status`). **Every command signs or reads only — none broadcasts a transaction or moves funds** (on-chain execution is seller/facilitator-side, bounded by the Permit2 `permit.amount` / `permit.expiration` the buyer signs). All commands print the standard `{ "ok": …, "data"/"error": … }` JSON envelope; exit `0` (success) / `1` (error) only — there is no `confirming` gate.

## Decide operation
| Situation | Command |
|---|---|
| New `period` 402 offer, no active sub for this host | `payment subscription subscribe --accepts '<json>' --url <url>` |
| Resource already has an active sub (check `my-subscriptions` first) | `payment subscription access --url <url>` — **never re-subscribe** |
| Change-offer 402 (`extra.changeFrom`), upgrade/downgrade | `payment subscription access` (proof) → proof-carrying probe → `payment subscription change --accepts '<json>' --sub-id <cur>` (see `change` — never probe naked) |
| Cancel an active sub | `payment subscription cancel --sub-id <s> --contract <c>` |
| Revoke a scheduled (not-yet-effective) downgrade | `payment subscription cancel-pending --sub-id <s> --new-sub-id <n> --contract <c>` |
| Inspect state / reconcile cache | `payment subscription my-subscriptions` · `payment subscription allowance-status --token <t>` |

## Pre-flight: allowance check (before subscribe / change)
`subscribe` and `change` read `allowance-status` **immediately before signing** (to obtain a fresh `nonce` / `reservedAmount` / `permit2Allowance`; the CLI does this for you). The signed Permit2 must satisfy `permit.amount ≥ reservedAmount + this-subscription-total-commitment`, and `permit.expiration` must cover the whole service window (`fixed_seconds`: `startAt + maxPeriods × periodSec`; `calendar_month`: `addMonths(effective_start, maxPeriods)`). If `allowance-status` shows an insufficient `permit2Allowance` (first payment for that token, or a grown window), the command errors with `allowance_expired` guidance — run the **one-time `ERC20 → Permit2 approve`** via the existing approve flow (NOT a subscription verb), then retry.

## Interpreting the result
| Command | How to read the result |
|---|---|
| subscribe / change | replay `.data.paymentHeaderValue` under header `.data.paymentHeaderName` (`PAYMENT-SIGNATURE`); persist `.data.subId` (the CLI also caches host→subId) |
| subscribe / change | on `… contract mismatch` in `.error`, treat as a hard security abort (exit 1) — the seller-declared contract did not match the authoritative `allowance-status`; do not retry or force |
| access | replay `.data.accessHeaderValue` under `APP-Access`; `.data.source` (`cache` \| `override`) tells you whether the subId came from the local cache or `--sub-id` |
| cancel / cancel-pending | relay the `.data.cancelAuth` / `.data.pendingChangeCancelAuth` object to the seller; the sub stays active/billable until the contract executes — the local cache is NOT flipped to canceled |
| my-subscriptions | `.data.subscriptions[]` — each item's `state` is `0` pending / `1` active / `2` completed / `3` canceled / `4` changed / `99` failed; the local cache is reconciled from this authoritative state |
| allowance-status | all 10 fields (`approvedAmount`, `reservedAmount`, `permit2Allowance`, `subscriptionContract`, …) always present |

## CLI Reference

```bash
onchainos payment subscription subscribe        --accepts '<json>' [--from <addr>] [--url <url>]
onchainos payment subscription access           --url <url> [--sub-id <id>] [--from <addr>] [--chain <name|index>]
onchainos payment subscription change           --accepts '<json>' --sub-id <id> [--from <addr>] [--url <url>]
onchainos payment subscription cancel           --sub-id <id> [--contract <addr>] [--token <addr>] [--chain <name|index>] [--from <addr>]
onchainos payment subscription cancel-pending   --sub-id <id> --new-sub-id <id> [--contract <addr>] [--token <addr>] [--chain <name|index>] [--from <addr>]
onchainos payment subscription my-subscriptions [--chain <name|index>] [--from <addr>] [--limit <n>] [--offset <n>]
onchainos payment subscription allowance-status --token <addr> [--chain <name|index>] [--from <addr>]
```

### `subscribe`
| Param | Required | Description |
|---|---|---|
| `--accepts` | yes | the 402 `accepts` array or single object (JSON); must contain a `period` entry |
| `--from` | no | payer address; default = selected account |
| `--url` | no | protected-resource URL; used as `resource.url` and the cache-key host |

### `access`
| Param | Required | Description |
|---|---|---|
| `--url` | yes | protected-resource URL; its host is the cache key |
| `--sub-id` | no | override the active subId (skips the cache); `source` becomes `override` |
| `--from` | no | payer address; default = selected account |
| `--chain` | no | chain name or index (default `xlayer` / `196`); resolved via `chains::resolve_chain` |

### `change`
| Param | Required | Description |
|---|---|---|
| `--accepts` | yes | change-offer accepts (JSON) carrying `extra.changeFrom` |
| `--sub-id` | yes | the subId being changed (from `my-subscriptions`, matched by host); overrides `extra.changeFrom.fromSubId` |
| `--from` | no | payer address; default = selected account |
| `--url` | no | cache key for the resulting subscription |

**Pre-flight probe (upgrade/downgrade) — carry an `APP-Access` proof, do NOT probe naked.** The change endpoint only returns a full change-offer with `extra.changeFrom` (the `direction` + `fromSubId` of the current subscription) when the probing request proves ownership of the current subscription. A **naked probe** (no proof) returns an offer **missing** `extra.changeFrom`, which fails `change` signing (`change` requires `--accepts` to carry `extra.changeFrom`) and forces a wasteful re-probe with the proof — one extra LLM round-trip + one extra CLI call. Always probe with the proof attached from the start:
1. `payment subscription access --url <change endpoint>` — generates the current subscription's `APP-Access` proof (replay `.data.accessHeaderValue` under the `APP-Access` header).
2. Probe the change endpoint **with that `APP-Access` header attached** → the 402 returns the change-offer carrying `extra.changeFrom` (matching `direction` / `fromSubId`) in a single probe.
3. `payment subscription change --accepts '<that offer>' --sub-id <cur>` → sign.

Required sequence: `access` (proof) → one proof-carrying probe of the change endpoint → `change`. Never do `naked probe → missing changeFrom → re-probe`.

### `cancel`
| Param | Required | Description |
|---|---|---|
| `--sub-id` | yes | the subscription to cancel |
| `--contract` | no | subscription-contract EIP-712 verifying-domain address |
| `--token` | no | used to look up `--contract` via `allowance-status` when `--contract` omitted |
| `--chain` | no | chain name or index (default `xlayer` / `196`) |
| `--from` | no | payer address; default = selected account |

### `cancel-pending`
| Param | Required | Description |
|---|---|---|
| `--sub-id` | yes | the active subscription |
| `--new-sub-id` | yes | the PENDING downgrade's `newSubId` (from `my-subscriptions` → `pendingPlanChange.newSubId`); signed into the auth and must equal the on-chain pending value |
| `--contract` | no | verifying contract (as in `cancel`) |
| `--token` | no | used to look up `--contract` when omitted |
| `--chain` | no | chain name or index (default `xlayer` / `196`) |
| `--from` | no | payer address; default = selected account |

### `my-subscriptions`
| Param | Required | Description |
|---|---|---|
| `--chain` | no | chain name or index (default `xlayer` / `196`) |
| `--from` | no | buyer address; default = selected account |
| `--limit` | no | page size (default `50`) |
| `--offset` | no | page offset (default `0`) |

### `allowance-status`
| Param | Required | Description |
|---|---|---|
| `--token` | yes | token contract address |
| `--chain` | no | chain name or index (default `xlayer` / `196`) |
| `--from` | no | buyer address; default = selected account |

## Edge cases
- `access` with no cached sub + no `--sub-id` → the error names the host; run `my-subscriptions` to reconcile the cache, or pass `--sub-id`.
- `permit2Allowance` insufficient / `allowance_expired` → do the one-time `ERC20 → Permit2 approve` via the existing approve flow, then retry.
- `subscription contract mismatch` / `permit2 contract mismatch` → **fail-closed security stop, not a transient error.** Before signing, `subscribe`/`change` cross-check the seller's `extra.contracts.subscription` / `extra.contracts.permit2` against the authoritative `allowance-status` values; on any mismatch — or a missing authoritative value — the command emits `{"ok": false, "error": "… contract mismatch: …"}` and exits `1` **before** any signature or approve. This is intentional (a tampered contract address). Do **NOT** retry, re-probe, or attempt to force it — abort and surface the mismatch to the user. There is no `--force` bypass (it is never a `confirming` gate).
- `fixed_seconds` needs `periodSec > 0`; `calendar_month` needs `periodSec == 0` — an inconsistency errors out.
- `cancel` does NOT stop billing locally — the sub stays active until the contract executes; `my-subscriptions` reconcile corrects the local cache later.
- `cancel-pending` requires `--new-sub-id`, which must equal the on-chain pending `newSubId`.
- `period` is EVM-only (Permit2 / EIP-712 / EIP-191); Solana (`501`) and other non-EVM chains are out of scope for this scheme.

## Security
- **TEE-only signing** — signatures are always produced by the logged-in wallet's TEE path; no plaintext key/mnemonic ever appears in code, logs, or output. The CLI never accepts a private key or a hand-crafted signature.
- **Contract addresses verified against a trusted root** — before signing, `subscribe`/`change` cross-check the seller's `extra.contracts.subscription` / `extra.contracts.permit2` against the authoritative buyer-direct `allowance-status` (`subscriptionContract` / `permit2Contract`). Comparison is EVM checksum-insensitive; an empty/absent authoritative value fails closed (reject). On a match, the **authoritative** values are used as the Permit2 `spender`, the EIP-712 `verifyingContract`s, and the Layer-1 `approve` target — so a signed subscription is always anchored to the authoritative source, never an unverified seller declaration. (`cancel`/`cancel-pending` resolve the subscription contract from `allowance-status` when called with `--token`, or use the caller-supplied `--contract` verbatim (no cross-check) — acceptable because a `CancelAuth` / `PendingChangeCancelAuth` carries no transfer authority.)
- **Bounded commitment** — the financial exposure is capped by the signed Permit2 `permit.amount` / `permit.expiration`; the pre-sign allowance check enforces the bound.
- **Never re-subscribe** an already-active resource — `access` or `change` it instead.

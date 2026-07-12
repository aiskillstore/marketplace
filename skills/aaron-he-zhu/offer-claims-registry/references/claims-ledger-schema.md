# Claims Projection Contract

The canonical claims/offers history is `memory/events/claims.ndjson`; current accepted state is `memory/projections/claims.json`. `claims-ledger.md` and `offers.md` are generated human views, not writable ledgers.

## Claim Fields

| Field | Required | Meaning |
|---|---|---|
| `kind` | yes | `claim` |
| `exact_wording` | yes | Verbatim approved or proposed wording |
| `interpretation` | yes | Measurable meaning and denominator |
| `status` | yes | `unresolved`, `approved`, `expired`, `withdrawn` |
| `evidence_type` | yes | measured/user-provided/calculated/estimated/proxy |
| `evidence_ref` / `evidence_date` | yes for approval | Named source and observation date |
| `scope` | yes | Population, product/version, market, channel/media, and time window |
| `approved_variants` | when approved | Wording variants within the same evidence scope |
| `required_disclosure` | conditional | Claim-level qualifier/disclaimer |
| `used_in` | recommended | Artifact/URL pointers, not copied content |
| `review_at` / `expires_at` | conditional | Revalidation or offer expiry |

`user-provided` is evidence provenance, not independent verification. `unresolved` is a registry fact, not an auditor verdict. A builder may use only accepted wording whose scope matches the current use.

## Offer Fields

| Field | Required | Meaning |
|---|---|---|
| `kind` | yes | `offer` |
| `terms` | yes | Exact price/discount/eligibility/guarantee terms |
| `code` | conditional | Promotion code |
| `starts_at` / `ends_at` | yes | ISO timestamps or dates |
| `destination_ref` | yes | Accepted destination |
| `status` | yes | `upcoming`, `live`, `ended`, `withdrawn` |
| `linked_claim_ids` | recommended | Claims dependent on these terms |

Expiry is a new owner event. Never delete or rewrite the original approval event.

## Producer Proposal

Ordinary skills do not write Markdown or NDJSON directly. With explicit permission, they pass a schema-valid request to `registry-events.py`:

```json
{
  "schema_version": "1.0",
  "idempotency_key": "claim-proposal-asset-v3-c14",
  "aggregate_id": "claim-c14",
  "operation": "propose",
  "proposed_operation": "upsert",
  "occurred_at": "2026-07-10T10:00:00Z",
  "actor": {"type": "skill", "id": "ad-creative-builder"},
  "authorized_by": "user",
  "authorization_ref": "current-save-request",
  "source": {"type": "user-provided", "ref": "asset-v3", "observed_at": "2026-07-10"},
  "expected_revision": 0,
  "payload": {"set": {"kind": "claim", "exact_wording": "[needs source]", "status": "unresolved"}}
}
```

The host-capability owner accepts/rejects by proposal event ID. The decision request omits `expected_revision`; acceptance inherits and checks the revision captured by the proposal. Resolution retains both events.

## Consumer Rules

- Auditors read accepted projection state plus concrete rendered use; missing evidence is Unknown unless failure is positively verified.
- Builders read accepted wording/scope/disclosure and keep unmatched wording `[needs source]` plus a proposal.
- Narrative stores claim IDs and projection offset; it does not copy unsupported claim truth.
- Human views include projection offset/revision and are regenerated, never manually curated.

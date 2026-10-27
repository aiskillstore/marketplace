# Report input

Use UTF-8 JSON with this shape:

```json
{
  "schemaVersion": 1,
  "currency": "USD",
  "language": "en",
  "coverage": {"start": "2024-01-01", "end": "2024-03-31"},
  "transactions": [
    {
      "id": "example-1",
      "date": "2024-01-05",
      "description": "Fictional market",
      "amount": "-42.50",
      "kind": "expense",
      "group": "daily",
      "category": "Groceries",
      "account": "Account A",
      "source": "Statement A, row 1",
      "share": 1
    }
  ],
  "refunds": [],
  "settlements": [],
  "notes": [],
  "demo": false
}
```

The example is invented. Never put real inputs in the installed skill or its Git checkout.

## Fields and accounting

These fields encode the prepared report; they do not prove that a transaction is understood. Follow the [confirmation step](workflow.md#confirm-uncertain-transactions) before final charts. Conservative `transfer_in` / `transfer_out` defaults, `other`, or missing categories do not remove the obligation to ask about unresolved records.

- `coverage` describes confirmed source coverage, not the earliest/latest transaction. Gaps must be described in `notes`; do not label a period complete without evidence.
- Dates are ISO calendar dates, not timestamps. Currency is a single three-letter code. Version 1 accepts currencies with two decimal places only; separate different currencies and do not invent exchange rates.
- Amount is a decimal string with at most two fractional digits. Positive is money received, negative is money paid. Zero records are allowed only as `internal` informational records.
- IDs must be unique. Do not silently discard same-date/same-amount payments. Deduplicate only established duplicate evidence before constructing this input.
- `kind` is `expense`, `income`, `refund`, `transfer_in`, `transfer_out`, or `internal`. Unknown incoming payments are `transfer_in`, not income. Uncertain outgoing payments are `transfer_out` until their purpose is confirmed.
- Income, refund and transfer-in amounts must be positive. Expense and transfer-out amounts must be negative. Internal entries allow either sign and are omitted from external cash movement.
- `group` is `daily`, `fixed`, `ai`, `housing`, `education`, `equipment`, or `other`. It applies to expenses. Do not infer an AI subscription from ordinary software.
- Optional `incomeType` is `salary`, `support` or `other` (default). Use a confirmed classification, not an inference from the sender. It selects the secondary income rings.
- Optional `purpose` is `loan`, `reimbursement` or `other` (default). Only explicit `loan` transfers contribute to confirmed loan metrics. Settlement rules still apply to all confirmed allocations.
- Optional `merchant` groups descriptions from the same confirmed merchant; when absent, the report uses `description` for merchant rings.
- `category`, `description`, `merchant`, `account` and `source` are plain text. Use account aliases, not account numbers. Source references should identify a private original without embedding its contents or absolute filesystem path.
- `share` defaults to 1 and is between 0 and 1, with up to four decimal places. Apply only a user-confirmed personal share to expenses. Bank amounts remain unchanged. Calculation retains fractional cents; display rounds once.
- Optional `bankStatus` is `posted` (default) or `pending`. Use `pending` only for an expense that the user has confirmed as a real purchase while the bank still shows it as pending. It counts toward personal spending and the daily allowance, but not toward bank-date cash movement until it posts. Keep one record per purchase: when the posted record arrives, replace the pending one only after matching them on clear evidence such as account, amount and description. Ask before applying a changed amount or treating the purchase as cancelled; a pending record that is missing from a later export is not cancelled by that alone. Leave out pending records the user has not confirmed.
- `notes` is a list of plain-text limitations, definitions and source coverage notes.

## Refunds

Each confirmed *full* refund mapping is:

```json
{"purchaseId": "purchase-1", "refundIds": ["refund-1"]}
```

The purchase must be an expense and refunds must be refund records. Their raw amounts must exactly offset in the report currency. Each purchase and each refund may occur in only one mapping. Both sides are removed from the personal-spending view, including across months; bank-date cash movement still includes them. A partial or unpaired refund stays separate and does not reduce spending automatically. Foreign-currency full returns with a local-currency difference need explicit analysis outside this matching shortcut; never force equality.

## Loans and reimbursements

Confirmed transfer settlements use:

```json
{"outId": "loan-1", "inId": "repayment-1", "amount": "25.00"}
```

Both endpoints must be external transfer records with opposite signs. The allocation cannot exceed either record, including prior allocations. Each allocation removes that amount from the original outgoing and incoming transfer in the adjusted transfer/cash views; original dates and amounts remain visible. A partial repayment leaves the outstanding amount on the original outgoing date. Matching names, dates or amounts alone is not confirmation.

## CSV

The CLI also accepts CSV with headers:

```csv
id,date,description,amount,kind,group,category,account,source,share
example-1,2024-01-05,Fictional market,-42.50,expense,daily,Groceries,Account A,Statement A row 1,1
```

Supply `--currency`, `--start`, `--end` and optionally `--language`. CSV has no refund or settlement mappings; use JSON for those. A bank export usually needs an explicit column/sign/date mapping first. Never guess ambiguous day/month order.

## JavaScript API

`Finance.validate(input)` returns normalized data (adding `amountCents`, `bankStatus` and default text fields) or throws a safe error without echoing financial values.

`Finance.periods(data, grain)` returns ascending `{key, label, start, end}` periods clipped to coverage; grain is `day`, `week`, `month`, or `year`. Weeks start on Monday.

`Finance.summarize(data, period)` returns:

- `inflow`, `outflow`, `net`, `spending`, `daily`, `dailyAverage`, `income`, `transferIn`, `transferOut`, `unpairedRefunds`: amounts in cents (personal amounts can have fractional cents).
- `groups`: group-to-personal-spending-cents map.
- `rows`: all period rows with `bankStatus`, `personalCents`, `cashCents` (signed adjusted external amount; zero for internal and pending records), `transferCents` (signed adjusted transfer), `matchedRefund` and `settledCents`.
- `days`: inclusive covered calendar days.

The same pure module runs in the browser and Node tests. All rendering must insert untrusted text with DOM text nodes, never HTML interpolation.


## Optional merchant display names

JSON input may include `merchantDisplayNames`, an object mapping an exact original merchant string to a concise display label of 1–80 characters. This is optional presentation metadata; it does not alter transaction identities, merchant grouping, category, amounts, dates, shares or matches. Different original strings remain separate even when their display labels are identical. Search supports both labels and originals; full merchant and bank descriptions remain in transaction details and full labels are available on legend hover.

Use concise labels only where the provided merchant name or existing user evidence makes the identity clear. Remove redundant location/payment formatting from a known name, but do not infer an unknown legal entity's business or assign a category. Keep an ambiguous name unchanged. Do not automatically add real merchant mappings to the public Skill or its examples. Omitted, empty, overlong or non-string mapping values fall back to the original display text.


## Optional daily allowance settings

The following configuration is fictional. Add `budget` only when the user requests budgeting:

```json
{
  "budget": {
    "endpoint": null,
    "defaults": {
      "schemaVersion": 1,
      "dailyLimit": "40.00",
      "currency": "USD",
      "timezone": "UTC",
      "groups": ["daily", "fixed", "ai"],
      "allocationMode": "history",
      "shares": []
    }
  }
}
```

`dailyLimit` is a nonnegative decimal string with at most two decimal places. Currency must match the report and the timezone must be a valid IANA timezone. Groups are unique supported expense groups and must include `daily`. The budget is dailyLimit × calendar days in the current month, and resets each month. Today's opening allowance is the remaining budget before today's confirmed spending divided by remaining days including today, bounded between zero and dailyLimit. Today's confirmed spending, including confirmed pending purchases, is deducted once. Categories divide the nonnegative remaining allowance; cent remainders are assigned deterministically.

`allocationMode` is `history` or `manual`. Historical mode requires an empty shares array. Manual shares are unique `{ "category": "Groceries", "basisPoints": 4000 }` entries, with integer basis points totalling 10000. Category names use the original category identifiers, before display translations. Shares are advisory, not independent hard envelopes. Historical weights use only everyday spending from up to three complete previous calendar months covered by the source; missing or partial months are not silently filled. With no usable historical categories, ask for or allow a manual split rather than inventing one.

Spending in `Uncategorized`, `未分类`, `待分类` or `商户待分类` still counts against the allowance, but these categories are left out of the reference shares. Historical and manual shares are rescaled over the remaining categories to total 10000 basis points. Changing other settings does not rewrite saved manual shares; edited shares are saved only for the categories shown. If only unclassified history exists, no split is invented.

The optional `endpoint` must be exactly `/api/budget`; no external URL is accepted. Without it, edits are page-memory-only. With it, the renderer permits same-origin connections and the interface loads settings using GET. An empty configuration is `{ "settings": null, "revision": null }`. Saved responses contain validated `settings` and an opaque quoted `revision`. POST sends only the settings as JSON and uses `X-Budget-Revision` (`absent` for an initial save, otherwise the last loaded revision). The server must authenticate the user, require same-origin JSON writes, validate settings, conditionally store them privately and return 409 for conflicts. Never include credentials in the report. `preview: true` labels an explicitly isolated preview settings store.

`Finance.validateBudgetSettings(input)`, `Finance.budgetDate(settings, now)` and `Finance.dailyBudget(data, settings, asOf)` implement validation, timezone date selection and budget calculations. The report's existing refund, settlement and personal-share accounting remains authoritative. The source must cover the month start through yesterday for a usable current allowance; the UI distinguishes data cutoff and budget date. The result's `allocationShares` lists the reference shares actually used after that exclusion. Next to today's allowance, the report shows the change from yesterday's opening allowance, calculated with the current settings, as an amount and a percentage. It shows `—` when either value is unavailable, and `—` for the percentage when yesterday's opening allowance was zero.

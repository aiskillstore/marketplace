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

`Finance.validate(input)` returns normalized data (adding `amountCents` and default text fields) or throws a safe error without echoing financial values.

`Finance.periods(data, grain)` returns ascending `{key, label, start, end}` periods clipped to coverage; grain is `day`, `week`, `month`, or `year`. Weeks start on Monday.

`Finance.summarize(data, period)` returns:

- `inflow`, `outflow`, `net`, `spending`, `daily`, `dailyAverage`, `income`, `transferIn`, `transferOut`, `unpairedRefunds`: amounts in cents (personal amounts can have fractional cents).
- `groups`: group-to-personal-spending-cents map.
- `rows`: all period rows with `personalCents`, `cashCents` (signed adjusted external amount; zero for internal), `transferCents` (signed adjusted transfer), `matchedRefund` and `settledCents`.
- `days`: inclusive covered calendar days.

The same pure module runs in the browser and Node tests. All rendering must insert untrusted text with DOM text nodes, never HTML interpolation.

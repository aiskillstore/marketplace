# Statement to report

## Scope and language

Start with the user's supplied records, requested period and permitted tools. Do not search unrelated folders or connect additional services. Use the conversation language for the response and initial report language; an explicit choice takes priority. The interface supports English (`en`) and Simplified Chinese (`zh-CN`). Keep source descriptions unchanged unless the user requests translation.

Resolve only missing decisions that change the result, such as ambiguous date order, account ownership, personal share or a proposed loan/refund match. Continue independent reconciliation while those decisions are pending. No bank login is needed.

## Extract without inventing a parser

Read [schema.md](schema.md). A normalized CSV is already supported. A bank export may have separate debit and credit columns, localized dates, repeated headers or statement balances; map those fields explicitly first. PDFs require an available authorized extraction tool and visual checks where layout affects interpretation. If the tool cannot read the statement reliably, ask for a usable export rather than guessing.

Keep original statements intact. Use aliases for accounts and short source references; omit account numbers, credentials and absolute private paths from report fields. Record limitations in `notes` without copying unrelated statement text. Handle different currencies as separate reports; version 1 supports currencies with two decimal places and performs no currency conversion.

## Reconcile before classifying

- Establish source coverage independently of the first and last transaction. Note gaps and partial periods.
- Check amount direction and totals against the source. Reconcile balances when opening/closing balances are provided; unexplained differences remain unresolved.
- Deduplicate only proven duplicate evidence, including CSV/PDF representations of the same transaction. Same amount and date do not establish a duplicate. Keep a unique ID for each actual record.
- Confirm which account movements are internal. An unclassified receipt is `transfer_in`; an uncertain payment is `transfer_out`. Do not assume every deposit is income or every software charge is AI.
- Use `share` only for confirmed personal allocations. Preserve the raw bank amount. Keep rounding out of intermediate calculations.
- Add a full refund mapping only when a confirmed purchase and refund exactly offset in the report currency. Partial and unmatched refunds stay separate. Do not force an exchange-rate difference into a full match.
- Add settlements only for confirmed external transfers. A repayment can be partial; allocations cannot exceed either endpoint. Similar names and nearby dates alone are insufficient.

## Confirm uncertain transactions

Before rendering final charts for any user:

1. Review the available records and existing user confirmations. Identify unresolved facts that affect the requested report: unclear merchant purpose/category, missing account ownership or personal share, income versus transfer, a proposed refund/repayment match, or uncertain duplicate identity. A generic software merchant name does not establish an AI subscription, and matching names or amounts do not establish repayment or duplication.
2. Put the unresolved transactions in one confirmation table in the conversation. Use the user's language, account aliases, the original signed amounts and currency, and just enough description to identify each record. Keep a stable mapping from each row to its transaction ID in task context. Do not expose account numbers, private links or unrelated transactions. A suggested category is explicitly tentative.

   | Item | Bank date | Account alias | Transaction / merchant | Bank amount (currency) | Uncertain point | Please confirm |
   | --- | --- | --- | --- | --- | --- | --- |

   Populate the table only with the user's actual unresolved records. Ask specific questions such as what was purchased, whether a transfer was between their own accounts, or which purchase a refund concerns. Related rows may be grouped only if their individual dates and amounts and the scope of the answer remain clear.
3. Ask for the missing facts and wait. Reconcile unaffected data in parallel, but do not deliver the affected charts as final before a response. Do not invent uncertainty when evidence and existing confirmations are sufficient. A reply covering only some rows resolves only those rows.
4. Apply each answer only to its confirmed transaction(s) or explicitly stated broader rule. Preserve original bank facts, update the derived classification/allocation/match, and verify the changed totals and drill-down. Use existing authorized local ledgers when supplied; otherwise retain the clarification in task context without creating an unsolicited financial memory, cache or file.
5. If the user cannot identify an item, explicitly chooses to leave it pending, or asks to see a provisional result first, keep the unresolved status visible and explain its effect. Unknown income remains outside confirmed income; unconfirmed shares, internal transfers, refund matches and settlements must not be applied. Merely mentioning uncertainty in a footer is not a substitute for first showing the confirmation table and asking.

Do not ask again about the same transaction after a usable answer or an explicit decision to leave it pending, unless new evidence creates a specific conflict. Bank pending/posted status is separate from uncertainty about purpose; user confirmation of a purpose does not make a pending bank transaction posted. After the user confirms a pending purchase, include it with `bankStatus: "pending"` so spending and budgets reflect it. When the bank posts it, replace it once on clear matching evidence. Ask about a changed amount, a cancellation or a pending record that no longer appears.

## Understand the views

The report offers overview, spending, income and transfers, with day, week, month and year periods. Weeks run Monday–Sunday; all periods are clipped to confirmed coverage.

The overview shows bank-date external inflow, outflow and net change, excluding internal movements, confirmed settlement allocations and pending records. Spending uses confirmed personal shares, includes confirmed pending purchases (labelled in transaction details) and removes both sides of confirmed full refunds from the purchase period, even across months. These totals answer different questions and need not match. Income includes only confirmed income; other external receipts stay in transfers.

Groups provide a starting structure for daily costs, fixed services, AI, housing, education, equipment and other spending. Categories remain user-defined. Do not impose one person's categories, rent split or refund policy on another person's records.

## Deliver with memory as the default

Run `scripts/report.py` from the installed skill location. `--input` accepts normalized JSON, normalized CSV or `-` for JSON on stdin. For CSV, pass the currency and confirmed coverage with `--currency`, `--start` and `--end`. `--language` selects `en` or `zh-CN`. See the main skill for command examples.

Newly normalized input should be passed through supported process stdin without temporary files. Do not embed financial records in shell arguments. No intermediate financial logs, screenshots or automatic memory writeback should be created. This controls the skill's behavior; the host's own retention rules still apply.

The default mode keeps the report in memory, serves a tokenized URL on `127.0.0.1` and exits when stopped. Treat the URL as private. Browser history, memory and caches may persist under the browser's settings. Closing the process does not prove all copies have disappeared.

Use `--export /absolute/local/report.html` only after an explicit local-save request. Check the destination is outside the skill/repository and is not a cloud publication target. The exported HTML embeds records and works without remote assets. Do not overwrite an unrelated existing file; choose the user-authorized name or resolve the conflict.

Inspect the actual result for the chosen period and language. Check displayed totals against the reconciled dataset and open a relevant transaction detail. Use a temporary in-memory browser view for private data; persist screenshots only of the fictional demo. In the reply, give the opening link/path, coverage and any limitation that changes interpretation. Do not paste all transactions into the chat.

## Updates are separate

Only run `scripts/check_update.py` when the user asks to check the public version. It requests the latest release for `JasonHMY/personal-finance-visualizer` and does not need report input. Do not attach records, filenames, prompts or account details to this request. A version check does not install an update; installation is a separate explicit action. Neither the report renderer nor a financial-processing run should initiate an update request.


## Budget delivery

Confirm the daily limit, reset period, included expense groups and category allocation method. Reuse confirmed transaction classifications and personal shares. Use the existing budget calculation instead of subtracting both spending and its daily equivalent. Show source freshness, monthly balance and the daily cap; do not present an incomplete month as a reliable current allowance. Category references appear as one pie chart. Unclassified spending still counts against the allowance but stays out of the reference split until the user classifies it. The change shown next to today's allowance compares it with yesterday's opening allowance under the current settings; it is a guide, not a bank balance.

Standalone changes remain in page memory. If the user explicitly requests cross-device saving, use an authenticated private settings integration at the fixed same-origin budget endpoint, with conflict protection and no credentials in client code. Test initial save, reload, independent-page readback, stale-write rejection and anonymous/cross-origin rejection using fictional data first. An existing private deployment's authorization does not allow public file uploads or bypass links.

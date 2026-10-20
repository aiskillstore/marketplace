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

## Understand the views

The report offers overview, spending, income and transfers, with day, week, month and year periods. Weeks run Monday–Sunday; all periods are clipped to confirmed coverage.

The overview shows bank-date external inflow, outflow and net change, excluding internal movements and confirmed settlement allocations. Spending uses confirmed personal shares and removes both sides of confirmed full refunds from the purchase period, even across months. These totals answer different questions and need not match. Income includes only confirmed income; other external receipts stay in transfers.

Groups provide a starting structure for daily costs, fixed services, AI, housing, education, equipment and other spending. Categories remain user-defined. Do not impose one person's categories, rent split or refund policy on another person's records.

## Deliver with memory as the default

Run `scripts/report.py` from the installed skill location. `--input` accepts normalized JSON, normalized CSV or `-` for JSON on stdin. For CSV, pass the currency and confirmed coverage with `--currency`, `--start` and `--end`. `--language` selects `en` or `zh-CN`. See the main skill for command examples.

Newly normalized input should be passed through supported process stdin without temporary files. Do not embed financial records in shell arguments. No intermediate financial logs, screenshots or automatic memory writeback should be created. This controls the skill's behavior; the host's own retention rules still apply.

The default mode keeps the report in memory, serves a tokenized URL on `127.0.0.1` and exits when stopped. Treat the URL as private. Browser history, memory and caches may persist under the browser's settings. Closing the process does not prove all copies have disappeared.

Use `--export /absolute/local/report.html` only after an explicit local-save request. Check the destination is outside the skill/repository and is not a cloud publication target. The exported HTML embeds records and works without remote assets. Do not overwrite an unrelated existing file; choose the user-authorized name or resolve the conflict.

Inspect the actual result for the chosen period and language. Check displayed totals against the reconciled dataset and open a relevant transaction detail. Use a temporary in-memory browser view for private data; persist screenshots only of the fictional demo. In the reply, give the opening link/path, coverage and any limitation that changes interpretation. Do not paste all transactions into the chat.

## Updates are separate

Only run `scripts/check_update.py` when the user asks to check the public version. It requests the latest release for `JasonHMY/personal-finance-visualizer` and does not need report input. Do not attach records, filenames, prompts or account details to this request. A version check does not install an update; installation is a separate explicit action. Neither the report renderer nor a financial-processing run should initiate an update request.

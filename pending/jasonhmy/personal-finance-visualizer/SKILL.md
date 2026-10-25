---
name: personal-finance-visualizer
description: Turn user-provided personal finance records into a local interactive report with spending, income, transfers, cash movement and optional daily budgets in English or Chinese. Use for statement-based finance charts and period comparisons, not bank-account actions or investment advice.
license: MIT-0
metadata:
  version: "1.5.0"
  repository: "https://github.com/JasonHMY/personal-finance-visualizer"
---

# Personal Finance Visualizer

Prepare a reconciled dataset and show it in a local report. Use the user's language for the response and report (`en` or `zh-CN`); follow an explicit language request. Read [references/schema.md](references/schema.md) before preparing input and [references/workflow.md](references/workflow.md) for extraction, reconciliation and delivery.

## Preserve the report interface

Render the bundled `assets/report.html`, `report.css`, `app.js` and `engine.js` through `scripts/report.py`. These files are the maintained interface, not suggestions for generating a new dashboard. Do not substitute a different design, metric cards, tabs or chart library. The default is the dark circular report: four view buttons aligned to the heading’s right; period controls with a calendar popover (Monday-first day/week selection, month and year grids, dates restricted to supplied coverage, keyboard navigation and reduced motion); three primary spending rings, three secondary rings, merchant breakdown rings, timeline and collapsed details. Income uses two primary and three secondary rings, transfers use two rings and three metrics, and overview uses three metrics. Show at most six legend rows with internal scrolling and edge fades. Preserve rounded row feedback and pointer/keyboard chart tooltips. Spending, income and transfer timelines default to a gradient area chart with real-date scrubbing, bounded smoothing, interruptible period changes, keyboard drill-down and reduced-motion support. Keep the labeled, horizontally scrollable bar chart as a selectable alternative. Area-chart tooltips show actual observations, never interpolated amounts. Arrange the cards in a responsive grid. At widths of 700px or less, keep two ring/metric cards per row, proportionally scaled to 0.5 with a 12px gap; keep timelines and details full-width. Preserve zoom-aware drag coordinates and move transitions. Allow header dragging across the current view, keyboard reordering, cancellation and a per-view reset. Keep the default everyday merchant breakdown cards without a merchant-group selector or a visible drag instruction line. Center the day/week/month/year control on the page independently of the adjacent period label and date navigation. Use the same interruptible sliding indicator for view, period and chart-style switches, with brief opacity/position transitions only on affected visible content. Theme changes use a short color transition. Reduced motion disables nonessential animation. Create collapsed transaction tables and monthly summaries when opened, reuse number formatters and avoid repeated formatting inside chart-point animation loops. Group the bottom summaries, transaction tables, all-month overview, refunds and notes under one collapsed More information section, retaining their individual inner disclosures. Show card explanations on the information control. Keep card surfaces continuously visible when switching periods. Preserve interruptible ring and center/legend amount interpolation, with legend rows revealing from top to bottom and final values exact. Use the existing palette and layout unless the user requests a visual redesign. Animate disclosure panels, dialogs, menus and small control feedback without blocking input; respect reduced motion and defer offscreen animations. Change the design only if the user requests it.

## Data boundary

- Read only records authorized for the current task. Do not collect credentials, connect bank accounts, pay, transfer money or modify subscriptions.
- Keep data in process memory by default. Do not create normalized-input files, logs, screenshots, memory entries or cached financial summaries as an incidental part of the task. Never place real records in this skill, its Git repository, examples or public issues.
- Use the loopback memory server for delivery. Export a local HTML file only when the user requests saving/exporting, using their chosen local destination. An export contains transaction details. Do not publish or upload personal reports.
- After a user rearranges cards, save only opaque card identifiers and their order in local browser storage, separately for each view. Never store transaction data, amounts, merchant text or account identifiers there. Layouts persist on refresh at the same browser origin; if storage is unavailable, retain the in-page order and show that limitation.
- The renderer has no telemetry or remote assets. Standalone reports make no requests. An explicitly configured budget integration may read and save settings only through the same-origin `/api/budget` endpoint; never configure an external destination. The agent host may retain prompts, tool calls or supplied files under its own settings. Explain this briefly when relevant; a cloud agent reading data is not fully offline processing. Browser history/cache and explicit exports are also outside a promise of complete erasure.
- Never automatically check for updates while processing financial records. `scripts/check_update.py` is an explicit, separate public-version lookup; it does not receive financial input.

## Prepare and verify

For long merchant names, optionally provide `merchantDisplayNames` as described in the schema: shorten only clearly identified names for display, preserve original descriptions in details, and never change grouping or classification through a display label.

Use normalized JSON or CSV. Raw bank CSV needs an explicit column, sign and date mapping. PDF extraction uses the agent's available authorized tools; this skill does not include a universal statement parser. If extraction is unavailable, explain the limitation and request an accessible export.

Preserve source dates and amounts. Confirm source coverage, duplicate evidence, currency and signs before rendering. Unknown incoming money is a transfer until its purpose is established. Apply personal shares, full-refund matches and transfer settlements only when confirmed; never match solely by name, amount or date. Resolve uncertain transactions through the confirmation step below; notes disclose remaining limitations after that step, not a substitute for asking. Keep coverage gaps visible.

The report separates bank-date cash movement from personal spending. Internal account movements do not count as external cash movement. Shares affect spending only. Confirmed full refunds cancel spending in the purchase period; cash movement retains the actual bank dates. See the schema for partial and unmatched items.

## Ask before final charts

For every user, check for unresolved transactions before producing or updating final charts. Read available source evidence and the user's existing confirmations first. When a transaction's purpose, category, account ownership, personal share, income/transfer treatment or refund/repayment relationship remains uncertain, list it in a concise confirmation table in the conversation and ask the user to resolve the specific missing facts. Include date, account alias, merchant/description, signed amount and currency, what is uncertain, and the question to answer. Label any proposed classification as a suggestion, not a fact.

Batch the unresolved items in the requested scope. Do not silently guess, hide them in report notes and continue, or interpret no response as agreement. Continue independent extraction and reconciliation while waiting, but wait for the answers before finalizing affected charts. If the user explicitly requests a provisional preview or chooses to leave items unresolved, honor that choice and clearly label those items and the impact on totals; do not present them as confirmed.

Apply confirmations to the identified transactions without changing bank dates, amounts or source descriptions. Recompute and verify the affected tables and charts. Reuse prior answers within their confirmed scope, including an explicit choice to leave an item pending; do not repeatedly ask the same question or generalize a single purchase into a rule for every payment to that merchant. The detailed flow and table format are in [references/workflow.md](references/workflow.md#confirm-uncertain-transactions).

## Run

Requires Python 3.10+ and a modern browser. Resolve `<skill-dir>` to this installed skill directory; do not assume the user's working directory is the repository.

```bash
python3 "<skill-dir>/scripts/report.py" --input /local/normalized.json --language en
python3 "<skill-dir>/scripts/report.py" --input /local/normalized.csv --currency USD --start 2024-01-01 --end 2024-03-31 --language zh-CN
```

Existing files can be read directly within the user's authorization. For newly normalized data, prefer `--input -` and pass JSON to subprocess standard input through the host's supported API without writing an intermediate file or putting records in command arguments. Tool transcripts may still be retained by the host. Use `--demo` only for an explicitly labeled fictional demonstration.

The default command prints a tokenized `http://127.0.0.1:...` URL and keeps the report in memory while the process runs. Open that URL with the available browser tool or give it to the user. Keep the process alive during review; stop it when the user is finished. Do not expose the server beyond loopback or publish the tokenized URL.

If local export was requested:

```bash
python3 "<skill-dir>/scripts/report.py" --input /local/normalized.json --language en --export /absolute/local/report.html
```

Check the requested period, language, main totals and transaction drill-down. Use fictional data for saved screenshots and tests. Report the actual coverage, relevant unresolved items and how to open the result; do not claim a complete financial picture from a subset of accounts.


## Optional daily allowance

When requested, provide the `budget` input described in `references/schema.md`. The additional Daily allowance view uses a calendar-month budget, a daily upper limit and confirmed personal spending. It redistributes the remaining monthly allowance over the remaining days, resets in the next month and does not treat income or internal transfers as extra budget. Historical category shares use up to three complete earlier months of everyday spending; users can adjust these reference shares. Fixed-cost daily equivalents explain spending and are not deducted twice.

Clearly distinguish the budget date from the source cutoff. Missing month coverage or records older than yesterday makes today's allowance unavailable. Do not infer future bills or pending charges. Retain the existing confirmation requirements before using uncertain classifications.

A standalone report applies budget edits only in memory for the current page; it must not store budget values in localStorage. Persistent cross-device editing requires an explicitly authorized, authenticated same-origin budget endpoint backed by private storage. Only settings are sent, not transaction records. Show loading, failed-save and concurrent-edit states accurately; never treat an unconfirmed save as successful. Hosting authorization and the skill's default no-publication rule remain unchanged.

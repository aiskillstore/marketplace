---
name: personal-finance-visualizer
description: Turn user-provided personal finance records into a local interactive report with spending, income, transfers and cash movement in English or Chinese. Use for statement-based finance charts and period comparisons, not bank-account actions or investment advice.
license: MIT-0
metadata:
  version: "1.1.0"
  repository: "https://github.com/JasonHMY/personal-finance-visualizer"
---

# Personal Finance Visualizer

Prepare a reconciled dataset and show it in a local report. Use the user's language for the response and report (`en` or `zh-CN`); follow an explicit language request. Read [references/schema.md](references/schema.md) before preparing input and [references/workflow.md](references/workflow.md) for extraction, reconciliation and delivery.

## Preserve the report interface

Render the bundled `assets/report.html`, `report.css`, `app.js` and `engine.js` through `scripts/report.py`. These files are the maintained interface, not suggestions for generating a new dashboard. Do not substitute a different design, metric cards, tabs or chart library. The default is the dark circular report: title-adjacent view dropdown; period controls; three primary spending rings, three secondary rings, merchant breakdown rings, timeline and collapsed details. Income uses two primary and three secondary rings, transfers use two rings and three metrics, and overview uses three metrics. Keep the notes collapsed and show card explanations on the information control. Change the design only if the user requests it.

## Data boundary

- Read only records authorized for the current task. Do not collect credentials, connect bank accounts, pay, transfer money or modify subscriptions.
- Keep data in process memory by default. Do not create normalized-input files, logs, screenshots, memory entries or cached financial summaries as an incidental part of the task. Never place real records in this skill, its Git repository, examples or public issues.
- Use the loopback memory server for delivery. Export a local HTML file only when the user requests saving/exporting, using their chosen local destination. An export contains transaction details. Do not publish or upload personal reports.
- The renderer has no telemetry, remote assets or external requests. The agent host may retain prompts, tool calls or supplied files under its own settings. Explain this briefly when relevant; a cloud agent reading data is not fully offline processing. Browser history/cache and explicit exports are also outside a promise of complete erasure.
- Never automatically check for updates while processing financial records. `scripts/check_update.py` is an explicit, separate public-version lookup; it does not receive financial input.

## Prepare and verify

Use normalized JSON or CSV. Raw bank CSV needs an explicit column, sign and date mapping. PDF extraction uses the agent's available authorized tools; this skill does not include a universal statement parser. If extraction is unavailable, explain the limitation and request an accessible export.

Preserve source dates and amounts. Confirm source coverage, duplicate evidence, currency and signs before rendering. Unknown incoming money is a transfer until its purpose is established. Apply personal shares, full-refund matches and transfer settlements only when confirmed; never match solely by name, amount or date. Keep uncertain classifications and coverage gaps visible in report notes.

The report separates bank-date cash movement from personal spending. Internal account movements do not count as external cash movement. Shares affect spending only. Confirmed full refunds cancel spending in the purchase period; cash movement retains the actual bank dates. See the schema for partial and unmatched items.

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

---
name: bilig-workpaper
version: 0.1.0
description: Use @bilig/headless WorkPaper state for workbook formulas, agent spreadsheet tools, MCP file-backed editing, and XLSX formula bug reports without driving spreadsheet UI.
tags:
  - ai-agents
  - spreadsheet-automation
  - formulas
  - xlsx
  - mcp
  - typescript
---

# Bilig WorkPaper Agent Skill

Use this skill when an agent needs spreadsheet-style formulas but the work should run through files, terminal commands, TypeScript, HTTP routes, or MCP tools instead of Excel UI automation.

## When To Trigger

Trigger this skill for tasks involving:

- workbook-shaped business logic in Node.js services;
- formula readback after writing cells;
- quote, budget, payout, pricing, import-validation, or forecast models;
- agent spreadsheet tools that need deterministic cell addresses;
- MCP clients that can run a stdio server;
- reduced XLSX formula bugs that need a paste-ready report.

Do not trigger it for manual spreadsheet editing, Office macros, VBA, pivots, charts, COM automation, or exact Excel desktop behavior unless the user explicitly asks to compare Bilig against an Excel oracle.

## Command Safety

Do not build shell commands by concatenating user text. Treat the commands below as literal templates, validate workbook paths before use, and reject values containing newlines, backticks, `$(`, `;`, `&`, `|`, `<`, or `>`. Prefer MCP client `command` plus `args` arrays or direct TypeScript calls when inserting user-provided paths or cell references.

## First Choice: MCP

Use MCP when the host can run a stdio server. Configure it as an argument array, not a shell-concatenated string:

```json
{
  "command": "npm",
  "args": [
    "exec",
    "--package",
    "@bilig/headless@0.23.3",
    "--",
    "bilig-workpaper-mcp",
    "--workpaper",
    "./pricing.workpaper.json",
    "--init-demo-workpaper",
    "--writable"
  ]
}
```

The useful file-backed tools are:

- `list_sheets`
- `read_range`
- `read_cell`
- `set_cell_contents`
- `get_cell_display_value`
- `export_workpaper_document`
- `validate_formula`

After a write, always read the dependent output cell and export the WorkPaper document.

## Second Choice: Direct TypeScript

Use `@bilig/headless` directly when workbook logic belongs in a service, queue worker, test, or route:

```ts
import { WorkPaper, exportWorkPaperDocument, serializeWorkPaperDocument } from '@bilig/headless'

const workbook = WorkPaper.buildFromSheets({
  Inputs: [
    ['Metric', 'Value'],
    ['Customers', 20],
    ['Average revenue', 1200],
  ],
  Summary: [
    ['Metric', 'Value'],
    ['Revenue', '=Inputs!B2*Inputs!B3'],
  ],
})

const inputs = workbook.getSheetId('Inputs')
const summary = workbook.getSheetId('Summary')
if (inputs === undefined || summary === undefined) {
  throw new Error('Workbook is missing required sheets')
}

workbook.setCellContents({ sheet: inputs, row: 1, col: 1 }, 32)
const revenue = workbook.getCellDisplayValue({ sheet: summary, row: 1, col: 1 })
const saved = serializeWorkPaperDocument(exportWorkPaperDocument(workbook, { includeConfig: true }))

console.log({ revenue, savedBytes: saved.length })
```

## XLSX Formula Clinic

When the user has a reduced XLSX formula/import bug, generate a local report through an argument array:

```json
{
  "command": "npm",
  "args": ["exec", "--package", "@bilig/headless@0.23.3", "--", "bilig-formula-clinic", "./reduced.xlsx", "--cells", "Summary!B7,Inputs!B2"]
}
```

The report is local. It does not upload workbook contents. Ask for a reduced public fixture rather than private customer spreadsheets.

## Required Verification

Return proof, not vibes. A successful agent response should include:

- the exact edited sheet and A1 cell;
- before values for relevant inputs and dependent outputs;
- after values read from the recalculated workbook;
- persistence evidence from serialized or exported WorkPaper state;
- restore or reimport proof when file boundaries matter;
- limitations for unsupported formulas or Excel-only features.

If any proof step fails, report the blocker instead of claiming the workbook was updated.

## Reference URLs

- Compact docs map: https://proompteng.github.io/bilig/llms.txt
- Full agent context: https://proompteng.github.io/bilig/llms-full.txt
- Agent handbook: https://proompteng.github.io/bilig/headless-workpaper-agent-handbook.html
- MCP server guide: https://proompteng.github.io/bilig/mcp-workpaper-tool-server.html
- XLSX formula clinic: https://proompteng.github.io/bilig/formula-bug-clinic.html
- Compatibility limits: https://proompteng.github.io/bilig/where-bilig-is-not-excel-compatible-yet.html
- Repository: https://github.com/proompteng/bilig

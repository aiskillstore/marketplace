---
name: softsync-tables
description: "Read the workspace structure — tables, fields, choices and groups — and add or change tables. Use before any other SoftSync task to learn what the workspace holds, or when the user wants a new table or field."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Tables

## Reading the structure
`describe_workspace_schema` returns every table you can see with its fields, field kinds and options, plus the groups you can access. Call it before any other workspace tool.

- A choice field lists `options.choices`, each with a `value` (what you send) and a `label` (what the user sees). Always send the value.
- A relation field's `options.tableId` names the table it links to.
- A text or number field whose `options.source.type` is `sequence` is numbered by the app (ticket or invoice numbers). It gets its value on create and cannot be written; leave it out of `record_creation` and `update_record`.
- A field whose `options.source.type` is `formula` is calculated by the app from `options.source.expression` and cannot be written; leave it out of record writes. One that is `formula-default` is filled from its formula when left empty, and a value you send replaces it until it is cleared.
- Every table also has `__system_created_at`, `__system_updated_at` and `__system_created_by`.

## Changing the structure
- `upsert_table`: create a table or add and change its fields. Needs the Admin or Editor role.
- A calculated field is any field with `options.source` = `{ "type": "formula", "expression": "ROUND({Qty} * {Unit price}, 2)" }` (or `formula-default` for a starting value people can change). Fields are written in braces by display name; a linked field goes through its link field, e.g. `{Deal}.{Currency}` or `SUM({Order lines}.{Amount})`. Excel-style functions work (`IF`, `ROUND`, `SUMIFS`, `LOOKUP`, `NETWORKDAYS`, `PMT`…). Supported on text, number, date, select and multi-select fields. A broken formula is rejected with the reason; totals over linked records update a moment after the save, and changing a formula recalculates existing records in the background.
- `delete_table`: removes a table and every record in it. There is no Bin for tables. Admin only; confirm with the user first.

## Numbered fields
`get_field_counter` shows the number the next record will get; `set_field_counter` moves it, for example to start invoices at 1000. It cannot go below a number already in use.

## Rules
- Reuse an existing table or field when one fits instead of creating a near-duplicate.
- Describe the change you plan in plain words and wait for agreement before changing the structure.

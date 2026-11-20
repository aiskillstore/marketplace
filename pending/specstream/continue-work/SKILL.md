---
name: continue-work
description: Read the finished rows with each value's source URL and read time, send them where the person works, and start new work only on purpose.
---

# Read, send and continue

SpecStream is the live web data engine for teams and agents. Use the configured MCP server at `https://api.specstream.ai/mcp`.

Read `list_find_rows` and follow each `next_cursor` through the `cursor` argument until it is null. The first page is not the whole result. Open `get_find_decisions` to show each condition check with the value observed, its source and the time it was read. Never invent links or fill in unknown facts. Keep the original read times and do not call reused evidence fresh.

When the person asks, `send_to_destination` sends selected results to Google Sheets, Excel, Notion, Airtable, HubSpot, Salesforce or an Outlook draft. An Outlook draft lands in the person's own Drafts folder and is never sent. `export_find` makes a download link as CSV, Excel, JSON or HTML. Reading, exporting and sharing cost nothing.

Finding more, adding facts or rechecking is new work with its own reviewed price. A recheck costs half the rate for a row that changed and 1 cent for a row that did not.

`create_capacity_schedule` sets up a monitor and is a write. It needs a scope, a cadence, a validity period and limits per run and per period. A monitor reruns on its schedule and labels each change: still matches, no longer matches, unresolved or unavailable. Creating one does not fund it. A blocked or missed run is not an unchanged result and is not bought later. Pause or revoke a monitor when the owner says so.

The workspace is the place to explore the full history. Do not present a small result widget as the whole workspace.

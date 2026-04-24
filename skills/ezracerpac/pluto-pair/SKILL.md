---
name: pluto-pair
description: Pair Codex with Pluto.jl notebooks using MCP tools. Use for discovering visible Pluto servers, attaching to running notebooks, opening notebooks headlessly, inspecting @bind controls, setting bond values, reading compact state, or exporting HTML.
---

# Pluto Pair

Use the `pluto-pair` MCP server when a task involves Pluto.jl notebook state or controls.

If the user has a Pluto browser window open, prefer live attach first:

- `pluto_discover_servers` to check local Pluto servers, especially port 1234.
- `pluto_attach_session` to attach to a notebook already running in that visible server.
- `pluto_open_visible` to open a notebook in the visible server and attach to it.

Live attached sessions update the same notebook the user sees in their browser.

Use headless tools for isolated checks, CI-like validation, exports, or untrusted/static previews:

- `pluto_list_notebooks` to discover notebook files.
- `pluto_open_notebook` to open and execute a trusted notebook. Execution is the default; pass `execution_allowed=false` only for untrusted preview.
- `pluto_list_bonds` to inspect `@bind` variables.
- `pluto_set_bonds` to set bound values and trigger Pluto reactivity.
- `pluto_read_state` to summarize code, outputs, errors, logs, and bonds.
- `pluto_export_html` to write a rendered HTML export.
- `pluto_close_notebook` when finished. On live attached sessions, this only detaches and does not shut down the user's Pluto notebook.

Use browser automation only for visual smoke checks or screenshots.

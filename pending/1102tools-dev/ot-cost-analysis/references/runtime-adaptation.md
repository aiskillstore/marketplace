# OT Cost Analysis Runtime Adaptation

## Structured questions

Use a structured input tool for short mutually exclusive choices when the host exposes one. Otherwise present numbered choices, accept a number, label, or correction, and preserve every stop-and-wait gate. Do not mention a host-specific function name.

## MCP discovery

Match stable server and operation names semantically:

- `bls-oews`: `detect_latest_year`, `get_wage_data`, metro and SOC lookup operations
- `gsa-calc`: `suggest_contains`, `exact_search`, `keyword_search`, `igce_benchmark`
- `gsa-perdiem`: `estimate_travel_cost`, `lookup_city_perdiem`, `get_mie_breakdown`

If the stable operation is absent, inspect the same server for an equivalent schema. Stop when the required capability is unavailable. Do not replace it with undocumented API code.

## Workbook authoring

Follow the host's authoritative spreadsheet instructions before choosing an authoring route. Use a host spreadsheet workflow when it preserves exact formulas, formats, names, and source notes. Use Python and openpyxl only when the host does not provide a governing spreadsheet workflow that prohibits or hard-stops that substitute. Never bypass a host spreadsheet hard stop by guessing dependency paths or switching authoring libraries. Resolve bundled scripts relative to the skill directory. Require Python 3.10 or later and openpyxl for deterministic validation.

Before the first artifact-specific approval, state whether full workbook mode is available. If it is not, preserve all approved inputs and offer the workbook specification as structured JSON plus Markdown or CSV tables, or ask the user to continue in a maintained client surface that supports workbook generation. Do not label the fallback as a completed workbook.

## Formula execution

Openpyxl reads and writes formulas but does not calculate them.

1. Run structural validation.
2. Independently recompute from raw validation inputs.
3. Detect `soffice` or the LibreOffice application executable.
4. Recalculate a temporary copy, never the delivered original.
5. Reopen the calculated copy with `data_only=True` and compare cached results.

If no engine is available, disclose the missing layer exactly as the core instructs.

## File delivery

Choose a user-supplied destination, then a host output directory, then the current working directory. Use the host's artifact-presentation capability when available; otherwise return the absolute path. Do not assume `/mnt`, `/tmp`, a named presentation function, or one operating system.

Confirm the file exists before reporting success. Do not overwrite a user file unless requested.

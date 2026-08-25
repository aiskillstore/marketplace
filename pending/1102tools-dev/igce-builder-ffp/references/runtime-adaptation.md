# Runtime Adaptation

Use capabilities rather than product names in the main workflow. This reference explains how to adapt questions, tools, files, and workbook calculation without forking the skill.

## Structured questions

When the host exposes a structured question or user-input tool, use it for short, mutually exclusive choices. Otherwise:

1. Present numbered options in chat.
2. Accept a number, label, or free-text correction.
3. Preserve the staged-question gates.
4. End the response at the question when the workflow requires a pause.

Do not mention a host-specific function name in user-facing instructions.

## MCP tool discovery

Inspect the operations exposed in the session. Match these stable server and operation names:

- `bls-oews`: `detect_latest_year`, `get_wage_data`, `igce_wage_benchmark`, `list_common_metros`, `list_common_soc_codes`
- `gsa-calc`: `suggest_contains`, `exact_search`, `keyword_search`, `igce_benchmark`, `price_reasonableness_check`
- `gsa-perdiem`: `estimate_travel_cost`, `lookup_city_perdiem`, `get_mie_breakdown`

Hosts may add namespaces or separators around an MCP operation. Treat those wrappers as runtime details. Never copy a full host-generated name into the workbook or Methodology.

If a stable operation is not exposed, inspect available schemas for an equivalent operation on the same server. If none exists, stop and report the missing dependency. Do not hand-build an API request as an undocumented substitute.

## Workbook authoring and deterministic validation

Follow the host's authoritative spreadsheet instructions before choosing an authoring route. Use a host-supported spreadsheet authoring capability when it can create an `.xlsx` with the exact formulas, cell formats, sheet names, and source notes required by the workbook specification. Use Python and openpyxl only when the host does not provide a governing spreadsheet workflow that prohibits or hard-stops that substitute. Never bypass a host spreadsheet hard stop by guessing dependency paths or switching authoring libraries.

Before the first artifact-specific approval, state which mode is available:

- **Full workbook mode:** the host can create and deterministically validate the required `.xlsx`.
- **Structured fallback mode:** the host cannot use its supported workbook path. Preserve all approved inputs and offer the workbook specification as structured JSON plus Markdown or CSV tables, or ask the user to continue in a maintained client surface that supports workbook generation. Do not label the fallback as a completed workbook.

The authoring route does not change any workbook or validation gate.

Confirm that the runtime can execute Python 3.10 or later and import openpyxl before Step 8.5. The bundled deterministic validators require them even when another capability authored the workbook. If they are unavailable, report that deterministic validation cannot be completed and do not present the workbook as fully validated.

Use the skill-local scripts with paths resolved relative to the skill directory. Do not assume a global skill root.

## Spreadsheet calculation

Openpyxl writes and inspects formulas but does not evaluate them. Use this order:

1. Prefer a real spreadsheet engine available to the runtime.
2. On macOS or Linux, detect `soffice` or the LibreOffice application executable.
3. Recalculate a temporary copy, never the only copy of the user's workbook.
4. Reopen the recalculated copy with `data_only=True` and compare the cached results with the independent Python recomputation.
5. If no engine is available, run structural and independent checks and disclose that formula execution was not independently verified.

Do not claim that opening a workbook will necessarily recalculate it. That behavior depends on the receiving application and its calculation settings.

## File locations and delivery

Choose the destination in this order:

1. A path supplied by the user
2. A writable output directory provided by the host
3. The current project or working directory

Use the host's attachment or artifact-presentation capability when it exists. Otherwise return the absolute path. Do not assume a particular sandbox directory, presentation function, or OS-specific open command exists.

Confirm the file exists before reporting success. Do not overwrite a user file unless the user requested that exact target.

## Validation disclosure

Report the layers that actually ran:

- Formula-structure audit
- Independent mathematical recomputation
- LibreOffice or Excel execution verification

When the third layer did not run, use this exact statement:

> Formula structure and independent calculations passed. Formula execution was not independently verified in Excel or LibreOffice.

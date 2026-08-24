# Runtime Adaptation

Use host capabilities instead of hardcoded client names.

## Questions

If the host exposes a structured question tool, use it for short mutually exclusive choices. Otherwise present a numbered list in chat and accept a number, label, or free-text answer. Do not refer to a tool name in user-facing prose.

For Stage A, ask only for decomposition confirmation and stop. For Stage B, batch independent missing fields into one response. Ask one field at a time only when an answer changes the next available choices.

## MCP operations

Inspect the available operations and match their server, operation name, description, and schema. Host prefixes and separators are implementation details. For example, look for the `detect_latest_year` operation from the BLS OEWS server rather than a literal generated namespace.

Declared MCP dependencies do not prove that a server is installed, authenticated, or reachable. Keep the pre-flight check.

## Files and Python

Use the host's file-reading, file-writing, and Python capabilities. Follow any authoritative host spreadsheet workflow and its hard stops. Use Python and openpyxl for workbook authoring only when no governing host spreadsheet workflow prohibits that substitute; never guess dependency paths or bypass a host hard stop. Resolve referenced files relative to this skill directory when possible. If the host does not expose the skill directory, report which reference or script cannot be loaded and stop before a step that depends on it.

Before the first artifact-specific approval, state whether full workbook mode is available. If it is not, preserve all approved inputs and offer the workbook specification as structured JSON plus Markdown or CSV tables, or ask the user to continue in a maintained client surface that supports workbook generation. Do not label the fallback as a completed workbook.

## Formula verification

openpyxl writes formulas and reads cached values; it does not calculate Excel formulas. Validation has three layers:

1. Formula-structure audit with openpyxl.
2. Independent recomputation from raw inputs in Python.
3. Formula execution in a real spreadsheet engine when available.

On macOS and Linux, detect `soffice` and use LibreOffice headless for layer 3. Do not automate desktop Excel on macOS. When no engine is available, use the exact disclosure in Step 8.5.

## Delivery

Use the host's artifact presentation capability when available. Otherwise save to the user-supplied directory or current working directory and report the absolute path. Do not assume `/mnt`, `present_files`, shell launch commands, or a particular desktop application exists.

Never claim that saving a workbook caused formulas to execute. Never call a workbook validated unless the claimed validation layers actually ran.

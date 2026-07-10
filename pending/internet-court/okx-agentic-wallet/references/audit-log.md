# Audit Log

Provide the audit log file path so developers can troubleshoot offline. This is a local file, not a CLI subcommand. Do NOT read or display the file contents in the conversation.

Tell the user:

1. **Log file path**: `~/.onchainos/audit.jsonl` (or `$ONCHAINOS_HOME/audit.jsonl` if the env var is set).
2. **Format**: JSON Lines, one JSON object per line.
3. **First line (device header)**: `{"type":"device","os":"<os>","arch":"<arch>","version":"<cli_version>"}` — written once when the file is created; preserved across rotations.
4. **Entry fields**: `ts` (local time with timezone, e.g. `2026-03-18 +8.0 18:00:00.123`), `source` (cli / mcp), `command`, `ok`, `duration_ms`, `args` (redacted), `error`.
5. **Rotation**: max 10,000 lines; auto-keeps the device header + the most recent 5,000 entries.

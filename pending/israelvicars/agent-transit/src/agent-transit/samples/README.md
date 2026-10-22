# Synthetic agent sessions

These JSONL files are hand-built fixtures, not copied from any real `~/.claude`, `~/.codex`, or `~/.cursor` directory. Claude Code and Codex fixtures carry a synthetic marker; the Cursor fixture follows the native transcript shape and is synthetic by this README/test context. The payloads intentionally contain prompt, output, file-content, and command-argument canaries so tests prove they never reach HTML by default. Cursor timing is synthetic because the format has no timestamps or results.

# JSON Schemas

Storage: `{DATA_DIR}/` (resolved by hook — see SKILL.md Storage section)

## library.json

Active notebooks index (minimal for fast loading).

```json
{
  "notebooks": {
    "claude-docs": {
      "id": "claude-docs",
      "name": "Claude Code Documentation",
      "url": "https://notebooklm.google.com/notebook/abc123",
      "topics": ["Claude Code", "CLI", "Plugins"],
      "added_at": "2026-01-20T08:00:00Z",
      "discovered_by": "smart-add"
    }
  },
  "schema_version": "1.0",
  "updated_at": "2026-01-25T14:30:00Z"
}
```

## archive.json

Same structure as library.json, for disabled notebooks.

## notebooks/{id}.json

Full metadata, loaded on-demand.

```json
{
  "schema_version": "1.0",
  "id": "claude-docs",
  "name": "Claude Code Documentation",
  "url": "https://notebooklm.google.com/notebook/abc123",
  "description": "Official Claude Code documentation",
  "topics": ["Claude Code", "CLI", "Plugins", "MCP", "Hooks"],
  "created_at": "2026-01-20T08:00:00Z",
  "updated_at": "2026-01-24T11:30:00Z"
}
```

## config.json

User preferences, initialized with defaults on first session.

```json
{
  "max_followups": 3,
  "max_query_length": 40000,
  "language": null,
  "auto_coverage": true,
  "schema_version": "1.0"
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_followups` | number | 3 | Maximum follow-up queries in coverage analysis |
| `max_query_length` | number | 40000 | Maximum characters per query sent to NotebookLM |
| `language` | string \| null | null | Preferred response language (null = match user's language) |
| `auto_coverage` | boolean | true | Enable automatic coverage analysis after queries |

## Empty States

```json
{"notebooks": {}, "schema_version": "1.0", "updated_at": "..."}
```

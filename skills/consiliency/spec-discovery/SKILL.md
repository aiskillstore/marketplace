---
name: spec-discovery
description: "Parse specs to extract IDs, titles, and traceability metadata (repo, path, hash)."
---

# Spec Discovery Skill

Locate specs and external request headers, extract IDs (e.g., `REQ-NOTIFY-001`), and return traceable metadata for downstream agents.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| ROOT | . | Primary repository root |
| EXTRA_REPOS | [] | Additional repo roots containing `specs/` |
| INCLUDE_EXTERNAL_REQUESTS | true | Scan `specs/external-requests/` |
| OUTPUT_FORMAT | json | json or toon manifest output |

## Workflow (Mandatory)

1. **Load repositories**: ROOT + EXTRA_REPOS
2. **Walk specs**: `specs/`, `specs/external-requests/`, skip `specs/templates/`
3. **Parse headings**: match `^#+\s*(REQ-[A-Za-z0-9_-]+)\s*:?\s*(.*)$`
4. **Normalize**: path relative to repo root, anchor from ID + title
5. **Traceability**: compute SHA-256 of file content; record `source_repo`, `path`, `hash`
6. **Emit manifest**: sorted by repo → path → ID in JSON/TOON (see Output Schema)

## Red Flags (Stop & Verify)

- No IDs detected in a spec file → confirm heading format before skipping
- Duplicate spec IDs across repos → flag in the manifest `notes` field
- Missing `specs/` directory → report empty result rather than failing

## Output Schema

```json
{
  "format": "spec-manifest/v1",
  "generated_at": "<ISO-8601 UTC>",
  "sources": [
    {"repository": "<repo-name>", "root": "<abs-path>"}
  ],
  "specs": [
    {
      "id": "REQ-NOTIFY-001",
      "title": "Email Sending Endpoint",
      "source_repo": "ai-dev-kit",
      "path": "specs/external-requests/notify.md",
      "link": "specs/external-requests/notify.md#req-notify-001-email-sending-endpoint",
      "hash": "<sha256-of-file>"
    }
  ]
}
```

## Provider Notes

- Use this skill when other commands request `/ai-dev-kit:specs-find` or spec traceability.
- Prefer JSON for machine workflows; use TOON for compact prompt embedding.
- Preserve ID/title casing; anchors should be lowercase + hyphenated.

# Frontmatter Schema

## Principle

Frontmatter must be minimal, machine-readable, and non-destructive. The skill only writes to defined PARA fields and never touches anything else.

## Full Field Definitions

```yaml
para_type: project       # REQUIRED when set. Values: project | area | resource | archive
status: active           # Values: active | on-hold | done | archived | reference | needs_review
review_date: 2026-03-21  # ISO date. When to next review this note.
confidence: high         # Classification confidence: high | medium | low
needs_review: false      # Boolean. Flag for manual review queue.
archived: false          # Boolean. True only when moved to Archive.
archive_date:            # ISO date. Only set when archiving.
source: manual           # Origin: manual | meeting | import | daily-note | web | capture
area:                    # Parent area name, if applicable (e.g., "career", "weiterbildung")
project:                 # Parent project slug, if applicable (e.g., "para-skill")
```

## Tags Convention

PARA-related tags use the `para/` prefix to stay clearly separated:

```yaml
tags:
  - para/project
  - para/area
  - para/resource
  - para/archive
  - para/review     # needs manual review
```

Never remove existing tags. Only add `para/` prefixed tags.

## Field Writing Rules

| Scenario | Rule |
|---|---|
| Note has no frontmatter | Create a minimal PARA block with only the fields you're confident about |
| Note has partial frontmatter | Add only missing PARA fields, preserve all existing fields |
| Note has `para_type` already set | Only update if clearly wrong AND confidence is high AND user confirmed |
| Note has non-PARA frontmatter | Leave all non-PARA fields untouched |
| Field is uncertain | Omit the field rather than guess; add `needs_review: true` instead |

## Minimal Required Block

When creating frontmatter from scratch, the minimum valid PARA block is:

```yaml
---
para_type: resource
status: active
needs_review: false
---
```

## Date Format

Always use ISO 8601: `YYYY-MM-DD` (e.g., `2026-03-14`)

## Status Values Reference

| Status | Meaning |
|---|---|
| `active` | Actively worked on or in use |
| `on-hold` | Temporarily paused, but not abandoned |
| `done` | Task/project complete, not yet archived |
| `archived` | Moved to Archive, no longer active |
| `reference` | Stable resource, accessed but not modified |
| `needs_review` | Classification or content needs human attention |

## Review Date Guidelines

Set `review_date` based on PARA type:
- **project**: 1 week from today (frequent check-ins)
- **area**: 1 month from today (regular maintenance)
- **resource**: 3 months from today (periodic relevance check)
- **archive**: 1 year from today (or omit entirely)

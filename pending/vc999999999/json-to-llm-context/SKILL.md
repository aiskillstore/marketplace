---
name: json-to-llm-context
description: Turn JSON or PostgreSQL jsonb payloads into compact readable context for LLMs. Use when a user wants to compress JSON, reduce token usage, summarize API responses, or convert structured data into model-friendly text without dumping raw paths.
---

# JSON to LLM Context

## Overview

Use this skill when raw JSON is too noisy for direct prompting. It converts JSON or exported `jsonb`
content into short, readable summaries that preserve entities, status, relationships, and counts.

Prefer this skill for:
- API responses
- PostgreSQL `jsonb` exports
- nested config/state payloads
- large arrays of records that need compact summaries

Do not use this skill for PDF, DOCX, image OCR, or arbitrary prose documents.

## Workflow

1. Confirm the input is valid JSON or `jsonb`-style JSON text.
2. Run `scripts/json_to_readable_context.py` on the file or pipe JSON through stdin.
3. Return the generated readable summary as the primary artifact.
4. If the output still feels too long, rerun with tighter limits such as lower `--max-samples`,
   `--max-depth`, or `--max-string-len`.
5. If parsing fails, report the JSON error clearly instead of guessing.

## Quick Start

```bash
python3 scripts/json_to_readable_context.py --input payload.json
```

From stdin:

```bash
cat payload.json | python3 scripts/json_to_readable_context.py
```

Write to a file:

```bash
python3 scripts/json_to_readable_context.py --input payload.json --output summary.txt
```

Common tuning:

```bash
python3 scripts/json_to_readable_context.py \
  --input payload.json \
  --style sectioned \
  --strict \
  --preserve status,profile.email \
  --show-paths \
  --expand collections \
  --max-samples 2 \
  --max-depth 2 \
  --max-string-len 48
```

## Output Style

The script aims for layer-2 readable output, for example:

```text
User[123]: Tom

Summary
- Status: active.
- Profile: email a@b.com (verified).

Collections
- Roles: 2 total; values: admin and editor.
```

Behavior rules:
- prefer entity headers like `User[123]: Tom`
- group top-level output into `Summary`, `Details`, and `Collections` when available
- convert fields into short report-style bullets when possible
- summarize large arrays as totals, statuses, and short examples
- keep stable ordering so repeated runs are comparable
- avoid raw path dumps unless the structure is too irregular to beautify safely

## Style Options

- `--style sectioned` (default): emits `Summary`, `Details`, and `Collections`
- `--style flat`: emits a simpler header + bullet list without section headings

Example flat output:

```text
User[123]: Tom
- Status: active.
- Profile: email a@b.com (verified).
- Roles: 2 total; values: admin and editor.
```

## Safety Controls

- `--strict`: reduces aggressive compression and keeps more explicit structure
- `--preserve key1,key2,path.to.field`: always keeps those keys or dotted paths, even when empty or normally dropped
- `--expand collections|details|all`: adds local sub-bullets so important parts are less compressed
- `--show-paths`: appends source markers like `[@status]` or `[@orders[0]]` to rendered lines

Example:

```bash
python3 scripts/json_to_readable_context.py \
  --input payload.json \
  --strict \
  --preserve status,profile.email,orders \
  --expand all \
  --show-paths
```

Example with paths:

```text
User[123]: Tom [@root]

Summary
- Status: active. [@active]

Collections
- Roles: 2 total; values: admin and editor. [@roles]
```

## When To Read References

Read `references/rules.md` only when you need:
- the exact summarization heuristics
- examples of array and nested-object handling
- guidance for deciding whether to tighten or loosen output

## Failure Handling

- Invalid JSON: stop and show the parse error
- Very irregular objects: fall back to simplified readable key/value lines
- Extremely deep payloads: cap traversal with `--max-depth`
- Overlong text blobs: truncate safely with length hints

## Notes

- `json` and PostgreSQL `jsonb` are treated the same once parsed
- the default output is a single readable text artifact
- this skill intentionally favors readability over perfect structural fidelity

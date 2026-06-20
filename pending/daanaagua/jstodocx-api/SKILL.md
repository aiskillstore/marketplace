---
name: jstodocx-api
description: Generate Microsoft Word DOCX files through the jstodocx.com API. Use when Codex needs to create or download .docx files from basic HTML, JavaScript source text, or controlled document template fields; when a user asks for HTML to DOCX, JS source to Word, or template-based DOCX generation via an API; or when integrating a lightweight Cloudflare Worker DOCX conversion endpoint into scripts, tests, or agent workflows.
---

# jstodocx.com API

Use the jstodocx.com API to create Word `.docx` files from controlled inputs. The API is useful for agents that need a downloadable DOCX without installing document-generation dependencies locally.

Read [references/api.md](references/api.md) when you need exact request schemas, examples, status codes, or response headers.

## Workflow

1. Choose one mode:
   - `html`: convert basic HTML headings, paragraphs, lists, and tables into DOCX.
   - `js-source`: archive JavaScript source text as a readable Word document. Do not treat this as code execution.
   - `template`: create a report, invoice, proposal, resume, or meeting-notes DOCX from structured fields.
2. Send `POST https://jstodocx.com/api/v1/docx` with `content-type: application/json`.
3. If the endpoint returns `401`, ask the user for an API key or use the browser-local website instead. Do not guess credentials.
4. Save the binary response to a `.docx` file.
5. Verify the result when possible by checking the response `content-type`, filename, and ZIP magic bytes `PK`.

## Safety Rules

- Do not execute arbitrary JavaScript through this API. The `js-source` mode treats JavaScript as text only.
- Do not send protected, confidential, or high-risk content unless the user explicitly confirms it is acceptable to send it to the API.
- Do not print, log, commit, or store API keys.
- Do not include raw user document content in logs or final summaries. Summarize mode, byte size, filename, and status instead.
- Do not claim pixel-perfect HTML fidelity. The API supports basic document formatting.

## Minimal Example

```bash
curl -X POST "https://jstodocx.com/api/v1/docx" \
  -H "content-type: application/json" \
  --output release-plan.docx \
  --data '{
    "mode": "html",
    "title": "Release Plan",
    "html": "<h1>Release Plan</h1><p>Hello <strong>team</strong>.</p>"
  }'
```

If the user provides an API key:

```bash
curl -X POST "https://jstodocx.com/api/v1/docx" \
  -H "content-type: application/json" \
  -H "authorization: Bearer $JSTODOCX_API_KEY" \
  --output source-archive.docx \
  --data '{
    "mode": "js-source",
    "title": "Widget Export Code",
    "code": "function exportWidget() {\n  return 42;\n}",
    "options": { "lineNumbers": true }
  }'
```

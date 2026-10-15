---
name: gaffa-support
description: Use when the user is stuck using the gaffa skills or wants to report a problem. First attempts to resolve it from the current context and the live docs, then, if still unresolved, packages a redacted local report the developer can email to support.
disable-model-invocation: true
---

# gaffa support

When a developer is stuck, first try to resolve the problem in-session, and only if that fails, package a redacted local report they can email to support.
The report is the project's feedback signal on how the skills perform in real use.
The skill runs entirely on the developer's machine: it reads the gaffa docs but never calls the gaffa API, spends no credits, and sends nothing on its own.

## Support contact

- `SUPPORT_EMAIL` is `support@gaffa.dev`.
  The address the developer emails the report to.
  To change it, edit this value.

## Critical gaffa facts (grounding)

1. Auth header is `X-API-Key: <key>`.
   Read from `GAFFA_API_KEY` env var.
   Never hard-code.
2. `POST /v1/browser/requests` runs synchronously by default and returns the finished result.
   Set `"async": true` to get an id back immediately.
   Poll `GET /v1/browser/requests/{id}` for the result.
3. Max runtime is plan-tiered (1 / 2 / 5 min) for async requests.
   Sync requests (`"async": false`) are capped at 60 seconds on every plan.
   Always set `settings.time_limit` explicitly.
4. `parse_json` is token-priced, so its cost scales with the content parsed rather than being a flat per-call charge.
   Stored `/v1/schemas` extractions run the same `parse_json` action and are priced the same way.
   Check the live docs for the current model and token rates.
   Other actions are deterministically priced.
5. Request recordings (`settings.record_request: true`) are a recon and debugging tool, they cost extra, so leave them off in shipped code.
   `/gaffa-debug` needs one, without it the skill can only suggest re-running the failing request with recording enabled.
   The plans' general data retention applies (7 days / 30 days / 3 months), recordings share that window.

The API base URL is `https://api.gaffa.dev`.
Every `/v1/...` endpoint is called on that host.
The documentation and the docs MCP live on `https://gaffa.dev`.
API responses are wrapped in a top-level `data` object, so read fields as `data.id`, `data.state`, `data.credit_usage`, and `data.actions`.
A finished request has `data.state` equal to `completed`.
Each action result is in `data.actions[].output`, a storage URL by default, or the content itself when the action ran with `output_type: "inline"`.
In the request body, `actions`, `time_limit`, and `record_request` go under `settings`, while `url`, `async`, `max_cache_age`, and `proxy_location` are root-level.
`time_limit` is in milliseconds.
The `parse_json` action uses a structured `data_schema` of the form `{name, description, fields: [{type, name, description}]}`, never a flat object and never a `schema` or `prompt` field.
An optional `instruction` parameter sits beside `data_schema` (not inside it) for extra parsing guidance.
`/v1/schemas` is an endpoint for reusable stored schemas, not an action type.
LLM-backed extraction runs through the `parse_json` action, with an inline `data_schema` or a stored `data_schema_id`, and there is no separate schema action type.
On a large content-rich page, `parse_json` over the full DOM can fail with `action_failed` (verified on Wikipedia), so narrow the input with a `selector` for the region that holds the data, or set `input_token_cap`.

## Credential hygiene

1. Read `GAFFA_API_KEY` from env only.
   Never hard-code in emitted code.
   Reference it as `${GAFFA_API_KEY}`.
2. Never echo, log, narrate, or persist the value of `GAFFA_API_KEY`.
   Never put it in a URL or query string.
3. Before showing a gaffa recording, error trace, or request body to the user, to an LLM judge, or to disk, strip the values of any fields whose names match (case-insensitive, including vendor-prefixed variants like `gaffa_api_key`): `Authorization`, `X-API-Key`, `api_key` (and `apiKey`, `api-key`), `cookie`, `set-cookie`.
   Replace the value with `<REDACTED>`.
4. If the runtime value of `GAFFA_API_KEY` appears as a substring anywhere in a payload you are about to show or persist, replace it with `<REDACTED>`.
   Only enable this substring scrub when the env value is at least 16 characters long and contains both a digit and a letter.
   Otherwise skip and warn the developer on first invocation that the entropy floor was not met (field-name and prose rules still apply).
5. Persisted writes (the `/gaffa-find` reasoning log `./.gaffa-find-<timestamp>.log`, and any other on-disk artifact) go through redaction first, then to a tempfile, then atomic-rename to the final path.
   A crash mid-write must not leave a plaintext-secrets file on disk.
6. If unsure whether a string is a secret, redact it.

## Doc-fetching strategy

Resolve documentation queries in two tiers, in order.

1. Preferred: gaffa docs MCP server at `https://gaffa.dev/docs/~gitbook/mcp`.
   `searchDocumentation` (param `query`) for "how do I do X".
   `getPage` (param `url`) to fetch one page by URL.
2. Fallback: live HTTP fetch.
   `?ask=` against the docs for narrow lookups, `https://gaffa.dev/docs/llms.txt` for breadth.
   Per-call timeout of 5 seconds.

MCP availability probe, once per session, cached, total budget 10 seconds: JSON-RPC `initialize`, then the mandatory `notifications/initialized` notification, then `tools/list` confirming `searchDocumentation` and `getPage` (or at least one).
Per-call MCP timeout is 5 seconds.
Two consecutive timeouts demote to live HTTP for the rest of the session, announced once.

If both tiers fail, skip the in-session resolution attempt, say the docs are unavailable, and continue to the report so the developer is not left empty-handed.
Both tiers read from `gaffa.dev`, so note the likely cause: `gaffa.dev` blocked by the environment's egress or proxy policy, separate from `api.gaffa.dev`, which the setup section in the skills README covers.

## Phase 1: resolve

1. State up front that the skill runs entirely on the machine: it reads only the gaffa docs over the network, makes no gaffa API call, spends no credits, and sends nothing on its own.
2. If the developer gave no problem statement, ask for one short sentence describing what they were trying to do and what went wrong.
3. Make one bounded attempt to unstick them: re-read the relevant context already in the conversation, consult the docs via the doc-fetching strategy above, and offer a concrete likely cause and a next step.
4. If that resolves it, stop.
   Otherwise, or if the developer wants a report regardless, continue to Phase 2.

## Phase 2: package a report

Gather:

- The developer's problem statement.
- Working-directory artifacts the other skills produce.
  List the working directory first, then read and include every file that matches: the `/gaffa-find` reasoning log `./.gaffa-find-<timestamp>.log`, and any generated gaffa script the developer points to or that the conversation produced.
  Also include any `brq_*` request ids the developer mentions.
  Do not skip an artifact that is present.
  List what you found, and let the developer drop any item before the report is written.
- A drafted problem description composed from the current context: what was attempted, where it broke, the relevant request ids and environment.
  This is best-effort.
  You can only summarize what is still in the conversation, and after auto-compaction the original turns may be gone, so the on-disk artifacts are the reliable part of the report.

Then:

- Get one timestamp from the system clock with `date -u +%Y%m%dT%H%M%SZ`.
  Do not invent it.
  Use that value for both the filename and the report's `Generated` line.
- Redact everything through the credential-hygiene rules above before writing.
  Redaction is best-effort, not a guaranteed scrub: it can miss secrets it does not recognize, such as a key hard-coded as a string literal in a generated script, a token inside a URL, or personal data scraped from a target site.
  Say this plainly so the developer reviews the file before sending it.
- Write the redacted report to `./gaffa-support-<timestamp>.md` in the working directory through the redaction-then-tempfile-then-atomic-rename path: write to a tempfile in the same directory, then rename it over the final path.
- Show the report contents inline so the developer can review without opening the file.
- End with the next action.
  The developer emails the file to `SUPPORT_EMAIL` (`support@gaffa.dev`).
  Give a one-line summary of what the file contains, for example the number of artifacts and the request ids.
  Sending is the developer's manual step.
  Remind them the report sits in their working directory, so they should delete it after sending or add `gaffa-support-*.md` to their `.gitignore`, since it can hold redacted data and scraped content.

## Report shape

```markdown
# gaffa skills support report

Generated: <timestamp from `date -u +%Y%m%dT%H%M%SZ`>

## Problem
<the developer's problem statement, plus the drafted description>

## Environment
- Skill involved: <gaffa-authoring | gaffa-find | gaffa-debug | unknown>
- Request ids: <brq_... or none>

## What was already tried
<the Phase 1 resolution attempt and its outcome>

## Artifacts
<for each gathered artifact: its filename, then its redacted contents in a fenced block>
```

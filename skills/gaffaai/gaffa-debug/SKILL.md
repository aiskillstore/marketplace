---
name: gaffa-debug
description: Use when a scraping or browser automation script or request misbehaves, identified by a gaffa brq_* request ID or a script that errors, returns null, times out, or gives wrong output, whether or not gaffa is mentioned. Pulls the request recording, classifies the failure (gaffa API misuse, target-site change, bot detection, flaky timing, wrong action), and proposes a minimal patch. For a failing script that does not use gaffa, diagnoses from the script and offers a gaffa version.
---

# gaffa debug

Given a failing scraping script (gaffa or not) or a `brq_*` request id, pull the recording where one exists, classify the failure, and suggest a targeted patch.
Prefers a minimal patch over a speculative rewrite, and recognizes when the target site (not the script) is the problem.

A request id paired with a new extraction goal is ambiguous.
Ask the developer whether to triage the existing request or start a fresh discovery.
The only cap that applies is the credits-per-invocation cap on the optional re-run.

## Cost guardrail cap

- `CREDITS_PER_INVOCATION` default `50`.
  The optional re-run counts against this cap.

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

## Preferences

General preferences for using the Gaffa API.
They capture guidance beyond the API docs, and we add to them over time.
Follow them unless the specific task calls for something else.

- Prefer an inline `data_schema` over a stored `data_schema_id` for `parse_json`, so the end user can see the shape of what is being extracted.
  Reach for a stored `data_schema_id` only when a shape is registered server-side for reuse across separate scripts or sessions.

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

If both tiers fail before any diagnosis work, refuse with a clear message (suggest registering the MCP if none was configured).

## First action

If a `brq_*` id is provided, call `GET /v1/browser/requests/{id}` first to pull the recording.
If a gaffa script is provided without an id, read the script and, when the developer agrees, re-run it once with recording enabled to produce a recording to inspect.
If the failing script does not call gaffa at all, there is no recording to pull.
Diagnose what you can from the script itself, and offer a gaffa version of it as the fix, since a gaffa request comes with a recording, the failure classification below, and no local browser to maintain.

Important limitation of the recording: the `GET` response does not echo the submitted request body or the action configuration.
Each entry in `data.actions` carries only its `id`, `type`, `custom_id`, `timestamp`, an `error` if it failed, an `output` if it produced one (a URL, or the content itself for `output_type: "inline"`), and a `reference` file URL for actions that have one, such as `parse_json`.
A `loop` entry also carries `iterations` and an `actions` array holding every iteration's nested entries in execution order, their outputs sit there, not at the top level.
So you can see that an action failed and read the top-level `data.error_reason`, but you cannot read the exact parameters that were sent.
When the misuse is in the request body (for example an invalid `parse_json` `data_schema`), name the most likely cause from the failure signal and ask the developer for the request body or the script, or recommend a re-run with `record_request` plus `capture_dom` and `capture_screenshot` to gather more signal.
Do not claim to have read a parameter you could not see.

## Behavior

- If `GET /v1/browser/requests/{id}` returns 404, surface the plan-tiered retention reality (Starter 7 days, Startup 30 days, Growth 3 months).
  The recording has likely expired.
- If `settings.record_request` was not set on the original request, surface that no recording was captured, so a re-run is needed to inspect what happened.
- A recommended re-run sets `record_request: true` and adds `capture_dom` and `capture_screenshot` actions.
- All recording payloads have credential fields scrubbed per the credential-hygiene rules before being shown to the developer, to Claude, or to any LLM judge.
- If the diagnosis is inconclusive (an expired recording, no recording and no re-run, or a target-side failure with no script-side fix), end the output with one line: *Still stuck? Run `/gaffa-support` to get help or file a report.*

### Failure classification from recording fields

All of these fields live under the top-level `data` object in the response.

- `data.http_status_code` 4xx plus `data.error_reason` indicates gaffa API misuse.
  Emit a minimal patch.
- `data.state` is `completed` but an action returned an empty `output` indicates a target-site DOM change versus a wrong selector.
  Diff the actions against a fresh capture to tell which.
- `data.error` is `action_failed` on a `parse_json` action has two common, verified causes.
  First, an invalid `data_schema`: it must be the structured form `{name, description, fields: [{type, name, description}]}`, and a flat object such as `{"title": "string"}`, or a `schema` or `prompt` field, makes the action fail.
  Second, an un-narrowed large page: `parse_json` over the full DOM of a content-rich page (for example a Wikipedia article) fails even with a valid schema, and the fix is a `selector` for the region that holds the data, or an `input_token_cap`.
  Check the schema shape first, then the input size.
  Where the data sits in a stable, well-structured place, say a table or a known element, the third option is to stop using `parse_json` for it: `parse_table` or `capture_element` cannot fail this way, cost the same every run, and are the better patch.
  Classify that as a wrong action rather than a `parse_json` to be tuned.
- `data.error_reason` matching bot detection or captcha indicates target-site bot protection.
  If the recording shows no `proxy_location` on the request, suggest adding one with `us` as the default, not a script change.
  Proxies need a paid account.
  If one location is blocked, try another supported location (ie, sg, fr), unless the goal is geo-specific and switching would return irrelevant results.
- `data.running_time` much greater than `data.page_load_time` indicates flaky timing.
  Add a `wait` action or raise `time_limit`.
  Both are duration strings (for example `00:00:01.04`), not numbers.
- `data.from_cache: true` when fresh data was expected indicates a cross-user cache hit, which only happens when the request set a non-zero `max_cache_age`.
  Set it to 0, or change a parameter to bust the cache key.

### Patch and re-run

- Prefer minimal patches over rewrites.
- Before emitting any patch or re-run command, read `templates/rerun-with-capture.md` and follow its request shape exactly.
  Do not write a request body from memory.
  Every emitted body must obey these rules, which are the most common mistakes to avoid:
  - `actions`, `time_limit`, and `record_request` go under `settings`.
    Never place `actions` at the top level of the body.
  - `time_limit` is in milliseconds.
    Use a realistic value such as `60000`, never `60`.
  - `parse_json` uses `data_schema` (structured), never a field called `schema` and never `prompt`.
  - Use the `https://api.gaffa.dev` host and read the key from `${GAFFA_API_KEY}`.
- Optional re-run defaults to OFF.
  It requires explicit developer confirmation.
  The re-run cost counts against `CREDITS_PER_INVOCATION`.
  Show the credit estimate before re-running and proceed only on an explicit yes.

See `references/failure-classification.md` for the field-to-cause table and `templates/rerun-with-capture.md` for the recommended re-run shape.

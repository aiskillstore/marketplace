---
name: gaffa-find
description: Use when the user wants to find, scrape, or extract a specific piece of information from a target website given only a URL and a plain-language goal but has no script yet, whether or not gaffa is mentioned. Invoke it even when the URL or the goal is still missing, and ask for them inside the skill, never before invoking. Iteratively writes and refines a gaffa script through reconnaissance, extraction, and validation, then stops in a clear terminal state.
---

# gaffa find

Given a target URL and a natural-language information goal, write and refine a gaffa script through reconnaissance, hypothesis, extraction, validation, and refinement, then stop with a clear terminal state.
Prevents premature commitment to a wrong selector and silent acceptance of empty or wrong results.
Invoked without the URL or the goal, ask for what is missing first, then run the loop.

## Cost guardrail caps

The skill enforces the caps below.

- `REQUESTS_PER_ITERATION` default `3`.
  Caps requests inside one loop step.
- `REQUESTS_PER_INVOCATION` default `15`.
  Caps total requests per run.
- `CREDITS_PER_INVOCATION` default `50`.
  Caps total credits per run.
- `MAX_ITERATIONS` default `5`.
  Caps loop iterations.

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
5. Request recordings (`settings.record_request: true`) are a recon and debugging tool, they cost extra.
   The find loop is reconnaissance, so it records every browser request it makes and `/gaffa-debug` has a recording to inspect a failed attempt.
   Leave it off in the re-runnable script the skill hands back.
   The plans' general data retention applies (7 days / 30 days / 3 months), recordings share that window.

The API base URL is `https://api.gaffa.dev`.
Every `/v1/...` endpoint is called on that host.
The documentation and the docs MCP live on `https://gaffa.dev`.
API responses are wrapped in a top-level `data` object, so read fields as `data.id`, `data.state`, `data.credit_usage`, and `data.actions`.
A finished request has `data.state` equal to `completed`.
Each action result is in `data.actions[].output`, a storage URL by default, or the content itself when the action ran with `output_type: "inline"`.
In the request body, `actions`, `time_limit`, and `record_request` go under `settings`, while `url`, `async`, `max_cache_age`, and `proxy_location` are root-level.
`time_limit` is in milliseconds.
Each entry in `settings.actions` is an object keyed by `type`, for example `{"type": "generate_markdown"}` or `{"type": "capture_element", "selector": "h1"}`.
The key is `type`, never `action`, and an action object missing it is rejected with `invalid_action`.
The `parse_json` action uses a structured `data_schema` of the form `{name, description, fields: [{type, name, description}]}`, never a flat object and never a `schema` or `prompt` field.
An optional `instruction` parameter sits beside `data_schema` (not inside it) for extra parsing guidance.
`/v1/schemas` is an endpoint for reusable stored schemas, not an action type.
LLM-backed extraction runs through the `parse_json` action, with an inline `data_schema` or a stored `data_schema_id`, and there is no separate schema action type.
`parse_json` is not the only way to get data off a page, see step 3 of the loop.
On a large content-rich page, `parse_json` over the full DOM can fail with `action_failed` (verified on Wikipedia), so narrow the input with a `selector` for the region that holds the data, or set `input_token_cap`.

Reconnaissance uses `POST /v1/site/map` (singular `map`, the POST waits for the crawl and returns the links) or a broad markdown capture (`generate_markdown`).

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

If both tiers fail at iteration 0 (before any work), refuse with a clear message (suggest registering the MCP if none was configured).
If both tiers fail mid-flight (at least one iteration done), do not discard progress: return the current best candidate as `needs-human-review`, persist the reasoning log, and surface the doc-fetch failure as the reason.

## First action

Once the URL and goal are in hand, fire a reconnaissance request, not a doc load.
The reconnaissance (site map or broad markdown capture) tells you where the answer is likely to live before you commit to a selector.

## Terminal states

The skill always ends in exactly one of these three states.

- success.
  The extracted value clearly fits the goal, and any developer-supplied validator passed.
  Output includes a short evidence line (which page, which selector or extraction step) so the developer can verify without rerunning.
- needs-human-review.
  The skill is uncertain (judgment ambiguous, or budget exhausted with a partial candidate).
  Output includes the best candidate, the reasoning-log location, and the failing script's request id with a `/gaffa-debug` suggestion.
- terminal-failure.
  Unrecoverable error: the target blocks every attempt, or the doc fetch fails mid-flight after work began.
  Output explains why and surfaces the request id.

On `needs-human-review` or `terminal-failure`, end the output with one line: *Still stuck? Run `/gaffa-support` to get help or file a report.*

## Loop

1. Reconnaissance (`/v1/site/map` or a broad markdown capture).
2. Hypothesize the answer's likely location.
3. Targeted extraction.
   Choose the action before you look up its parameters, and say which you chose and why.
   When the value sits in a stable, well-structured place, take the deterministic path: `parse_table` with a `selector` for a table, `generate_markdown` with a `selector` for a region you then parse in the developer's own language, or `capture_element` with a `selector` for one element.
   Cheaper, repeatable, identical every run, and your `generate_markdown` recon output often already shows whether the shape is stable enough.
   Only when the value is buried in free text or moves from page to page (a salary somewhere in a job description), the goal is interpretive (summarising, classifying), or the developer explicitly asks for it, use the `parse_json` action (inline `data_schema`, or `data_schema_id` for a reused shape), which handles ambiguity a selector cannot but is token-priced and can vary between runs.
4. Check the stop condition: does the value clearly fit the goal, and does any supplied validator pass?
5. Refine the hypothesis or finish, returning the answer plus a re-runnable script.
6. Stop on success, on budget exhaustion (any of the three caps or `MAX_ITERATIONS`), or on an unrecoverable error.

## Behavior

- Inputs.
  Required: target URL and a plain-language goal.
  Optional: an explicit validator passed as `--validator` (a regex, JSON schema, or expected type) for deterministic termination, and a max-iterations override.
- Pre-flight credit estimate before each request.
  Pause and confirm when the invocation total would breach `CREDITS_PER_INVOCATION`.
  For token-priced actions (`parse_json`, `/v1/schemas`) gate against the upper bound of the estimate, not the midpoint.
  For `parse_json`, fetch current rates from https://gaffa.dev/docs/features/browser-requests/actions/parse-json.md once per invocation, reuse that cached rate for later requests, and add a 50% safety margin on output tokens.
  For `/v1/schemas`, pin a conservative ceiling at the worst current `parse_json` rate applied to the captured page size in tokens, tell the developer the ceiling is a guess, and ask for confirmation regardless of headroom.
  Count the proxy bandwidth too: requests set `proxy_location` by default and the bandwidth is billed separately, so add a rough allowance for the page weight and say it is a guess.
- `--reconnaissance-only` returns the site map or landing capture without entering the extraction loop.
- Per-iteration reasoning is logged to `./.gaffa-find-<timestamp>.log` in the developer's working directory, written through the redaction-then-tempfile-then-atomic-rename path.
  Create it before the first request and append after every iteration, a run without the log is incomplete.
  See `templates/loop.md` for the rationale and shape.
- Always set `settings.time_limit` explicitly.
- Set `settings.record_request: true` on each browser request in the loop, they are reconnaissance, so a failing attempt can be triaged with `/gaffa-debug`.
  Recording doubles the browser-time charge, count that in the pre-flight estimate.
  Drop it from the re-runnable script you hand back.
- Set `proxy_location` on every browser request, the loop and the re-runnable script alike, `us` unless the target is clearly in another supported country or the developer asks for one.
  With none set, the request goes out from a datacenter IP, which sites block more readily.
  If a request fails with a proxy or access error, retry it once without `proxy_location`, some sites are restricted on the proxy network.
- Do not invent an answer.
  If the goal is not found within budget, stop with `needs-human-review` and say so plainly.
- Returns both the answer and the working, re-runnable gaffa script.

See `templates/loop.md` for the reconnaissance, extraction, and reasoning-log shapes.

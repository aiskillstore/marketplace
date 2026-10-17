---
name: xcrawl-crawl
description: Use this skill for XCrawl crawl tasks, including bulk site crawling, crawler rule design, async status polling, and delivery of crawl output for downstream scrape and search workflows.
allowed-tools: Bash(curl:*) Bash(node:*) Read Write Edit Grep
metadata: {"version":"1.0.2","openclaw":{"skillKey":"xcrawl-crawl","homepage":"https://www.xcrawl.com/","requires":{"localFiles":["~/.xcrawl/config.json"],"anyBins":["curl","node"]},"apiKeySource":"local_config"}}
---

# XCrawl Crawl

## Overview

This skill orchestrates full-site or scoped crawling with XCrawl Crawl APIs.
Default behavior is raw passthrough: return upstream API response bodies as-is.

## Required Local Config

Before using this skill, the user must create a local config file and write `XCRAWL_API_KEY` into it.

Path: `~/.xcrawl/config.json`

```json
{
  "XCRAWL_API_KEY": "<your_api_key>"
}
```

Read API key from local config file only. Do not require global environment variables.

## Credits and Account Setup

Using XCrawl APIs consumes credits.
If the user does not have an account or available credits, guide them to register at `https://dash.xcrawl.com/`.
After registration, they can activate the free `1000` credits plan before running requests.

## Tool Permission Policy

Request runtime permissions for `curl` and `node` only.
Do not request Python, shell helper scripts, or other runtime permissions.

## API Surface

- Start crawl: `POST /v1/crawl`
- Read result: `GET /v1/crawl/{crawl_id}`
- Base URL: `https://run.xcrawl.com`
- Required header: `Authorization: Bearer <XCRAWL_API_KEY>`

## Usage Examples

### cURL (create + result)

```bash
API_KEY="$(node -e "const fs=require('fs');const p=process.env.HOME+'/.xcrawl/config.json';const k=JSON.parse(fs.readFileSync(p,'utf8')).XCRAWL_API_KEY||'';process.stdout.write(k)")"

CREATE_RESP="$(curl -sS -X POST "https://run.xcrawl.com/v1/crawl" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"url":"https://example.com","crawler":{"limit":100,"max_depth":2},"output":{"formats":["markdown","links"]}}')"

echo "$CREATE_RESP"

CRAWL_ID="$(node -e 'const s=process.argv[1];const j=JSON.parse(s);process.stdout.write(j.crawl_id||"")' "$CREATE_RESP")"

curl -sS -X GET "https://run.xcrawl.com/v1/crawl/${CRAWL_ID}" \
  -H "Authorization: Bearer ${API_KEY}"
```

### Node

```bash
node -e '
const fs=require("fs");
const apiKey=JSON.parse(fs.readFileSync(process.env.HOME+"/.xcrawl/config.json","utf8")).XCRAWL_API_KEY;
const body={url:"https://example.com",crawler:{limit:300,max_depth:3,include:["/docs/.*"],exclude:["/blog/.*"]},request:{locale:"ja-JP"},output:{formats:["markdown","links","json"]}};
fetch("https://run.xcrawl.com/v1/crawl",{
  method:"POST",
  headers:{"Content-Type":"application/json",Authorization:`Bearer ${apiKey}`},
  body:JSON.stringify(body)
}).then(async r=>{console.log(await r.text());});
'
```

## Request Parameters

### Request endpoint and headers

- Endpoint: `POST https://run.xcrawl.com/v1/crawl`
- Headers:
- `Content-Type: application/json`
- `Authorization: Bearer <api_key>`

### Request body: top-level fields

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `url` | string | Yes | - | Site entry URL |
| `crawler` | object | No | - | Crawler config |
| `proxy` | object | No | - | Proxy config |
| `request` | object | No | - | Request config |
| `js_render` | object | No | - | JS rendering config |
| `output` | object | No | - | Output config |
| `webhook` | object | No | - | Async callback config |

### `crawler`

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `limit` | integer | No | `100` | Max pages |
| `include` | string[] | No | - | Include only matching URLs (regex supported) |
| `exclude` | string[] | No | - | Exclude matching URLs (regex supported) |
| `max_depth` | integer | No | `3` | Max depth from entry URL |
| `include_entire_domain` | boolean | No | `false` | Crawl full site instead of only subpaths |
| `include_subdomains` | boolean | No | `false` | Include subdomains |
| `include_external_links` | boolean | No | `false` | Include external links |
| `sitemaps` | boolean | No | `true` | Use site sitemap |

### `proxy`

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `location` | string | No | `US` | ISO-3166-1 alpha-2 country code, e.g. `US` / `JP` / `SG` |
| `sticky_session` | string | No | Auto-generated | Sticky session ID; same ID attempts to reuse exit |

### `request`

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `locale` | string | No | `en-US,en;q=0.9` | Affects `Accept-Language` |
| `device` | string | No | `desktop` | `desktop` / `mobile`; affects UA and viewport |
| `cookies` | object map | No | - | Cookie key/value pairs |
| `headers` | object map | No | - | Header key/value pairs |
| `only_main_content` | boolean | No | `true` | Return main content only |
| `block_ads` | boolean | No | `true` | Attempt to block ad resources |
| `skip_tls_verification` | boolean | No | `true` | Skip TLS verification |

### `js_render`

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `enabled` | boolean | No | `true` | Enable browser rendering |
| `wait_until` | string | No | `load` | `load` / `domcontentloaded` / `networkidle` |
| `viewport.width` | integer | No | - | Viewport width (desktop `1920`, mobile `402`) |
| `viewport.height` | integer | No | - | Viewport height (desktop `1080`, mobile `874`) |

### `output`

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `formats` | string[] | No | `["markdown"]` | Output formats |
| `screenshot` | string | No | `viewport` | `full_page` / `viewport` (only if `formats` includes `screenshot`) |
| `json.prompt` | string | No | - | Extraction prompt |
| `json.json_schema` | object | No | - | JSON Schema |

`output.formats` enum:

- `html`
- `raw_html`
- `markdown`
- `links`
- `summary`
- `screenshot`
- `json`

### `webhook`

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `url` | string | No | - | Callback URL |
| `headers` | object map | No | - | Custom callback headers |
| `events` | string[] | No | `["started","completed","failed"]` | Events: `started` / `completed` / `failed` |

## Response Parameters

### Create response (`POST /v1/crawl`)

| Field | Type | Description |
|---|---|---|
| `crawl_id` | string | Task ID |
| `endpoint` | string | Always `crawl` |
| `version` | string | Version |
| `status` | string | Always `pending` |

### Result response (`GET /v1/crawl/{crawl_id}`)

| Field | Type | Description |
|---|---|---|
| `crawl_id` | string | Task ID |
| `endpoint` | string | Always `crawl` |
| `version` | string | Version |
| `status` | string | `pending` / `crawling` / `completed` / `failed` |
| `url` | string | Entry URL |
| `data` | object[] | Per-page result array |
| `started_at` | string | Start time (ISO 8601) |
| `ended_at` | string | End time (ISO 8601) |
| `total_credits_used` | integer | Total credits used |

`data[]` fields follow `output.formats`:

- `html`, `raw_html`, `markdown`, `links`, `summary`, `screenshot`, `json`
- `metadata` (page metadata)
- `traffic_bytes`
- `credits_used`
- `credits_detail`

## Workflow

1. Confirm business objective and crawl boundary.
- What content is required, what content must be excluded, and what is the completion signal.

2. Draft a bounded crawl request.
- Prefer explicit limits and path constraints.

3. Start crawl and capture task metadata.
- Record `crawl_id`, initial status, and request payload.

4. Poll `GET /v1/crawl/{crawl_id}` until terminal state.
- Track `pending`, `crawling`, `completed`, or `failed`.

5. Return raw create/result responses.
- Do not synthesize derived summaries unless explicitly requested.

## Output Contract

Return:

- Endpoint flow (`POST /v1/crawl` + `GET /v1/crawl/{crawl_id}`)
- `request_payload` used for the create request
- Raw response body from create call
- Raw response body from result call
- Error details when request fails

Do not generate summaries unless the user explicitly requests a summary.

## Guardrails

- Never run an unbounded crawl without explicit constraints.
- Do not present speculative page counts as final coverage.
- Do not hardcode provider-specific tool schemas in core logic.
- Highlight policy, legal, or website-usage risks when relevant.

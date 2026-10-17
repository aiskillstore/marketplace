---
name: xcrawl
description: Use this skill as the default XCrawl entry point for direct XCrawl requests, including single-URL fetch, format selection, sync or async execution, and JSON extraction with prompt or json_schema.
allowed-tools: Bash(curl:*) Bash(node:*) Read Write Edit Grep
metadata: {"version":"1.0.2","openclaw":{"skillKey":"xcrawl","homepage":"https://www.xcrawl.com/","requires":{"localFiles":["~/.xcrawl/config.json"],"anyBins":["curl","node"]},"apiKeySource":"local_config"}}
---

# XCrawl

## Overview

This skill is the default XCrawl entry point when the user asks for XCrawl directly without naming a specific API or sub-skill.
It currently targets single-page extraction through XCrawl Scrape APIs.
Default behavior is raw passthrough: return upstream API response bodies as-is.

## Routing Guidance

- If the user wants to extract one or more specific URLs, use this skill and default to XCrawl Scrape.
- If the user wants site URL discovery, prefer XCrawl Map APIs.
- If the user wants multi-page or site-wide crawling, prefer XCrawl Crawl APIs.
- If the user wants keyword-based discovery, prefer XCrawl Search APIs.

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

- Start scrape: `POST /v1/scrape`
- Read async result: `GET /v1/scrape/{scrape_id}`
- Base URL: `https://run.xcrawl.com`
- Required header: `Authorization: Bearer <XCRAWL_API_KEY>`

## Usage Examples

### cURL (sync)

```bash
API_KEY="$(node -e "const fs=require('fs');const p=process.env.HOME+'/.xcrawl/config.json';const k=JSON.parse(fs.readFileSync(p,'utf8')).XCRAWL_API_KEY||'';process.stdout.write(k)")"

curl -sS -X POST "https://run.xcrawl.com/v1/scrape" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"url":"https://example.com","mode":"sync","output":{"formats":["markdown","links"]}}'
```

### cURL (async create + result)

```bash
API_KEY="$(node -e "const fs=require('fs');const p=process.env.HOME+'/.xcrawl/config.json';const k=JSON.parse(fs.readFileSync(p,'utf8')).XCRAWL_API_KEY||'';process.stdout.write(k)")"

CREATE_RESP="$(curl -sS -X POST "https://run.xcrawl.com/v1/scrape" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"url":"https://example.com/product/1","mode":"async","output":{"formats":["json"]},"json":{"prompt":"Extract title and price."}}')"

echo "$CREATE_RESP"

SCRAPE_ID="$(node -e 'const s=process.argv[1];const j=JSON.parse(s);process.stdout.write(j.scrape_id||"")' "$CREATE_RESP")"

curl -sS -X GET "https://run.xcrawl.com/v1/scrape/${SCRAPE_ID}" \
  -H "Authorization: Bearer ${API_KEY}"
```

### Node

```bash
node -e '
const fs=require("fs");
const apiKey=JSON.parse(fs.readFileSync(process.env.HOME+"/.xcrawl/config.json","utf8")).XCRAWL_API_KEY;
const body={url:"https://example.com",mode:"sync",output:{formats:["markdown","json"]},json:{prompt:"Extract title and publish date."}};
fetch("https://run.xcrawl.com/v1/scrape",{
  method:"POST",
  headers:{"Content-Type":"application/json",Authorization:`Bearer ${apiKey}`},
  body:JSON.stringify(body)
}).then(async r=>{console.log(await r.text());});
'
```

## Request Parameters

### Request endpoint and headers

- Endpoint: `POST https://run.xcrawl.com/v1/scrape`
- Headers:
- `Content-Type: application/json`
- `Authorization: Bearer <api_key>`

### Request body: top-level fields

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `url` | string | Yes | - | Target URL |
| `mode` | string | No | `sync` | `sync` or `async` |
| `proxy` | object | No | - | Proxy config |
| `request` | object | No | - | Request config |
| `js_render` | object | No | - | JS rendering config |
| `output` | object | No | - | Output config |
| `webhook` | object | No | - | Async webhook config (`mode=async`) |

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

### Sync create response (`mode=sync`)

| Field | Type | Description |
|---|---|---|
| `scrape_id` | string | Task ID |
| `endpoint` | string | Always `scrape` |
| `version` | string | Version |
| `status` | string | `completed` / `failed` |
| `url` | string | Target URL |
| `data` | object | Result data |
| `started_at` | string | Start time (ISO 8601) |
| `ended_at` | string | End time (ISO 8601) |
| `total_credits_used` | integer | Total credits used |

`data` fields (based on `output.formats`):

- `html`, `raw_html`, `markdown`, `links`, `summary`, `screenshot`, `json`
- `metadata` (page metadata)
- `traffic_bytes`
- `credits_used`
- `credits_detail`

`credits_detail` fields:

| Field | Type | Description |
|---|---|---|
| `base_cost` | integer | Base scrape cost |
| `traffic_cost` | integer | Traffic cost |
| `json_extract_cost` | integer | JSON extraction cost |

### Async create response (`mode=async`)

| Field | Type | Description |
|---|---|---|
| `scrape_id` | string | Task ID |
| `endpoint` | string | Always `scrape` |
| `version` | string | Version |
| `status` | string | Always `pending` |

### Async result response (`GET /v1/scrape/{scrape_id}`)

| Field | Type | Description |
|---|---|---|
| `scrape_id` | string | Task ID |
| `endpoint` | string | Always `scrape` |
| `version` | string | Version |
| `status` | string | `pending` / `crawling` / `completed` / `failed` |
| `url` | string | Target URL |
| `data` | object | Same shape as sync `data` |
| `started_at` | string | Start time (ISO 8601) |
| `ended_at` | string | End time (ISO 8601) |

## Workflow

1. Classify the request through the default XCrawl entry behavior.
- If the user provides specific URLs for extraction, default to XCrawl Scrape.
- If the user clearly asks for map, crawl, or search behavior, route to the dedicated XCrawl API instead of pretending this endpoint covers it.

2. Restate the user goal as an extraction contract.
- URL scope, required fields, accepted nulls, and precision expectations.

3. Build the scrape request body.
- Keep only necessary options.
- Prefer explicit `output.formats`.

4. Execute scrape and capture task metadata.
- Track `scrape_id`, `status`, and timestamps.
- If async, poll until `completed` or `failed`.

5. Return raw API responses directly.
- Do not synthesize or compress fields by default.

## Output Contract

Return:

- Endpoint(s) used and mode (`sync` or `async`)
- `request_payload` used for the request
- Raw response body from each API call
- Error details when request fails

Do not generate summaries unless the user explicitly requests a summary.

## Guardrails

- Do not present XCrawl Scrape as if it also covers map, crawl, or search semantics.
- Default to scrape only when user intent is URL extraction.
- Do not invent unsupported output fields.
- Do not hardcode provider-specific tool schemas in core logic.
- Call out uncertainty when page structure is unstable.

---
name: xcrawl-map
description: Use this skill for XCrawl map tasks, including site URL discovery, regex filtering, scope estimation, and crawl planning before full-site crawling.
allowed-tools: Bash(curl:*) Bash(node:*) Read Write Edit Grep
metadata: {"version":"1.0.2","openclaw":{"skillKey":"xcrawl-map","homepage":"https://www.xcrawl.com/","requires":{"localFiles":["~/.xcrawl/config.json"],"anyBins":["curl","node"]},"apiKeySource":"local_config"}}
---

# XCrawl Map

## Overview

This skill uses XCrawl Map API to discover URLs for a site.
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

- Start map task: `POST /v1/map`
- Base URL: `https://run.xcrawl.com`
- Required header: `Authorization: Bearer <XCRAWL_API_KEY>`

## Usage Examples

### cURL

```bash
API_KEY="$(node -e "const fs=require('fs');const p=process.env.HOME+'/.xcrawl/config.json';const k=JSON.parse(fs.readFileSync(p,'utf8')).XCRAWL_API_KEY||'';process.stdout.write(k)")"

curl -sS -X POST "https://run.xcrawl.com/v1/map" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"url":"https://example.com","filter":"/docs/.*","limit":2000,"include_subdomains":true,"ignore_query_parameters":false}'
```

### Node

```bash
node -e '
const fs=require("fs");
const apiKey=JSON.parse(fs.readFileSync(process.env.HOME+"/.xcrawl/config.json","utf8")).XCRAWL_API_KEY;
const body={url:"https://example.com",filter:"/docs/.*",limit:3000,include_subdomains:true,ignore_query_parameters:false};
fetch("https://run.xcrawl.com/v1/map",{
  method:"POST",
  headers:{"Content-Type":"application/json",Authorization:`Bearer ${apiKey}`},
  body:JSON.stringify(body)
}).then(async r=>{console.log(await r.text());});
'
```

## Request Parameters

### Request endpoint and headers

- Endpoint: `POST https://run.xcrawl.com/v1/map`
- Headers:
- `Content-Type: application/json`
- `Authorization: Bearer <api_key>`

### Request body: top-level fields

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `url` | string | Yes | - | Site entry URL |
| `filter` | string | No | - | Regex filter for URLs |
| `limit` | integer | No | `5000` | Max URLs (up to `100000`) |
| `include_subdomains` | boolean | No | `true` | Include subdomains |
| `ignore_query_parameters` | boolean | No | `true` | Ignore URLs with query parameters |

## Response Parameters

| Field | Type | Description |
|---|---|---|
| `map_id` | string | Task ID |
| `endpoint` | string | Always `map` |
| `version` | string | Version |
| `status` | string | `completed` |
| `url` | string | Entry URL |
| `data` | object | URL list data |
| `started_at` | string | Start time (ISO 8601) |
| `ended_at` | string | End time (ISO 8601) |
| `total_credits_used` | integer | Total credits used |

`data` fields:

- `links`: URL list
- `total_links`: URL count
- `credits_used`: credits used
- `credits_detail`: credit breakdown

## Workflow

1. Restate mapping objective.
- Discovery only, selective crawl planning, or structure analysis.

2. Build and execute `POST /v1/map`.
- Keep filters explicit and reproducible.

3. Return raw API response directly.
- Do not synthesize URL-family summaries unless requested.

## Output Contract

Return:

- Endpoint used (`POST /v1/map`)
- `request_payload` used for the request
- Raw response body from map call
- Error details when request fails

Do not generate summaries unless the user explicitly requests a summary.

## Guardrails

- Do not claim full site coverage if `limit` is reached.
- Do not mix inferred URLs with returned URLs.
- Do not hardcode provider-specific tool schemas in core logic.

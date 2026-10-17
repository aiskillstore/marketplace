---
name: xcrawl-search
description: Use this skill for XCrawl search tasks, including keyword search request design, location and language controls, result analysis, and follow-up crawl or scrape planning.
allowed-tools: Bash(curl:*) Bash(node:*) Read Write Edit Grep
metadata: {"version":"1.0.2","openclaw":{"skillKey":"xcrawl-search","homepage":"https://www.xcrawl.com/","requires":{"localFiles":["~/.xcrawl/config.json"],"anyBins":["curl","node"]},"apiKeySource":"local_config"}}
---

# XCrawl Search

## Overview

This skill uses XCrawl Search API to retrieve query-based results.
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

- Search endpoint: `POST /v1/search`
- Base URL: `https://run.xcrawl.com`
- Required header: `Authorization: Bearer <XCRAWL_API_KEY>`

## Usage Examples

### cURL

```bash
API_KEY="$(node -e "const fs=require('fs');const p=process.env.HOME+'/.xcrawl/config.json';const k=JSON.parse(fs.readFileSync(p,'utf8')).XCRAWL_API_KEY||'';process.stdout.write(k)")"

curl -sS -X POST "https://run.xcrawl.com/v1/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"query":"AI web crawler API","location":"US","language":"en","limit":20}'
```

### Node

```bash
node -e '
const fs=require("fs");
const apiKey=JSON.parse(fs.readFileSync(process.env.HOME+"/.xcrawl/config.json","utf8")).XCRAWL_API_KEY;
const body={query:"web scraping pricing",location:"DE",language:"de",limit:30};
fetch("https://run.xcrawl.com/v1/search",{
  method:"POST",
  headers:{"Content-Type":"application/json",Authorization:`Bearer ${apiKey}`},
  body:JSON.stringify(body)
}).then(async r=>{console.log(await r.text());});
'
```

## Request Parameters

### Request endpoint and headers

- Endpoint: `POST https://run.xcrawl.com/v1/search`
- Headers:
- `Content-Type: application/json`
- `Authorization: Bearer <api_key>`

### Request body: top-level fields

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `query` | string | Yes | - | Search query |
| `location` | string | No | `US` | Location (country/city/region name or ISO code; best effort) |
| `language` | string | No | `en` | Language (ISO 639-1) |
| `limit` | integer | No | `10` | Max results (`1-100`) |

## Response Parameters

| Field | Type | Description |
|---|---|---|
| `search_id` | string | Task ID |
| `endpoint` | string | Always `search` |
| `version` | string | Version |
| `status` | string | `completed` |
| `query` | string | Search query |
| `data` | object | Search result data |
| `started_at` | string | Start time (ISO 8601) |
| `ended_at` | string | End time (ISO 8601) |
| `total_credits_used` | integer | Total credits used |

`data` notes from current API reference:

- Concrete result schema is implementation-defined
- Includes billing fields like `credits_used` and `credits_detail`

## Workflow

1. Rewrite the request as a clear search objective.
- Include entity, geography, language, and freshness intent.

2. Build and execute `POST /v1/search`.
- Keep request explicit and deterministic.

3. Return raw API response directly.
- Do not synthesize relevance summaries unless requested.

## Output Contract

Return:

- Endpoint used (`POST /v1/search`)
- `request_payload` used for the request
- Raw response body from search call
- Error details when request fails

Do not generate summaries unless the user explicitly requests a summary.

## Guardrails

- Do not claim ranking guarantees that the API does not expose.
- Do not fabricate unavailable filters or response fields.
- Do not hardcode provider-specific tool schemas in core logic.

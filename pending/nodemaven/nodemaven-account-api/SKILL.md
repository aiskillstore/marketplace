---
name: nodemaven-account-api
description: Call the NodeMaven dashboard REST API (v2) - traffic left, usage statistics, top domains, the location catalogue (countries, regions, cities, ISPs, zip codes), sub-users and whitelisted IPs. Covers authentication, paging, date format and the endpoints' quirks. Use when the user wants to read their NodeMaven account, automate sub-users or IP whitelisting, or look up valid location codes, from any language or curl.
license: MIT
---

# NodeMaven account API

Base URL: `https://dashboard.nodemaven.com/api/v2/base/`

Authentication is an API key from the dashboard profile, sent as

```
Authorization: x-api-key <KEY>
```

Not `Bearer`, not an `X-API-Key` header. Keep the key in an environment variable
(the SDKs read `NODEMAVEN_APIKEY`). In Python, Rust or Go use the SDK client
(`nodemaven-sdk` skill) instead of raw HTTP; it handles everything below.

**`users/me` and `sub-users/` return proxy passwords in clear text.** Never print,
log or paste a whole response body from this API. Extract the fields you need.

## Endpoints

| method and path | what it is |
|---|---|
| `GET users/me` | the account. `data` is the traffic left; `is_traffic_frozen` is a string, not a bool |
| `GET locations/countries/` | countries; filters `name`, `code`, `connection_type` |
| `GET locations/regions/?country__code=us` | regions of a country |
| `GET locations/cities/?country__code=us&region__code=...` | cities |
| `GET locations/isps/?country__code=us` | ISPs |
| `GET locations/zipcodes/?country__code=us` | zip codes |
| `GET locations/isps/regions/`, `isps/cities/`, `zipcodes/regions/`, `zipcodes/cities/` | where the ISP and zip catalogues have coverage |
| `GET statistics/data/?proxy_username=...` | traffic over time |
| `GET statistics/requests/?proxy_username=...` | requests over time |
| `GET statistics/domains/?proxy_username=...` | traffic per domain |
| `GET sub-users/` | sub-users |
| `POST sub-users/` | create: `proxy_username`, `proxy_password`, optional `is_traffic_limited`, `traffic_limit` |
| `PUT sub-users/` | update: `id` plus the fields to change (PUT to the collection, not to `sub-users/{id}`) |
| `DELETE sub-users/?id=...` | delete; the id is a query parameter |
| `POST sub-users/reset/usage` | `{"ids": [...]}`, a list even for one |
| `GET whitelist/ips` | whitelisted IPs (no trailing slash) |
| `POST whitelist/ip/upsert` | add or update: `ip`, `ports_count`, **`protocol`** (`HTTP` or `SOCKS5`), optional `name`, `country`, ... |
| `GET whitelist/ip/{id}`, `DELETE whitelist/ip/{id}` | one entry |

Location filters use the server's own spelling, `country__code` and
`region__code`. **An unknown query parameter is ignored**, so a misspelt filter
returns the unfiltered list with no error.

## Quirks that break generated clients

- **Statistics dates are `dd-mm-yyyy`**: `start=01-10-2026&end=07-10-2026`. ISO
  dates (`2026-10-01`) are answered 400 even though the published schema says
  `format: date`. Instead of dates, `period=today` or `period=hours24`. With no
  `start`, `end` or `period` at all, the statistics endpoints answer 500.
- **`protocol` is required on `whitelist/ip/upsert`** although the schema gives
  it a default. Without it the answer is 400 "Please enter a valid protocol".
  Success is `201` with `{ip_id, message}`; the listing calls the same id `id`.
- **Three paging styles.** Location endpoints: `limit` and `offset`, at most
  1000 rows a page (US cities need more than one page). `sub-users/`: `page` and
  `per_page`, from 1, an empty page past the end. `whitelist/ips`: `page` and
  `page_size`, from 1, **404 past the end**. Stop on an empty page, not on a
  short one.
- **Envelopes differ by endpoint**: rows are under `results` on the location
  endpoints and under `payload` on `sub-users/`, and `reset/usage` answers a
  `payload` list where others carry an object. No list endpoint returns a total
  count. Read the actual response shape before indexing into it.
- `POST sub-users/` answers 201; `DELETE sub-users/` answers 200 with a body.
- **An unregistered path answers `302` to `/not-found`.** An HTTP client that
  follows redirects turns a wrong path into a 200 HTML page. Disable redirects
  and treat a 3xx or a non-JSON body as an error. Following redirects would also
  send the API key to wherever the redirect points.
- Errors come as `{"error": {"code", "message", "retryable"}}`; a rejected key
  is 401 `invalid_api_key`.
- Deleting a whitelisted IP and adding the same IP again right away can be
  refused with "IP is already whitelisted" for a while after the delete.

## curl

```bash
curl -s --max-redirs 0 -H "Authorization: x-api-key $NODEMAVEN_APIKEY" \
  "https://dashboard.nodemaven.com/api/v2/base/statistics/data/?proxy_username=$NODEMAVEN_LOGIN&start=01-10-2026&end=07-10-2026"
```

```bash
curl -s --max-redirs 0 -X POST -H "Authorization: x-api-key $NODEMAVEN_APIKEY" \
  -H "Content-Type: application/json" \
  -d '{"ip": "203.0.113.7", "ports_count": 10, "protocol": "HTTP", "name": "office"}' \
  https://dashboard.nodemaven.com/api/v2/base/whitelist/ip/upsert
```

From an AI client, the `nodemaven-mcp` server exposes `account_status`,
`traffic_stats`, `top_domains`, `list_locations`, `list_sub_users` and
`list_whitelist_ips`, with passwords removed from every result. Its sub-user and
whitelist write tools work only when the server runs with
`NODEMAVEN_MCP_ALLOW_WRITE=1`.

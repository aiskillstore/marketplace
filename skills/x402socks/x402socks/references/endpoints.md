# Endpoints and client snippets

All shapes below were verified against the live service. Fields are additive-compatible; treat unknown fields as ignorable.

## Discovery

| Method | URL                                       | Notes                                    |
| ------ | ----------------------------------------- | ---------------------------------------- |
| GET    | `https://x402socks.com/llms.txt`           | Agent overview and policy                |
| GET    | `https://x402socks.com/.well-known/x402`   | Static payment metadata                  |
| GET    | `https://x402socks.com/faq`                | Human-facing help                        |
| GET    | `https://x402socks.com/status`             | Status, release notes, evidence boundaries |
| GET    | `https://payments.x402socks.com/openapi.json` | OpenAPI 3.1 contract for payable routes |

`/.well-known/x402` is a static summary. The live `PAYMENT-REQUIRED` header on a 402 is authoritative whenever the two disagree.

## Service state

### `GET /api/health`

```json
{ "status": "ok", "service": "proxy-web", "version": "0.5.65" }
```

### `GET /api/nodes` and `GET /nodes.json`

`/nodes.json` returns `{"nodes": [...]}`; `/api/nodes` exposes the same data.

```json
{
  "id": "us-central1",
  "hostname": "https://us-central1.x402socks.com",
  "port": 1080,
  "health": "healthy",
  "disabled": false,
  "latitude": 32.7831,
  "longitude": -96.8065,
  "label": "US Texas"
}
```

Filter on `disabled == false` and `health == "healthy"`. The feed is dynamic: disabled and unhealthy entries appear and disappear as nodes are toggled, so never cache the set or infer how many exits exist.

### `GET /catalog.json` and `GET /packages.json`

```json
{
  "catalog_version": 1,
  "currency": "USD",
  "packages": [
    {
      "id": "time_6h",
      "name": "6 Hours",
      "family": "Time",
      "price_usd": 1,
      "duration_hours": 6,
      "max_bytes": 1073741824,
      "max_sessions": 1,
      "entitlements": ["Up to 1 GB data", "All exit points", "1 active session"]
    }
  ]
}
```

The response carries `catalog_digest` and `content_sha256`. Pin the digest if you want to detect that prices changed between quote and purchase. Internal-visibility packages are excluded from this public feed.

## Credentials

### `POST /api/token/status`

```bash
curl -sS -X POST https://x402socks.com/api/token/status \
  -H 'content-type: application/json' -d '{"token":"..."}'
```

Body field is `token`. An `Authorization: Bearer` header alone returns `400 invalid_request`, so send the JSON body.

Success returns the account and usage. Failure:

```json
{ "error": "invalid_token", "code": "invalid_token", "request_id": "86dff920d63dd7de" }
```

### `POST /api/token/validate`

Same body. Returns **204 No Content** on success, `401` otherwise. Cheap liveness check — prefer it over `status` in retry loops.

### `POST https://api.x402socks.com/api/v1/token/rotate`

```bash
curl -sS -X POST https://api.x402socks.com/api/v1/token/rotate \
  -H "Authorization: Bearer $X402SOCKS_TOKEN"
```

Success: `200 {"account":{...},"token":"NEW_TOKEN"}`. The old token stops working immediately, for the proxy and every other route. Unknown, inactive, or expired tokens get `401 "a valid token is required"` and nothing changes.

## Purchasing

### `POST https://payments.x402socks.com/v1/access/{package_id}`

Body: `{}` (empty JSON object, no other fields). Secrets go in headers, never the body.

| Response | Meaning                                                     |
| -------- | ----------------------------------------------------------- |
| `200`    | Provisioned; `{"account":...,"token":...}` returned once     |
| `402`    | Challenge; retry with `PAYMENT-SIGNATURE`                    |
| `404`    | `{"error":{"code":"package_not_found",...}}`                 |
| `502`    | Payment settled but provisioning failed — do not repay       |

Note the two error envelopes: the web API returns a flat `{"error":"code","code":"...","request_id":"..."}`, while the payments API returns a nested `{"error":{"code","message"},"request_id":"..."}`. Handle both.

### `POST https://payments.x402socks.com/v1/access/recover`

See `payments.md`. Not listed in `openapi.json` because it is not payable.

## Client snippets

### curl (SOCKS5)

```bash
export X402SOCKS_TOKEN='...'
curl --proxy socks5h://us-central1.x402socks.com:1080 \
     --proxy-user "$X402SOCKS_TOKEN:$X402SOCKS_TOKEN" \
     https://api.ipify.org
```

### curl (HTTP CONNECT, port 3128)

```bash
curl --proxy http://us-central1.x402socks.com:3128 \
     --proxy-user "$X402SOCKS_TOKEN:$X402SOCKS_TOKEN" \
     https://api.ipify.org
```

### Python requests

```python
import os, requests

t = os.environ["X402SOCKS_TOKEN"]
proxies = {
    "http":  f"socks5h://{t}:{t}@us-central1.x402socks.com:1080",
    "https": f"socks5h://{t}:{t}@us-central1.x402socks.com:1080",
}
print(requests.get("https://api.ipify.org", proxies=proxies, timeout=30).text)
```

Requires `pip install "requests[socks]"`.

### Node (undici, HTTP CONNECT variant)

```js
import { ProxyAgent, request } from "undici";

const t = process.env.X402SOCKS_TOKEN;
const dispatcher = new ProxyAgent({
  uri: "http://us-central1.x402socks.com:3128",
  token: `Basic ${Buffer.from(`${t}:${t}`).toString("base64")}`,
});

const { body } = await request("https://api.ipify.org", { dispatcher });
console.log(await body.text());
```

undici's `ProxyAgent` speaks HTTP CONNECT, not SOCKS5. For SOCKS5 in Node, use `socks-proxy-agent` with `http`/`https` (not undici), or stay on the 3128 variant.

### Playwright

```js
const browser = await chromium.launch({
  proxy: {
    server: "socks5://us-central1.x402socks.com:1080",
    username: process.env.X402SOCKS_TOKEN,
    password: process.env.X402SOCKS_TOKEN,
  },
});
```

### Chrome

```bash
--proxy-server=http://us-central1.x402socks.com:3128
```

Chrome shows its own credential dialog after the first `407`. Enter the token as **both** username and password.

## Rate limits and secrecy

- The proxy endpoints expect the token in SOCKS5 RFC 1929 or `Proxy-Authorization`, never in a query string.
- The recovery route is rate-limited.
- `PAYMENT-RESPONSE` on a successful purchase contains settlement metadata. Store the tx hash; it is your only recovery key.

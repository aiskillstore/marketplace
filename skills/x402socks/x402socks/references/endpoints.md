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
# The token is in argv here, so other local processes can see it.
# In real clients read it from a 0600 file and pass curl options via --config -
curl -sS -X POST https://x402socks.com/api/token/status \
  -H 'content-type: application/json' -d '{"token":"..."}'
```

Body field is `token`. An `Authorization: Bearer` header alone returns `400 invalid_request`, so send the JSON body.

Safer form, with the token read from the file and the request body supplied on stdin:

```bash
umask 077
cfg="$(mktemp)"; trap 'rm -f "$cfg"' EXIT
printf 'header = "content-type: application/json"\ndata = "%s"\n' \
  "$(python3 -c 'import json,sys; print(json.dumps({"token": sys.stdin.read()}))' \
      < ~/.config/x402socks/token)" > "$cfg"
curl --config "$cfg" -X POST https://x402socks.com/api/token/status
```

Success returns the account and usage. Failure:

```json
{ "error": "invalid_token", "code": "invalid_token", "request_id": "86dff920d63dd7de" }
```

### `POST /api/token/validate`

Same body. Returns **204 No Content** on success, `401` otherwise. Cheap liveness check — prefer it over `status` in retry loops.

### `POST https://api.x402socks.com/api/v1/token/rotate`

```bash
# Token as an argument is visible in the process list. Use a 0600 config file:
umask 077
cfg="$(mktemp)"; trap 'rm -f "$cfg"' EXIT
printf 'header = "Authorization: Bearer %s"\n' "$(cat ~/.config/x402socks/token)" > "$cfg"
curl --config "$cfg" -X POST https://api.x402socks.com/api/v1/token/rotate
```

Success: `200 {"account":{...},"token":"NEW_TOKEN"}`. The old token stops working immediately, for the proxy and every other route. Unknown, inactive, or expired tokens get `401 "a valid token is required"` and nothing changes.

The response contains the replacement token. Write it to a `0600` file rather
than printing it; `scripts/x402socks.sh rotate` does that and emits a redacted
copy of the response.

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

`curl --proxy-user "$TOKEN:$TOKEN"` puts the token in the process list. Keep it
in a `0600` config file instead:

```bash
umask 077
cfg="$(mktemp)"; trap 'rm -f "$cfg"' EXIT
{
  printf 'proxy = "socks5h://us-central1.x402socks.com:1080"\n'
  printf 'proxy-user = "%s:%s"\n' \
    "$(cat ~/.config/x402socks/token)" "$(cat ~/.config/x402socks/token)"
} > "$cfg"
curl --config "$cfg" https://api.ipify.org
```

SOCKS5 RFC 1929 authentication is not encrypted. Treat the client-to-exit hop as
observable on a shared network and keep tokens short-lived.

### curl (HTTP CONNECT)

TLS listener, preferred where available (`eu-north1`, `asia-west1`, `asia-central2`):

```bash
# same 0600 config pattern as above, with:
# proxy = "https://eu-north1.x402socks.com:3129"
curl --config "$cfg" https://api.ipify.org
```

Plaintext listener on 3128 (`us-central1`, `eu-central1`, `asia-central2`). The
token crosses the client-to-node hop unencrypted; use it only on a trusted
network:

```bash
# proxy = "http://us-central1.x402socks.com:3128"
```

### Python requests

```python
import os, requests

t = open(os.path.expanduser("~/.config/x402socks/token")).read().strip()
proxies = {
    "http":  f"socks5h://{t}:{t}@us-central1.x402socks.com:1080",
    "https": f"socks5h://{t}:{t}@us-central1.x402socks.com:1080",
}
print(requests.get("https://api.ipify.org", proxies=proxies, timeout=30).text)
```

Requires `pip install "requests[socks]"`. SOCKS5 credentials are sent in
cleartext on the client-to-exit hop, so avoid untrusted networks.

### Node (undici, HTTP CONNECT variant)

```js
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { ProxyAgent, request } from "undici";

const t = readFileSync(`${homedir()}/.config/x402socks/token`, "utf8").trim();
const dispatcher = new ProxyAgent({
  // TLS listener: the token is not sent in cleartext on this hop.
  uri: "https://eu-north1.x402socks.com:3129",
  token: `Basic ${Buffer.from(`${t}:${t}`).toString("base64")}`,
});

const { body } = await request("https://api.ipify.org", { dispatcher });
console.log(await body.text());
```

undici's `ProxyAgent` speaks HTTP CONNECT, not SOCKS5. For SOCKS5 in Node, use `socks-proxy-agent` with `http`/`https` (not undici), or stay on the CONNECT variant. On the plaintext 3128 listener the token is unencrypted.

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

Playwright's SOCKS5 authentication is not encrypted either; the token still
crosses the client-to-exit hop in the clear.

### Chrome

```bash
--proxy-server=https://eu-north1.x402socks.com:3129
```

Chrome shows its own credential dialog after the first `407`. Enter the token as **both** username and password. Use the `http://…:3128` form only on a trusted network.

## Rate limits and secrecy

- The proxy endpoints expect the token in SOCKS5 RFC 1929 or `Proxy-Authorization`, never in a query string.
- The recovery route is rate-limited.
- `PAYMENT-RESPONSE` on a successful purchase contains settlement metadata. Store the tx hash; it is your only recovery key.

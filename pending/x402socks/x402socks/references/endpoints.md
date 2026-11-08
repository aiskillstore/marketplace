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

## Transport

TLS HTTP CONNECT on **TCP 3129** is the preferred transport and is available on `eu-north1`, `asia-central2`, and `asia-west1`:

```
https://<exit>.x402socks.com:3129
```

The client verifies the exit certificate, then sends `Proxy-Authorization` inside the TLS tunnel to the exit. The reusable token is not readable on the client-to-exit hop.

**SOCKS5 on 1080** is the primary protocol and is available on every exit. **TLS HTTP CONNECT on 3129** (above) is preferred where available. Plaintext HTTP CONNECT on **3128** is supported only for browser compatibility and will be **discontinued shortly**. Both legacy transports send the reusable token unencrypted on the client-to-exit hop and are **opt-in only**: the helper requires `X402SOCKS_ALLOW_PLAINTEXT=1` before it will use either. Use them only when a client cannot do TLS CONNECT and the network is trusted.

## Legacy transport addresses (for browser compatibility only)

| Transport | Address | Notes |
| --------- | ------- | ----- |
| Plaintext HTTP CONNECT | `http://<exit>.x402socks.com:3128` | Every exit |
| SOCKS5 | `socks5h://<exit>.x402socks.com:1080` | Every exit |

When using these legacy transports, the token is sent in cleartext on the client-to-proxy hop. Do not use unless necessary for browser compatibility and the network is trusted.

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

Send the token in a JSON body. Build the body from the `0600` file into a
temporary payload file so the token never reaches argv and the JSON is not
hand-quoted into a curl config line:

```bash
umask 077
payload="$(mktemp)"; trap 'rm -f "$payload"' EXIT
python3 -c 'import json,sys; print(json.dumps({"token": open(sys.argv[1]).read().strip()}))' \
  "$HOME/.config/x402socks/token" > "$payload"
curl -sS -X POST https://x402socks.com/api/token/status \
  -H 'content-type: application/json' --data-binary "@$payload"
```

The body field is `token`. An `Authorization: Bearer` header alone returns `400 invalid_request`, so send the JSON body.

Success returns the account and usage. Failure:

```json
{ "error": "invalid_token", "code": "invalid_token", "request_id": "86dff920d63dd7de" }
```

### `POST /api/token/validate`

Same body. Returns **204 No Content** on success, `401` otherwise. Cheap liveness check — prefer it over `status` in retry loops.

### `POST https://api.x402socks.com/api/v1/token/rotate`

```bash
# Saves the replacement token atomically to the 0600 token file and prints a
# redacted response. The old token stops working immediately.
scripts/x402socks.sh rotate
```

Success: `200 {"account":{...},"token":"NEW_TOKEN"}`. The old token stops working immediately, for the proxy and every other route. Unknown, inactive, or expired tokens get `401 "a valid token is required"` and nothing changes.

The replacement token is the only copy. If you call the endpoint directly, capture the response yourself and write it to the `0600` file before any output reaches a terminal, transcript, or log — do not print the raw JSON.

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

Before signing, compare every `accepts[]` entry against the terms you got
approved: `scheme`, `network`, `asset`, `payTo`, `extra.name`,
`extra.version`, and `amount`. Reject the payment if any advertised option
falls outside the approval or if the list is ambiguous. See `payments.md`.

### `POST https://payments.x402socks.com/v1/access/recover`

See `payments.md`. Not listed in `openapi.json` because it is not payable.

## Client snippets

All snippets read the token from the `0600` file and use **TLS CONNECT**. None of
them puts the token in a command argument.

### curl (TLS CONNECT, recommended)

```bash
umask 077
cfg="$(mktemp)"; trap 'rm -f "$cfg"' EXIT
{
  printf 'proxy = "https://eu-north1.x402socks.com:3129"\n'
  printf 'proxy-user = "%s:%s"\n' \
    "$(cat ~/.config/x402socks/token)" "$(cat ~/.config/x402socks/token)"
} > "$cfg"
curl --config "$cfg" https://api.ipify.org
```

`curl` verifies the exit certificate by default. If that check fails, the exit
is not usable — do not disable verification or fall back to plaintext.

### Python (urllib3, TLS CONNECT) — token sent via `Proxy-Authorization`, never in a URL

```python
import os, base64, urllib3

token = open(os.path.expanduser("~/.config/x402socks/token")).read().strip()
auth = base64.b64encode(f"{token}:{token}".encode()).decode()

http = urllib3.ProxyManager(
    "https://eu-north1.x402socks.com:3129",
    proxy_headers={"Proxy-Authorization": f"Basic {auth}"},
)
print(http.request("GET", "https://api.ipify.org").data.decode())
```

This needs `urllib3` 2.0+, which supports an HTTPS proxy. The token is put in a `Proxy-Authorization` header, not embedded in a URL; if the request does not send it on your urllib3 version, fall back to the `requests` snippet above and add "do not log the proxy URL / token" beside it.
The token stays in process memory; it is not placed in argv.

### Node (undici, TLS CONNECT)

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

undici's `ProxyAgent` speaks HTTP CONNECT, not SOCKS5.

### Playwright (TLS CONNECT)

Chromium cannot authenticate to a SOCKS5 proxy, and Playwright's
`proxy.username` / `proxy.password` only apply to HTTP(S) proxies. A
`socks5://` entry with credentials fails before it connects. Use the TLS HTTP
CONNECT listener:

```js
import { readFileSync } from "node:fs";
import { homedir } from "node:os";

const t = readFileSync(`${homedir()}/.config/x402socks/token`, "utf8").trim();

const browser = await chromium.launch({
  proxy: {
    server: "https://eu-north1.x402socks.com:3129", // TLS CONNECT, not SOCKS5
    username: t,
    password: t,
  },
});
```

### Chrome

```bash
--proxy-server=https://eu-north1.x402socks.com:3129
```

Chrome shows its own credential dialog after the first `407`. Enter the token as **both** username and password.

### Legacy plaintext transports (opt-in)

Only if the client cannot use TLS CONNECT, and only on a network you trust.
The helper exposes both under `test --plaintext` / `test --socks5` with
`X402SOCKS_ALLOW_PLAINTEXT=1`; see `scripts/x402socks.sh help`. For hand-written
clients, use the addresses in the transport table above with the token as both
username and password. Both put the reusable token on the wire in cleartext; a
successful TLS request does not protect that hop.

## Rate limits and secrecy

- The proxy endpoints expect the token in SOCKS5 RFC 1929 or `Proxy-Authorization`, never in a query string.
- The recovery route is rate-limited.
- `PAYMENT-RESPONSE` on a successful purchase contains settlement metadata. Store the tx hash; it is your only recovery key.

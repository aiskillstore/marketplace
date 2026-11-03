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

The other exits and the legacy transports are **opt-in**:

| Transport              | Address                                   | Availability                          | Token on the wire        |
| ---------------------- | ----------------------------------------- | ------------------------------------- | ------------------------ |
| TLS HTTP CONNECT       | `https://<exit>.x402socks.com:3129`       | `eu-north1`, `asia-central2`, `asia-west1` | Encrypted (recommended)  |
| HTTP CONNECT, plaintext| `http://<exit>.x402socks.com:3128`        | every exit                            | Cleartext                |
| SOCKS5 (RFC 1929)      | `socks5h://<exit>.x402socks.com:1080`     | every exit                            | Cleartext                |

Both legacy transports send the token unencrypted. A passive observer on the same network can capture it and spend the remaining balance. Use them only when a client cannot do TLS CONNECT and the network is trusted; `scripts/x402socks.sh` requires `X402SOCKS_ALLOW_PLAINTEXT=1` before it will use either.

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
# Token goes through stdin into curl's --config, never into argv.
printf 'header = "Authorization: Bearer %s"\n' \
  "$(cat ~/.config/x402socks/token)" | \
curl -sS --config - -X POST https://api.x402socks.com/api/v1/token/rotate
```

Success: `200 {"account":{...},"token":"NEW_TOKEN"}`. The old token stops working immediately, for the proxy and every other route. Unknown, inactive, or expired tokens get `401 "a valid token is required"` and nothing changes.

The response contains the replacement token. Write it to a `0600` file rather than printing it; `scripts/x402socks.sh rotate` does that and emits a redacted copy of the response.

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

### Python (requests, TLS CONNECT)

```python
import os
import requests

token = open(os.path.expanduser("~/.config/x402socks/token")).read().strip()
proxy = f"https://{token}:{token}@eu-north1.x402socks.com:3129"

print(
    requests.get(
        "https://api.ipify.org",
        proxies={"http": proxy, "https": proxy},
        timeout=30,
    ).text
)
```

This needs `requests` 2.26+ and `urllib3` 2.0+, which support an HTTPS proxy.
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

Only if the client cannot use TLS CONNECT, and only on a network you trust:

```bash
# HTTP CONNECT without TLS
X402SOCKS_ALLOW_PLAINTEXT=1 scripts/x402socks.sh test --plaintext us-central1

# SOCKS5 with RFC 1929 user/password
X402SOCKS_ALLOW_PLAINTEXT=1 scripts/x402socks.sh test --socks5 us-central1
```

The helper prints a warning when either is selected. For hand-written clients,
the equivalent URLs are `http://<exit>.x402socks.com:3128` and
`socks5h://<exit>.x402socks.com:1080` with the token as both username and
password. Both put the reusable token on the wire in cleartext; a successful
TLS request does not protect that hop.

## Rate limits and secrecy

- The proxy endpoints expect the token in SOCKS5 RFC 1929 or `Proxy-Authorization`, never in a query string.
- The recovery route is rate-limited.
- `PAYMENT-RESPONSE` on a successful purchase contains settlement metadata. Store the tx hash; it is your only recovery key.

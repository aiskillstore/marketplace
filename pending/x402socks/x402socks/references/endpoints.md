# Endpoints and client snippets

All shapes below were verified against the live service. Fields are
additive-compatible; treat unknown fields as ignorable. For wallet setup and
`cast`, see `wallet.md`.

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

**TLS HTTP CONNECT on 3129** (`https://<exit>.x402socks.com:3129`) is the only
transport this skill uses: the exit presents a valid certificate and curl
verifies it, so the token is encrypted on the client-to-exit hop. It is available
on `eu-north1`, `asia-central2`, and `asia-west1`.

SOCKS5 (1080) and plaintext HTTP CONNECT (3128) exist for legacy browser clients
only. Both send the reusable token unencrypted on the client-to-exit hop, so this
skill does not use them and the helper does not expose them. Do not add a
plaintext or SOCKS5 step to an agent workflow; if a client cannot do TLS CONNECT,
stop and ask the operator rather than downgrading the transport.

## Legacy transport addresses (browser compatibility only)

| Transport | Address | Notes |
| --------- | ------- | ----- |
| Plaintext HTTP CONNECT | `http://<exit>.x402socks.com:3128` | Browser clients only; token in cleartext |
| SOCKS5 | `socks5h://<exit>.x402socks.com:1080` | Browser clients only; token in cleartext |

These addresses exist so a browser that cannot do TLS CONNECT still has an
option. They are not part of this skill's workflow, and a successful TLS request
through them does not protect the token on the proxy hop.

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

Credential-bearing requests (status, validate, rotate, recover, and the pre-test
token check) must target `https://` on an `x402socks.com` host. The helper
refuses a plaintext or non-x402socks `X402SOCKS_WEB`, `X402SOCKS_API`, or
`X402SOCKS_PAY` override before it reads the token or signature, and its curl
invocations restrict the transfer and redirects to HTTPS so a credential request
cannot be silently downgraded. Do not move these routes to HTTP.
`X402SOCKS_ALLOW_INSECURE_API=1` exists only for a trusted local test harness and
is not a safe way to reach the public service.

### `POST /api/token/status`

Send the token in a JSON body. Build the body from the `0600` file into a
temporary payload file so the token never reaches argv and the JSON is not
hand-quoted into a curl config line:

```bash
umask 077
payload="$(mktemp)"; trap 'rm -f "$payload"' EXIT
python3 -c 'import json,sys; print(json.dumps({"token": open(sys.argv[1]).read().strip()}))' \
  "$HOME/.config/x402socks/token" > "$payload"
curl -q -sS --proto '=https' --proto-redir '=https' \
  -X POST https://x402socks.com/api/token/status \
  -H 'content-type: application/json' --data-binary "@$payload"
```

`curl -q` ignores any ambient curl config, and the proto pins prevent a
redirect from downgrading the credential-bearing request. The body field is
`token`. An `Authorization: Bearer` header alone returns `400 invalid_request`,
so send the JSON body. Prefer `scripts/x402socks.sh status`, which prints only
an allowlisted set of account and usage fields.

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
`extra.version`, and `amount`. Also require the exact request URL, package ID,
challenge `resource`, and signer public address to match the approval. Reject
the payment if any advertised option falls outside the approval, if the list is
ambiguous, or if a later 402 appears after a signed authorization. See
`payments.md`.

### `POST https://payments.x402socks.com/v1/access/recover`

See `payments.md`. Not listed in `openapi.json` because it is not payable.

## Client snippets

All snippets read the token from the `0600` file and use **TLS CONNECT**. None of
them puts the token in a command argument. Each snippet also requires an explicit
target allowlist in `X402SOCKS_ALLOWED_HOSTS` and refuses an empty list or a
non-HTTPS target. A proxy changes the source IP, not permission to access a site.
Obey the destination's access rules and do not use rotating egress to evade a
block, rate limit, or access decision.

### curl (TLS CONNECT, recommended)

```bash
umask 077
cfg="$(mktemp)"; trap 'rm -f "$cfg"' EXIT
{
  printf 'proxy = "https://eu-north1.x402socks.com:3129"\n'
  printf 'proxy-user = "%s:%s"\n' \
    "$(cat ~/.config/x402socks/token)" "$(cat ~/.config/x402socks/token)"
} > "$cfg"
target="${X402SOCKS_TARGET_URL:-}"
python3 -c 'import os,sys
u = sys.argv[1]
allowed = [h.strip().lower() for h in os.environ.get("X402SOCKS_ALLOWED_HOSTS","").split(",") if h.strip()]
if not u.startswith("https://") or not allowed or u.split("/")[2].lower() not in allowed:
    sys.exit("target is not in X402SOCKS_ALLOWED_HOSTS")' "$target"
curl -q --proto '=https' --proto-redir '=https' --config "$cfg" "$target"
```

`curl -q` ignores ambient curl config, so a local `~/.curlrc` cannot add an
output or tracing option that exposes the proxy credentials. The proto pins
block plaintext redirects. `curl` verifies the exit certificate by default. If
that check fails, the exit is not usable, do not disable verification or fall
back to plaintext.

### Python (urllib3, TLS CONNECT) — token sent via `Proxy-Authorization`, never in a URL

```python
import os, base64, urllib3
from urllib.parse import urlparse

token = open(os.path.expanduser("~/.config/x402socks/token")).read().strip()
auth = base64.b64encode(f"{token}:{token}".encode()).decode()

target = os.environ.get("X402SOCKS_TARGET_URL", "")
allowed = {h.strip().lower() for h in os.environ.get("X402SOCKS_ALLOWED_HOSTS", "").split(",") if h.strip()}
u = urlparse(target)
if u.scheme != "https" or not allowed or (u.hostname or "").lower() not in allowed:
    raise SystemExit("target is not in X402SOCKS_ALLOWED_HOSTS")

http = urllib3.ProxyManager(
    "https://eu-north1.x402socks.com:3129",
    proxy_headers={"Proxy-Authorization": f"Basic {auth}"},
)
print(http.request("GET", target).data.decode())
```

This needs `urllib3` 2.0+, which supports an HTTPS proxy. The token is put in a
`Proxy-Authorization` header, not embedded in a URL. If the request does not send
it on your urllib3 version, use a client that sends `Proxy-Authorization`
explicitly and keep the token out of the proxy URL. The token stays in process
memory; it is not placed in argv.

### Node (undici, TLS CONNECT)

```js
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { ProxyAgent, request } from "undici";

const t = readFileSync(`${homedir()}/.config/x402socks/token`, "utf8").trim();
const target = process.env.X402SOCKS_TARGET_URL ?? "";
const allowed = (process.env.X402SOCKS_ALLOWED_HOSTS ?? "")
  .split(",").map(h => h.trim().toLowerCase()).filter(Boolean);
const parsed = new URL(target);
if (parsed.protocol !== "https:" || !allowed.includes(parsed.hostname)) {
  throw new Error("target is not in X402SOCKS_ALLOWED_HOSTS");
}
const dispatcher = new ProxyAgent({
  // TLS listener: the token is not sent in cleartext on this hop.
  uri: "https://eu-north1.x402socks.com:3129",
  token: `Basic ${Buffer.from(`${t}:${t}`).toString("base64")}`,
});

const { body } = await request(target, { dispatcher });
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
const target = process.env.X402SOCKS_TARGET_URL ?? "";
const allowed = (process.env.X402SOCKS_ALLOWED_HOSTS ?? "")
  .split(",").map(h => h.trim().toLowerCase()).filter(Boolean);
const parsed = new URL(target);
if (parsed.protocol !== "https:" || !allowed.includes(parsed.hostname)) {
  throw new Error("target is not in X402SOCKS_ALLOWED_HOSTS");
}

const browser = await chromium.launch({
  proxy: {
    server: "https://eu-north1.x402socks.com:3129", // TLS CONNECT, not SOCKS5
    username: t,
    password: t,
  },
});
const page = await browser.newPage();
await page.goto(target);
```

### Chrome

```bash
--proxy-server=https://eu-north1.x402socks.com:3129
```

Chrome shows its own credential dialog after the first `407`. Enter the token as **both** username and password. Chrome cannot enforce the target allowlist, so the operator must check `X402SOCKS_ALLOWED_HOSTS` and the destination's access rules before launching.

### Legacy plaintext transports (not used by this skill)

The helper does not offer SOCKS5 or plaintext CONNECT: both put the reusable
token on the wire in cleartext, and a successful TLS request to the target does
not protect that hop. They exist only for a browser that cannot do TLS CONNECT.
If you must use one, use the addresses in the transport table above with the
token as both username and password, and only on a network you trust.

## Rate limits and secrecy

- The proxy endpoints expect the token in SOCKS5 RFC 1929 or `Proxy-Authorization`, never in a query string.
- The recovery route is rate-limited.
- `PAYMENT-RESPONSE` on a successful purchase contains settlement metadata. Store the tx hash; it is your only recovery key.

---
name: x402socks
description: Buy and use pay-per-use anonymous proxy egress for AI agents via x402socks.com, paid in USDC on Base with the x402 protocol. Use when a task needs a different source IP, rotating or geo-specific egress, or an unblocked fetch - triggers include "get a proxy", "route this through a proxy", "rotate my IP", "scrape without getting blocked", "anonymous proxy for an agent", "pay for a proxy with USDC", "x402 proxy", "x402socks", or any request for short-lived SOCKS5 egress on a per-job basis.
license: MIT
metadata:
  author: x402socks
  version: 1.0.0
  homepage: https://x402socks.com
---

# x402socks proxy access

Buy anonymous SOCKS5 egress for an agent, paying in USDC on Base through **x402** (HTTP 402). No signup, no email, no card. You pay, receive a one-time proxy token, and use that token as **both** the SOCKS5 username and password.

## Fast path

```bash
# 1. Confirm the service is up and pick a live exit
curl -s https://x402socks.com/api/health          # {"status":"ok",...}
curl -s https://x402socks.com/nodes.json          # keep nodes where disabled == false

# 2. Buy a package (x402 library does the 402 handshake) -> see references/payments.md
#    Credential comes back once: {"account":{...},"token":"..."}

# 3. Use it
curl --proxy socks5h://us-central1.x402socks.com:1080 \
     --proxy-user "$X402SOCKS_TOKEN:$X402SOCKS_TOKEN" https://api.ipify.org
```

## Spending rule — read before paying

Buying spends real money from the user's wallet. **Do not pay without explicit authorization for that specific amount.** If the user has not pre-approved a budget:

1. Look up the price in `/catalog.json`.
2. State the package, price, and what it entitles them to.
3. Wait for a clear yes.

Prefer the cheapest package that covers the job. A $1 / 6-hour token is almost always the right first purchase; upgrading later is cheaper than overbuying now.

## Pricing (live catalog, USD)

| Package ID    | Price  | Entitlements                                  |
| ------------- | ------ | --------------------------------------------- |
| `time_6h`     | $1.00  | 6 hours, 1 GB, all exits, 1 session           |
| `time_1d`     | $3.59  | 1 day, 10 GB, all exits, 1 session            |
| `time_7d`     | $9.99  | 7 days, 75 GB, all exits, 1 session           |
| `usage_5gb`   | $6.99  | 5 GB, no time limit, all exits, 1 session     |
| `usage_50gb`  | $34.99 | 50 GB, no time limit, all exits, 1 session    |
| `multi_agent` | $29.99 | 30 days, 300 GB (fair use), all exits, 5 agents |

Always re-read `/catalog.json` at buy time — the table above is a snapshot, not a contract.

**Choosing:** time-boxed plans suit a single burst; the `usage_*` plans suit intermittent jobs that would otherwise expire mid-work; `multi_agent` is the only plan that explicitly allows more than one agent.

## Steps

1. **Verify the service.** `GET /api/health` must return `{"status":"ok"}`. If a chosen exit is down, pick another from `/nodes.json`.
2. **Quote the price** from `/catalog.json` and get user approval (see spending rule).
3. **Request access.** `POST https://payments.x402socks.com/v1/access/{package_id}` with `{}`. Expect HTTP 402 plus a base64 `PAYMENT-REQUIRED` header.
4. **Pay and retry.** Select the requirement from `accepts[]`, sign an x402 v2 EIP-3009 authorization, retry the same URL with `PAYMENT-SIGNATURE`. Details and working code: `references/payments.md`.
5. **Capture the token** from the 200 response. It is returned once, and only once.
6. **Route traffic** through an exit on TCP 1080 using the token for both username and password.
7. **Validate** with `POST /api/token/status` before debugging anything else. A dead token and a dead exit look identical from a failed fetch.

A helper script ships with this skill:

```bash
scripts/x402socks.sh health
scripts/x402socks.sh nodes --available
scripts/x402socks.sh catalog --summary
scripts/x402socks.sh status            # reads $X402SOCKS_TOKEN
scripts/x402socks.sh test              # confirms egress IP actually changed
```

## Routing traffic

SOCKS5 on TCP 1080, on every exit. The fleet is not fixed — nodes are added, retired, and toggled at any time, so read `/nodes.json` and filter on `disabled == false and health == "healthy"` instead of trusting a list. Snapshot at the time of writing:

| Exit ID         | Region                |
| --------------- | --------------------- |
| `us-central1`   | US Texas              |
| `us-east1`      | US New York           |
| `us-west1`      | US California         |
| `eu-central1`   | EU Paris              |
| `eu-north1`     | EU Riga               |
| `asia-central1` | APAC China (Hong Kong) |
| `asia-central2` | APAC Singapore        |
| `asia-west1`    | APAC India            |

An HTTP CONNECT variant also runs on **port 3128** for `us-central1`, `eu-central1`, and `asia-central2` only. It is plaintext on the client-to-node hop. Use it for browsers or HTTP clients that cannot send SOCKS5 credentials.

```bash
# Python (requests)
proxies = {"http": "socks5h://TOKEN:TOKEN@us-central1.x402socks.com:1080",
           "https": "socks5h://TOKEN:TOKEN@us-central1.x402socks.com:1080"}
# requires: pip install "requests[socks]"

# Node (undici)
// use a ProxyAgent; see references/endpoints.md for the exact snippet

# Browser / HTTP client
# http://us-central1.x402socks.com:3128  (token as username AND password)
```

Prefer `socks5h://` over `socks5://` so DNS resolves at the exit rather than locally — otherwise the local resolver still leaks your target hostname.

## Credential rules (hard)

- The token is a secret. Never put it in source control, logs, analytics, browser storage, shared URLs, or shell history. Export it as an environment variable and substitute locally.
- Never echo a token into a chat transcript or a commit. If a token appears in output, treat it as burned and rotate it.
- A token in a URL (`socks5h://TOKEN:TOKEN@...`) can leak via process listings. Prefer client-level credential config or `--proxy-user` with a variable.
- Rotate on any suspicion of exposure: `scripts/x402socks.sh rotate`. Rotation invalidates the old token immediately, everywhere.

## Rotation and recovery

- **Rotate** (you still hold the token): `POST https://api.x402socks.com/api/v1/token/rotate` with `Authorization: Bearer $TOKEN`. The presented token is both the credential and the object being rotated. Update every client immediately.
- **Recover** (payment settled, token lost): `POST https://payments.x402socks.com/v1/access/recover` with the settlement tx hash and an EIP-191 signature from the paying wallet over a fixed message. Free, and safe to retry. Never pay twice for the same access — see `references/payments.md`.
- Recovery signatures expire in ±10 minutes, so generate the message, sign it, and submit promptly.

## Gotchas

- Node membership changes without notice. `/nodes.json` carries disabled and unhealthy entries alongside live ones (a node that is `disabled: true` or `health: "down"` will refuse connections). Never hardcode the exit list, its size, or which nodes are excluded — always re-read the feed.
- Entitlements say "1 active session" on single packages. Do not assume unlimited parallelism; use `multi_agent` when several agents must egress at once.
- Data caps are **fair use**. Sustained bulk transfer may be throttled or cut off.
- **Failed connections are non-refundable by default.** Validate the token and the exit before blaming the target site.
- Amounts in the 402 challenge are atomic USDC units (6 decimals): `"1000000"` is $1.00. Do not confuse them with the decimal prices in the catalog.
- The runtime challenge is authoritative for network, asset, recipient, and amount. Never hardcode them from documentation, including this file.
- Support is a Telegram channel (`https://t.me/x402socks`), not a ticket queue.

## References

- `references/payments.md` — full x402 v2 purchase flow, TypeScript and Python code, credential recovery.
- `references/endpoints.md` — every endpoint, request/response shapes, client snippets.
- `references/troubleshooting.md` — symptom-to-cause table for 402/407/401/connection errors.

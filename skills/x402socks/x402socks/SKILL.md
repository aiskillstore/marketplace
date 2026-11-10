---
name: x402socks
description: Use this skill when an agent needs a different source IP, rotating or geo-specific egress, or an unblocked fetch - for example "get a proxy", "route this through a proxy", "rotate my IP", "scrape without getting blocked", "anonymous proxy for an agent", "pay for a proxy with USDC", "x402 proxy", or "x402socks". It buys pay-per-use anonymous proxy egress from x402socks.com (TLS HTTP CONNECT by default, SOCKS5 opt-in), paid in USDC on Base with the x402 protocol.
license: MIT
metadata:
  author: x402socks
  version: 1.3.0
  homepage: https://x402socks.com
---

# x402socks proxy access

Buy anonymous proxy egress for an agent, paid per job in USDC on Base through
**x402** (HTTP 402). No signup, no email, no card. The payment returns a one-time
proxy token; use it as **both** the proxy username and password.

TLS HTTP CONNECT on port **3129** is the default where available (`eu-north1`,
`asia-central2`, `asia-west1`): the exit presents a valid certificate and curl
verifies it. SOCKS5 (1080) and plaintext HTTP CONNECT (3128) are opt-in; both
expose the reusable token on the client-to-exit hop.

## Before you start: wallet access (required)

The agent cannot buy anything without a wallet it can use.

- **Wallet:** an EVM-compatible wallet funded with **USDC on Base**. The cheapest
  package is **$1.00** (6 hours, 1 GB). No ETH is needed for an x402 purchase:
  the facilitator submits the EIP-3009 transfer. A manual `cast send` does need
  ETH for gas.
- **Signing access:** the agent needs non-interactive access to that wallet. Use
  a Foundry encrypted keystore
  (`cast wallet import <name> --interactive`, then
  `--keystore <path> --password-file <0600 file>`), a hardware wallet, or a
  signer configured in the x402 client. Do not paste a raw private key into
  chat.
- **Tools:** `cast` plus a free Base RPC for low-volume balance checks and manual
  sends, for example `https://mainnet.base.org`,
  `https://base-rpc.publicnode.com`, `https://1rpc.io/base`, or
  `https://base.drpc.org`. USDC on Base is
  `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`.
- **Never** print, echo, log, or pass the private key as a command argument. It
  must not appear in a terminal transcript, process list, log, or commit. Keep
  keystores and password files at mode `0600`.
- **No wallet access = no purchase.** There is no free trial and no way to use
  the wallet without a signer.

`references/wallet.md` has the `cast` recipes for address, USDC balance, manual
send, and EIP-712 signing.

## Fast path

```bash
scripts/x402socks.sh health                         # {"status":"ok",...}
scripts/x402socks.sh nodes --available              # usable exits only
X402SOCKS_MAX_USDC=1.00 scripts/x402socks.sh quote time_6h
# pay with the x402 client (see references/payments.md), then:
scripts/x402socks.sh save-token                     # paste token, Ctrl-D; mode 600
scripts/x402socks.sh test eu-north1                 # TLS 3129, prints egress IP
```

## Spending rule

Buying spends real money. **Do not pay without explicit authorization for that
exact amount.**

1. Read the live price from `/catalog.json` (or `quote <package_id>`).
2. Tell the user the package, price, and entitlements.
3. Wait for a clear yes.
4. Before signing, compare the live 402 `accepts[]` to the approved terms:
   `scheme`, `network`, `asset`, `payTo`, `extra.name`, `extra.version`, and
   `amount`. Abort on any mismatch or ambiguity.

An approval is an amount, not a package name. `scripts/x402socks.sh quote
<package_id>` prints the live terms and exits non-zero above
`X402SOCKS_MAX_USDC`. Start with `time_6h` ($1.00, 6 hours, 1 GB) unless the job
clearly needs more; re-read `/catalog.json` for current packages.

## Steps

1. **Check the service.** `GET /api/health` returns `{"status":"ok"}`. Pick an
   exit from `/nodes.json` with `disabled == false` and `health == "healthy"`.
2. **Quote and approve.** Run `quote <package_id>`, show the user, wait.
3. **Request access.** `POST https://payments.x402socks.com/v1/access/{package_id}`
   with `{}`. Expect `402` and a base64 `PAYMENT-REQUIRED` header.
4. **Pay.** Validate the live `accepts[]` against the approval, sign an x402 v2
   EIP-3009 authorization, and retry the same URL with `PAYMENT-SIGNATURE`.
5. **Save the token.** It is returned once as
   `{"account":{...},"token":"..."}`. Write it to a `0600` file; never print it.
6. **Route and prove.** Use TLS CONNECT on 3129 with the token as both username
   and password. `scripts/x402socks.sh test <exit>` prints the egress IP; compare
   it with your direct IP.
7. **If it fails.** Run `status` (or `validate`) before debugging the target. A
   dead token and a dead exit look identical.

## Using the token

```bash
# Helper: TLS CONNECT by default, token read from the 0600 file, never argv
scripts/x402socks.sh test eu-north1

# curl: put the proxy credentials in a 0600 config file, not argv
umask 077
cfg="$(mktemp)"; trap 'rm -f "$cfg"' EXIT
{
  printf 'proxy = "https://eu-north1.x402socks.com:3129"\n'
  printf 'proxy-user = "%s:%s"\n' \
    "$(cat ~/.config/x402socks/token)" "$(cat ~/.config/x402socks/token)"
} > "$cfg"
curl --config "$cfg" https://api.ipify.org
```

For SOCKS5 use `socks5h://<exit>.x402socks.com:1080` so the exit resolves DNS.
SOCKS5 and plaintext CONNECT (3128) require `X402SOCKS_ALLOW_PLAINTEXT=1` in the
helper and send the token unencrypted; use them only when a client cannot do TLS
CONNECT and the network is trusted. Python, Node, Playwright, and Chrome examples
are in `references/endpoints.md`.

## Credential rules (hard)

- Store the token in a `0600` file (`X402SOCKS_TOKEN_FILE`, default
  `~/.config/x402socks/token`) or an environment variable. Never put it in source
  control, logs, analytics, browser storage, shared URLs, or shell history.
- Never pass the token as a command argument. Feed it through stdin or a `0600`
  config file; the helper does this for curl.
- Never echo a token into a chat, transcript, or commit. If one appears in
  output, treat it as burned and rotate it.
- Prefer TLS CONNECT on 3129. Rotate on suspicion:
  `scripts/x402socks.sh rotate` invalidates the old token immediately and saves
  the replacement without printing it.
- Credential-bearing requests only go to `https://`. The helper refuses a
  plaintext `X402SOCKS_WEB`, `X402SOCKS_API`, or `X402SOCKS_PAY` override before
  reading the token, and pins curl to HTTPS. `X402SOCKS_ALLOW_INSECURE_API=1` is
  for a trusted local test only.

## Gotchas

- `/nodes.json` is live; never hardcode the exit list or assume how many exist.
- Single packages allow **one active session**. Use `multi_agent` for parallel
  agents.
- Data caps are fair use; sustained bulk transfer may be throttled.
- Failed connections are non-refundable by default; validate first.
- 402 amounts are atomic USDC (6 decimals): `"1000000"` = $1.00. The runtime
  challenge is authoritative for network, asset, recipient, and amount - never
  hardcode them.
- Support: https://t.me/x402socks.

## References

- `references/wallet.md` - wallet access, `cast`, free Base RPCs, key handling.
- `references/payments.md` - x402 v2 flow, approval pinning, recovery.
- `references/endpoints.md` - endpoints, client snippets, credential handling.
- `references/troubleshooting.md` - symptom-to-cause table.

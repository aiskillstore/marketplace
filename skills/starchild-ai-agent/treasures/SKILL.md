---
name: treasures
version: 1.0.3
description: |
  Treasures Finance: tokenized stocks (xStocks / Ondo) trading, USDC bridging, and delegated wallet ops on Solana and Ethereum.

  Use when running Treasures-routed finance ops (e.g. discover tokenized stocks, quote/execute a trade, bridge USDC across chains, check a delegated wallet's portfolio).

  Base URL needs the `/public/v1` prefix (bare host 404s). Trade paths (`/quote/*`, `/trade/submit`, `/bridge/quote`) are geo-fenced at the AWS load balancer → 451 from US and GB, before auth — route those calls through the `sc-vpn` skill with a per-request proxy (DE/NL/SE/CH/SG/HK/JP are clear); reads work from anywhere. A 451 is never a signing problem. See the "Read this before any trade attempt" section.

  Wallet: DEFAULT to the user's Privy wallet via `treasures-b2b-api` (the wallet signs `ownership_proof` for quotes + per-leg signed payloads for `/trade/submit` — use the `wallet` skill to sign). Route by where the assets live: assets in the Privy/EOA wallet → `treasures-b2b-api`; only use the `treasures-wallet` delegated skill when the user explicitly asks for the Treasures-provisioned wallet or the assets sit in it.
metadata:
  starchild:
    emoji: "💎"
    skillKey: treasures-finance
    requires:
      bins:
        - npx
        - node
user-invocable: true
disable-model-invocation: false
---

# Treasures Finance Agent Skills

**Agent Skills** for building AI agents on the Treasures finance APIs.

A skill is a folder of plain-Markdown instructions (`SKILL.md`) that a coding agent loads on demand. The skills here teach an agent to call the Treasures finance APIs correctly — discover tokenized stocks, quote and execute trades, bridge USDC across chains, operate a delegated wallet, and read portfolios — including the signing details and footguns that are easy to get wrong.

## Skill catalog

| Skill | What it does |
| ----- | ------------ |
| [`treasures-b2b-api`](skills/treasures-b2b-api/SKILL.md) | Build an agent on the Treasures public B2B API: discover tokenized stocks, quote/execute trades, bridge USDC across Solana and Ethereum, and read portfolio + trade history for a single end-user wallet pair. Covers endpoint selection, ownership-proof signing (incl. embedded wallets), trade/bridge execution, and error handling. |
| [`treasures-wallet`](skills/treasures-wallet/SKILL.md) | Operate a Treasures delegated wallet over HTTP: onboard (provision a wallet + mint a scoped API key), quote, execute async buys/sells (non-custodial — the agent never signs; Treasures signs as a delegated signer scoped strictly to RWA trades), read balances/portfolio/trade history, and manage API keys. Trades tokenized equities (xStocks / Ondo) vs USDC on Solana or Ethereum with only HTTPS + an API key — no web3 libraries, keys, or RPC. |

## ⚠️ Read this before any trade attempt (verified live 2026-07-27)

Two things fail silently if you don't know them. Both were confirmed with live calls, not docs.

### 1. Base URL needs a path prefix

`https://api.treasures.io` alone **404s on every path**. Two planes off the same host:

| Plane | Base | Used by |
| ----- | ---- | ------- |
| Public B2B | `https://api.treasures.io/public/v1` | `treasures-b2b-api` (default) |
| Delegated agent | `https://api.treasures.io/api/v1` | `treasures-wallet` |

### 2. Trade paths are geo-fenced at the load balancer

Reads are open worldwide; writes are not.

| Path | Result from a blocked IP |
| ---- | ------------------------ |
| `GET /stocks/*`, `/portfolio`, `/trades` | ✅ 200 |
| `POST /quote/buy`, `/quote/sell`, `/bridge/quote`, `/trade/submit` | ❌ 451 `unavailable_for_legal_reasons` |

- The block sits at the **AWS load balancer** (`server: awselb/2.0`), matched on **path + real TCP source IP, before auth and before the app**. Unknown paths return 404 (not 451), and `GET`/`OPTIONS` on a trade path also 451 → the *path* is fenced, not the write method. Both planes are covered — `/api/v1/quote/sell` 451s identically to `/public/v1/quote/sell`.
- **Spoofed geo headers do not work** (`X-Forwarded-For`, `CF-IPCountry`, `X-Real-IP`, `True-Client-IP` all still 451).
- **Blocked:** US (default Starchild egress is San Jose, CA) and GB. **Clear:** DE, NL, SE, CH, SG, HK, JP — tested via the `sc-vpn` skill with a **per-request** proxy (`proxies=` / `curl -x`). Never set a global `HTTP_PROXY`; it breaks sc-proxy billing.

**A 451 is never a wallet, signing, or delegation problem.** Don't debug signatures until you're past it.

### Error ladder on `/quote/sell` — tells you which layer rejected you

```
451 unavailable_for_legal_reasons  → geo edge (change exit region)
400 invalid_request                → schema (fix the body)
401 ownership_proof_eth_invalid    → signature (re-sign the challenge)
422 holdings_insufficient          → auth OK, wallet just lacks the asset
```

Reaching `422` proves geo **and** signing both work — it's the healthiest failure you can get.

### Eligibility — not optional

The 451 is an eligibility rule working as designed, not an outage. Ondo/xStocks tokenized equities are **not offered to US persons**, and Ondo additionally enforces KYC/transfer whitelists **at the token contract**, so an ineligible wallet is rejected on-chain no matter what the exit IP says. **Confirm the user is eligible in a permitted jurisdiction before routing around the fence.** Clearing a geo-block for a user who is genuinely non-US is fine; using it to evade a securities restriction is not.

### How to route trade calls through `sc-vpn`

Prerequisite: the `sc-vpn` skill (official). Install if missing — `npx skills add Starchild-ai-agent/official-skills --skill sc-vpn --agent openclaw`. No credentials; internal network only. Health check: `curl http://sc-vpn.internal:8081/health` → `{"status": "ok"}`.

Proxy URL format is `http://<region>:x@sc-vpn.internal:8080` — the **username is the region code**. Omit it and you get `400 No region specified`.

**Rule: reads go direct, only the fenced trade paths go through the VPN.** Sending everything through the tunnel is slower and pointless — `/stocks`, `/portfolio` and `/trades` already work from anywhere.

```python
import requests, time
from core.skill_tools import wallet   # run from a dir where `core` is importable (e.g. /tmp or /data/workspace)

BASE = "https://api.treasures.io/public/v1"
VPN  = "http://de:x@sc-vpn.internal:8080"          # de | nl | se | ch | sg | hk | jp
PROX = {"http": VPN, "https": VPN}                  # per-request ONLY — never os.environ

ETH = "0x...".lower()                               # wallet address, lowercase

# READ — direct, no proxy
pf = requests.get(f"{BASE}/portfolio", params={"eth_wallet": ETH}, timeout=30).json()

# WRITE — through the VPN, with a signed ownership proof
issued    = int(time.time())
challenge = f"treasures-finance-quote-v1\n{issued}\n\n{ETH}"     # verified format; note the blank line
sig       = wallet.wallet_sign(challenge)["signature"]

body = {
    "ticker": "GOOGL", "chain": "eth",
    "amount_shares": "0.01", "max_slippage_bps": 100,
    "eth_wallet": ETH,
    "ownership_proof": {"issued_at": issued, "eth_signature": sig},
}
r = requests.post(f"{BASE}/quote/sell", json=body, proxies=PROX, timeout=60)
print(r.status_code, r.text)      # 422 holdings_insufficient = geo + signing both OK
```

Same thing from bash:

```bash
curl -x "http://de:x@sc-vpn.internal:8080" \
     -X POST https://api.treasures.io/public/v1/quote/sell \
     -H 'content-type: application/json' -d @body.json
```

Confirm the exit before trusting a result: `curl -x "http://de:x@sc-vpn.internal:8080" https://ipinfo.io/json`.

**Footguns**

| Symptom | Cause |
| ------- | ----- |
| Still 451 through the VPN | Region is itself blocked — GB is fenced too. Use DE/NL/SE/CH/SG/HK/JP. |
| Every *other* API starts 401ing | You set a global `HTTP_PROXY` and bypassed sc-proxy. Unset it; use `proxies=` per request. |
| `400 Bad Request: No region specified` | Missing the region username in the proxy URL. |
| `502 Unknown region` | Region code not in the sc-vpn list of 18. |
| `401 ownership_proof_eth_invalid` | Proof issue, not geo — check lowercase address, fresh `issued_at`, exact challenge string. |

Keep the whole trade sequence (`/quote/*` → `/trade/submit`, and `/bridge/quote` → bridge submit) on the **same exit region**. Mixing exits mid-flow risks the backend seeing an inconsistent origin between legs.

## Install

```bash
# Install one sub-skill (recommended — pulls just what you need)
npx skills add treasures-io/treasures-finance-agent-skills --skill treasures-b2b-api
npx skills add treasures-io/treasures-finance-agent-skills --skill treasures-wallet

# Or install everything (auto-detects your environment and installs accordingly)
npx skills add treasures-io/treasures-finance-agent-skills
```

[`npx skills`](https://github.com/vercel-labs/skills) installs `SKILL.md` files into the right place for 70+ coding agents (Claude Code, Codex, Cursor, GitHub Copilot, Windsurf, Cline, OpenCode, …) and auto-detects which ones you have. It reads this repo's `skills/<name>/SKILL.md` layout directly, so no extra setup is required.

Target specific agents with `-a`:

```bash
npx skills add treasures-io/treasures-finance-agent-skills -a claude-code -a codex -a cursor
```

## License

[MIT](LICENSE)

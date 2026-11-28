# x402socks skill

An [Agent Skill](https://agentskills.io) for agent-first, paid proxy egress
packages from a different source IP or a specific region for targets you are authorized
to access. Clients connect directly to an exit node with a
package-bound proxy token. Tokens can be obtained through
[x402](https://x402.org) payments in USDC on Base or by the documented
[manual checkout](https://x402socks.com/buy).

A token is reusable within the purchased plan, not one-use. Most packages are
short-lived and cheap, so a token is commonly used in a single session or a few
sessions over a few hours. Prefer one token per agent or job to keep agent
memory and context small and avoid cross-contamination between agents; that is
operational hygiene, not only a security precaution. The x402 payment approval
is one-use, but the token it buys is not consumed by a request.

Both SOCKS5 and CONNECT TLS are native transports. Prefer SOCKS5 when the client
supports it, then CONNECT + TLS; use plaintext HTTP CONNECT only when no secure
channel works. Plaintext exposes credentials on the client-to-exit hop, so use a
short-lived token there and prefer a fresh token for another agent or job.
Listener availability is exit-dependent. Target TLS verification stays on. A
proxy-only certificate bypass requires an explicit operator opt-in after the
normal chain fails.

With no package argument, the agent lists current packages and asks which one to
use, then explains the x402 or manual acquisition path. With a package argument,
it does not ask again: with a usable signer it follows the guarded x402 purchase
flow; otherwise it stops with the manual checkout URL. The skill teaches the
agent to quote exact terms, get one-use signed approval for x402 payments, store
the token safely, route traffic through a chosen exit, and verify egress changed.

## Wallet access for agent-side x402 purchases

The agent cannot buy through x402 without a wallet it can sign with. There is no
free tier and no account credit. The manual checkout at
https://x402socks.com/buy is the alternative when the agent has no signer; the
operator completes that transfer and saves the resulting token locally.

1. **An EVM-compatible wallet funded with USDC on Base.** The cheapest package is
   $1.00 for 6 hours / 1 GB. USDC on Base is
   `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`. No ETH is needed for the x402
   purchase because the facilitator submits the EIP-3009 transfer. A manual send
   needs ETH for gas.
2. **A signer the agent can use non-interactively.** Prefer an injected browser
   wallet (EIP-1193), a signer-owned store, or an x402 client signer. No extra
   install is required. A Foundry encrypted keystore, hardware wallet, KMS, or
   HSM is also valid. Do not paste a raw private key into chat or argv.
3. **A Base RPC is optional** for low-volume checks, for example
   `https://mainnet.base.org`, `https://base-rpc.publicnode.com`,
   `https://1rpc.io/base`, or `https://base.drpc.org`.

Never print or output a private key in a terminal, log, chat, or commit. Keep
key material in a signer-owned store or mode `0600` files. See
[`references/wallet.md`](references/wallet.md) for browser and host signer paths.
`cast` recipes there are optional.

### Other requirements

- An Agent Skills client that can run shell commands.
- `curl` and `python3` for the helper. No `cast` requirement.
- Node.js + npm for the TypeScript x402 client, or Python 3.10+ with `uv` for
  the Python client.

No account, email, card, or API key.

## Install

```bash
npx skills add X402Socks/skill
```

Or copy this folder to your client's skills directory:

```bash
cp -r skills/x402socks ~/.claude/skills/       # Claude Code
cp -r skills/x402socks ~/.agents/skills/       # OpenCode and other clients
```

## What is here

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Triggers, wallet requirement, spending rule, buy flow, routing, credential rules. |
| `references/wallet.md` | Browser and host signers, optional `cast` recipes, key handling. |
| `references/payments.md` | x402 v2 flow, approval pinning, guarded clients, recovery. |
| `references/endpoints.md` | Endpoints, client snippets, transport chain, credential handling. |
| `references/troubleshooting.md` | Symptom-to-cause table for 401/402/407/transport errors. |
| `scripts/x402socks.sh` | Helper CLI: quote, status, validate, rotate, recover, test, curl. |
| `scripts/x402socks-browser.mjs` | Allowlisted Playwright runner with transport fallbacks. |
| `assets/purchase-approval.md` | Template for recording the approved terms. |

## Safety defaults

- **Spending:** the skill requires operator-signed approval for an exact term
  set and checks it against the live 402 challenge before signing. The bundled
  pure-Python verifier needs no extra install.
- **Credentials:** the helper reads the token from a `0600` file
  (`~/.config/x402socks/token`) or a signer-owned store. Proxy credentials are
  consumed inside the helper and never reach stdout, argv, logs, URLs, or
  browser storage. Rotation and recovery save the replacement token instead of
  printing it.
- **Origins:** credential-bearing requests only go to pinned `https://`
  x402socks origins with exact ports. Public discovery origins are validated too.
  `X402SOCKS_ALLOW_INSECURE_API=1` is for a trusted loopback test only and is
  separate from the proxy TLS opt-in.
- **Transport:** all traffic goes through the proxy. Prefer SOCKS5, then CONNECT
  + TLS, then plaintext CONNECT only as a last resort. Plaintext exposure calls
  for a short-lived token and a fresh token for the next agent or job; the token
  itself is package-bound and reusable within the plan. The helper clears
  ambient proxy bypass settings, pins HTTPS targets, and disables redirects.
  The browser runner blocks service workers, disables WebRTC, allows every
  request and redirect
  through an exact host and port allowlist, and rechecks the final URL on each
  transport attempt.

## Links

- Repository: https://github.com/X402Socks/skill
- Directory: https://skills.sh/X402Socks/skill
- Service: https://x402socks.com

MIT. Maintained by the x402socks project.

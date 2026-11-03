# x402socks skill

An [Agent Skill](https://agentskills.io) for buying short-lived anonymous
SOCKS5/HTTP egress with USDC on Base through [x402](https://x402.org).

The skill teaches an agent to quote a package, get approval for an exact amount,
complete the x402 v2 payment, store the one-time token safely, route traffic
through a chosen exit, and prove that the egress IP actually changed.

## Requirements

- An Agent Skills client that can run shell commands (Claude Code, Codex,
  Cursor, GitHub Copilot, OpenCode, and others).
- `curl`, plus `python3` for the helper.
- Node.js + npm for the TypeScript x402 client, or Python 3.10+ with `uv` for
  the Python client.
- A wallet with a small USDC balance on Base. The cheapest package is $1 for
  6 hours / 1 GB.

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
| `SKILL.md` | The skill itself: triggers, pricing, spending rule, routing, credential rules. |
| `references/payments.md` | x402 v2 flow, guarded TypeScript/Python clients, recovery. |
| `references/endpoints.md` | Endpoints, client snippets, safe credential handling. |
| `references/troubleshooting.md` | Symptom-to-cause table for 401/402/407/connection errors. |
| `scripts/x402socks.sh` | Helper: health, nodes, quote, status, validate, rotate, test, recover. |
| `assets/purchase-approval.md` | Template for recording the approved amount before spending. |

## Safety defaults

- **Spending:** the skill requires explicit approval for an exact amount and
  enforces it against the live 402 challenge before signing.
- **Credentials:** the helper reads the token from a `0600` file
  (`~/.config/x402socks/token`) and passes it to curl on stdin, so it never
  appears in the process list. Rotation and recovery save the replacement token
  instead of printing it.
- **Transport:** SOCKS5 and plaintext HTTP CONNECT do not encrypt proxy
  authentication. Prefer the TLS CONNECT listener on port 3129 where available.

## Links

- Repository: https://github.com/X402Socks/skill
- Directory: https://skills.sh/X402Socks/skill
- Service: https://x402socks.com

MIT. Maintained by the x402socks project.
